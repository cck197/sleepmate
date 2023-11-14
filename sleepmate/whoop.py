import logging
from datetime import date, datetime, time, timedelta
from urllib.parse import urlparse

from authlib.integrations.requests_client import OAuth2Session
from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField
from whoop_client import ApiClient, Configuration, SleepApi, UserApi
from whoop_client.exceptions import UnauthorizedException

from .agent import BaseAgent
from .bmi import DBBodyMeasures
from .config import (
    WHOOP_CLIENT_ID,
    WHOOP_CLIENT_SECRET,
    WHOOP_REDIRECT_URI,
    WHOOP_SCOPE,
)
from .goal import clear_goal_refused, goal_refused
from .helpful_scripts import (
    get_date_fields,
    get_start_end,
    json_dumps,
    parse_date,
    set_attribute,
)
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser, get_user_from_id
from .wearable import DBWearables

parsed_url = urlparse(Configuration().host)
base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
WHOOP_AUTH_URL = f"{base_url}/oauth/oauth2/auth"
WHOOP_TOKEN_URL = f"{base_url}/oauth/oauth2/token"

log = logging.getLogger(__name__)


class WhoopToken(BaseModel):
    state: str = Field(description="state", default=None)
    access_token: str = Field(description="access token", default=None)
    expires_in: int = Field(description="expires in", default=None)
    refresh_token: str = Field(description="refresh token", default=None)
    scope: str = Field(description="scope", default=None)
    token_type: str = Field(description="token type", default=None)
    expires_at: int = Field(description="expires at", default=None)


DBWhoopToken = pydantic_to_mongoengine(
    WhoopToken, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


class WhoopImportEntry_(BaseModel):
    date: datetime = Field(description="date of entry")


date_fields = get_date_fields(WhoopImportEntry_)


# this is just a thin wrapper to record the import
class WhoopImportEntry(WhoopImportEntry_):
    @classmethod
    def schema(cls):
        return fix_schema(WhoopImportEntry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value, default_days=0)


DBWhoopImportEntry = pydantic_to_mongoengine(
    WhoopImportEntry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


class WhoopUser(BaseModel):
    whoop_user_id: int = Field(description="WHOOP user ID")


DBWhoopUser = pydantic_to_mongoengine(
    WhoopUser, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


# this is where the WHOOP sleep data is stored as a JSON string
class WhoopSleep(BaseModel):
    whoop_id: int = Field(description="Unique identifier for the sleep activity")
    whoop_user_id: int = Field(
        description="The WHOOP User who performed the sleep activity"
    )
    # the Pydantic models are all in whoop_client if you care to recreate them
    json_dumps: str = Field(description="JSON representation of the sleep activity")


DBWhoopSleep = pydantic_to_mongoengine(WhoopSleep)


class WhoopSleepDiaryEntry_(BaseModel):
    date: datetime = Field(description="date of entry")
    notes: str = Field(description="any other notes you'd like to add")


date_fields = get_date_fields(WhoopSleepDiaryEntry_)


# this is just a thin wrapper to record the human confirmation
class WhoopSleepDiaryEntry(WhoopSleepDiaryEntry_):
    @classmethod
    def schema(cls):
        return fix_schema(WhoopSleepDiaryEntry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value, default_days=1)


DBWhoopSleepDiaryEntry = pydantic_to_mongoengine(
    WhoopSleepDiaryEntry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def clear_whoop_data(db_user_id: str) -> None:
    """Clears all WHOOP data for the given user."""
    DBWhoopToken.objects(user=db_user_id).delete()
    db_entry = DBWhoopUser.objects(user=db_user_id).first()
    if db_entry is not None:
        DBWhoopSleep.objects(whoop_user_id=db_entry.whoop_user_id).delete()
        db_entry.delete()
    [clear_goal_refused(db_user_id, goal) for goal in GOAL_HANDLERS[0].keys()]
    DBWhoopSleepDiaryEntry.objects(user=db_user_id).delete()
    DBWhoopImportEntry.objects(user=db_user_id).delete()


def update_user_from_whoop(db_user_id: str) -> DBUser:
    api_instance = UserApi(get_whoop_api_client(db_user_id))
    api_response = api_instance.get_profile_basic()
    db_entry = DBWhoopUser.objects(whoop_user_id=api_response.user_id).first()
    if db_entry is None:
        DBWhoopUser(user=db_user_id, whoop_user_id=api_response.user_id).save()
    db_user = get_user_from_id(db_user_id)
    db_user.update(
        **{
            "name": f"{api_response.first_name} {api_response.last_name}",
            "email": api_response.email,
        }
    )
    return db_user


def whoop_exception_handler(func):
    """Decorator to handle WHOOP exceptions and return an OAuth2 URL."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UnauthorizedException as e:
            log.error(e)
            return get_whoop_auth_url_(args[0])

    return wrapper


def import_whoop_sleep(db_user_id: str) -> list[DBWhoopSleep]:
    """Imports sleep data from WHOOP."""
    api_instance = SleepApi(get_whoop_api_client(db_user_id))
    api_response = api_instance.get_sleep_collection()
    results = []
    for sleep in api_response.records:
        db_entry = DBWhoopSleep.objects(whoop_id=sleep.id).first()
        if db_entry is not None:
            db_entry.delete()
        results.append(
            DBWhoopSleep(
                whoop_id=sleep.id,
                whoop_user_id=sleep.user_id,
                json_dumps=json_dumps(sleep.model_dump()),
            )
        )
    return results


def get_whoop_token(**kwargs) -> DBWhoopToken:
    """Returns the WHOOP token by given kwargs."""
    db_token = DBWhoopToken.objects(**kwargs).order_by("-id").first()
    if db_token:
        return db_token
    return DBWhoopToken(**kwargs).save()


def get_whoop_oauth2_session():
    assert WHOOP_CLIENT_ID, "WHOOP_CLIENT_ID is required"
    assert WHOOP_CLIENT_SECRET, "WHOOP_CLIENT_SECRET is required"
    assert WHOOP_REDIRECT_URI, "WHOOP_REDIRECT_URI is required"
    return OAuth2Session(
        WHOOP_CLIENT_ID,
        WHOOP_CLIENT_SECRET,
        scope=WHOOP_SCOPE,
        redirect_uri=WHOOP_REDIRECT_URI,
        token_endpoint_auth_method="client_secret_post",
    )


def get_whoop_auth_url_(db_user_id: str) -> str:
    authorization_url, state = get_whoop_oauth2_session().create_authorization_url(
        WHOOP_AUTH_URL
    )
    db_token = get_whoop_token(user=db_user_id)
    db_token.state = state
    db_token.save()
    return authorization_url


@set_attribute("return_direct", False)
def get_whoop_auth_url(x: BaseAgent, utterance: str):
    """Use this to get a link to the WHOOP OAuth2 authorization page."""
    return get_whoop_auth_url_(x.db_user_id)


@whoop_exception_handler
def import_whoop_sleep_data_(db_user_id: str) -> str:
    db_entries = import_whoop_sleep(db_user_id)
    log.info(f"import_whoop_sleep_data: {len(db_entries)=}")
    [db_entry.save() for db_entry in db_entries]
    return "Success!"


@set_attribute("return_direct", False)
def import_whoop_sleep_data(x: BaseAgent, utterance: str) -> str:
    """Use this to import sleep data from WHOOP."""
    return import_whoop_sleep_data_(x.db_user_id)


@whoop_exception_handler
def import_whoop_user_data_(db_user_id: str) -> str:
    db_user = update_user_from_whoop(db_user_id)
    log.info(f"import_whoop_user_data: {db_user.to_mongo()=}")
    db_user.save()
    db_entry = get_whoop_body_measures(db_user_id)
    log.info(f"import_whoop_user_data: {db_entry.to_mongo()=}")
    db_entry.save()
    DBWhoopImportEntry(user=db_user_id, date=datetime.now()).save()
    return "Success!"


@set_attribute("return_direct", False)
def import_whoop_user_data(x: BaseAgent, utterance: str) -> str:
    """Use this to import user data from WHOOP."""
    return import_whoop_user_data_(x.db_user_id)


@set_attribute("return_direct", False)
def get_whoop_sleep_data(x: BaseAgent, utterance: str) -> str:
    """Use this to retrieve WHOOP sleep data from the local database."""
    db_entry = DBWhoopUser.objects(user=x.db_user_id).first()
    if db_entry is None:
        return "No WHOOP user ID found."
    db_entry = (
        DBWhoopSleep.objects(whoop_user_id=db_entry.whoop_user_id)
        .order_by("id")
        .first()
    )
    if db_entry is None:
        return "No sleep data found."
    log.info(f"get_whoop_sleep_data: {db_entry.to_mongo()=}")
    return db_entry.json_dumps


def get_whoop_api_client(db_user_id: str):
    db_token = get_whoop_token(user=db_user_id)
    if not db_token.access_token:
        return None
    return ApiClient(Configuration(access_token=db_token.access_token))


def get_whoop_body_measures(db_user_id: str) -> DBBodyMeasures:
    api_response = UserApi(get_whoop_api_client(db_user_id)).get_body_measurement()
    return DBBodyMeasures(
        **{
            "user": db_user_id,
            "date": datetime.now(),
            "height": api_response.height_meter,
            "weight": api_response.weight_kilogram,
        }
    )


def get_whoop_sleep_diary_entry_from_memory(x: BaseAgent) -> WhoopSleepDiaryEntry:
    return get_parsed_output(
        "summarise the last WHOOP sleep diary entry",
        x.get_latest_messages,
        WhoopSleepDiaryEntry,
    )


def save_whoop_sleep_diary_entry_to_db(
    db_user_id: str, entry: WhoopSleepDiaryEntry
) -> DBWhoopSleepDiaryEntry:
    entry = entry.dict()
    # delete any existing entries for this date
    (start, end) = get_start_end(entry["date"])
    DBWhoopSleepDiaryEntry.objects(
        user=db_user_id, date__gte=start, date__lte=end
    ).delete()
    # save the new entry
    return DBWhoopSleepDiaryEntry(**{"user": db_user_id, **entry}).save()


@set_attribute("return_direct", False)
def save_whoop_sleep_diary_entry(x: BaseAgent, utterance: str):
    """Use this once the WHOOP sleep data has been summarised and the human has
    confirmed their correctness. Saves the WHOOP sleep diary entry to the
    database."""
    entry = get_whoop_sleep_diary_entry_from_memory(x)
    if entry is None:
        return
    log.info(f"save_whoop_sleep_diary_entry {entry=}")
    save_whoop_sleep_diary_entry_to_db(x.db_user_id, entry)


def whoop_import(db_user_id: str) -> bool:
    if goal_refused(db_user_id, "whoop_import"):
        return False

    return DBWhoopImportEntry.objects(user=db_user_id).count() == 0


def whoop_sleep(db_user_id: str) -> bool:
    if goal_refused(db_user_id, "whoop_sleep"):
        return False

    if DBWearables.objects(user=db_user_id, whoop=True).count() == 0:
        return False

    end = datetime.combine(date.today(), time())
    start = end - timedelta(days=1)

    return DBWhoopSleepDiaryEntry.objects(user=db_user_id, date__gte=start).count() == 0


GOAL_HANDLERS = [
    {
        "whoop_import": whoop_import,
        "whoop_sleep": whoop_sleep,
    },
]

NO_SKIPPING = "Follow the steps below one at a time. Do not skip any steps."

GOALS = [
    {
        "whoop_import": f"""
        Your goal is to ask the human if they'd like to import their data from
        WHOOP. {NO_SKIPPING}
        
        Steps:
        - Confirm now is a good time.
        - Generate a link to the WHOOP login page by calling
        `get_whoop_auth_url` and ask the human to click it and log in. Tell them
        to close the browser tab and come back here once they've logged in.  
        - Call `import_whoop_user_data` to import the user data from WHOOP.
        - Confirm the import was successful.
        """,
        "whoop_sleep": f"""
        Your goal is to summarise the human's WHOOP sleep data and save a record
        to the database. {NO_SKIPPING}
        
        Steps:
        - Ask if now is a good time to review their WHOOP sleep data.
        - Call `import_whoop_sleep_data` to import the data from WHOOP.
        - Call `get_whoop_sleep_data` to retrieve the sleep data.
        - Summarise the data as a bullet list. Be sure to include the date and
        sleep efficiency.
        - Ask are any other notes you'd like to add.
        - Important! Finish by calling `save_whoop_diary_entry` to save the
        WHOOP diary entry to the database.
        """,
    }
]

TOOLS = [
    get_whoop_auth_url,
    import_whoop_user_data,
    import_whoop_sleep_data,
    get_whoop_sleep_data,
    save_whoop_sleep_diary_entry,
]
