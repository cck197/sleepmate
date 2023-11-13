import logging
from datetime import datetime
from urllib.parse import urlparse

from authlib.integrations.requests_client import OAuth2Session
from langchain.pydantic_v1 import BaseModel, Field
from mongoengine import ReferenceField
from whoop_client import ApiClient, Configuration, SleepApi, UserApi

from .agent import BaseAgent
from .bmi import DBBodyMeasures
from .config import (
    WHOOP_CLIENT_ID,
    WHOOP_CLIENT_SECRET,
    WHOOP_REDIRECT_URI,
    WHOOP_SCOPE,
)
from .goal import goal_refused
from .helpful_scripts import json_dumps, set_attribute
from .structured import pydantic_to_mongoengine
from .user import DBUser, get_user_from_id
from .wearable import DBWearables

parsed_url = urlparse(Configuration().host)
base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
WHOOP_AUTH_URL = f"{base_url}/oauth/oauth2/auth"
WHOOP_TOKEN_URL = f"{base_url}/oauth/oauth2/token"

log = logging.getLogger(__name__)


class WhoopToken(BaseModel):
    state: str = Field(description="state")
    access_token: str = Field(description="access token", default=None)
    expires_in: int = Field(description="expires in", default=None)
    refresh_token: str = Field(description="refresh token", default=None)
    scope: str = Field(description="scope", default=None)
    token_type: str = Field(description="token type", default=None)
    expires_at: int = Field(description="expires at", default=None)


DBWhoopToken = pydantic_to_mongoengine(
    WhoopToken, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


class WhoopUser(BaseModel):
    whoop_user_id: int = Field(description="WHOOP user ID")


DBWhoopUser = pydantic_to_mongoengine(
    WhoopUser, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


class WhoopSleep(BaseModel):
    whoop_id: int = Field(description="Unique identifier for the sleep activity")
    whoop_user_id: int = Field(
        description="The WHOOP User who performed the sleep activity"
    )
    # the Pydantic models are all in whoop_client if you care to recreate them
    json_dumps: str = Field(description="JSON representation of the sleep activity")


DBWhoopSleep = pydantic_to_mongoengine(WhoopSleep)


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


def import_whoop_sleep(db_user_id: str):
    """Imports sleep data from WHOOP."""
    api_instance = SleepApi(get_whoop_api_client(db_user_id))
    api_response = api_instance.get_sleep_collection()
    for sleep in api_response.records:
        db_entry = DBWhoopSleep.objects(whoop_id=sleep.id).first()
        if db_entry is not None:
            db_entry.delete()
        db_entry = DBWhoopSleep(
            whoop_id=sleep.id,
            whoop_user_id=sleep.user_id,
            json_dumps=json_dumps(sleep.model_dump()),
        )
        log.info(f"import_whoop_sleep: {db_entry.to_mongo()=}")
        db_entry.save()


def get_whoop_token(**kwargs) -> DBWhoopToken:
    """Returns the WHOOP token by given kwargs."""
    db_token = DBWhoopToken.objects(**kwargs).order_by("-id").first()
    if db_token:
        return db_token
    return DBWhoopToken(**kwargs)


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


@set_attribute("return_direct", False)
def get_whoop_auth_url(x: BaseAgent, utterance: str):
    """Use this to get a link to the WHOOP OAuth2 authorization page."""
    authorization_url, state = get_whoop_oauth2_session().create_authorization_url(
        WHOOP_AUTH_URL
    )
    db_token = get_whoop_token(user=x.db_user_id)
    db_token.state = state
    db_token.save()
    return authorization_url


@set_attribute("return_direct", False)
def import_whoop_data(x: BaseAgent, utterance: str):
    """Use this to import data from WHOOP."""
    db_user = update_user_from_whoop(x.db_user_id)
    log.info(f"import_whoop_data: {db_user.to_mongo()=}")
    db_user.save()
    db_entry = get_whoop_body_measures(x.db_user_id)
    log.info(f"import_whoop_data: {db_entry.to_mongo()=}")
    db_entry.save()


@set_attribute("return_direct", False)
def get_whoop_sleep_data(x: BaseAgent, utterance: str):
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


def whoop(db_user_id: str) -> bool:
    return not goal_refused(db_user_id, "whoop") and (
        DBWearables.objects(user=db_user_id, whoop=True).count() == 0
    )


GOAL_HANDLERS = [
    {
        "whoop": whoop,
        "whoop_sleep": lambda _: True,
    },
]

GOALS = [
    {
        "whoop": """
        Your goal is to ask the human if they'd like to import their data from
        WHOOP.
        
        Steps:
        - Confirm now is a good time.
        - Generate a link to the WHOOP OAuth2 authorization page and ask the
        human to click it and log in. Tell them they can close the browser
        tab once they've logged in.
        - Import the data from WHOOP.
        - Confirm the import was successful.
        """,
        "whoop_sleep": """
        Summarise WHOOP sleep data. There's no need to import the data from
        WHOOP. 
        
        Steps:
        - Call `get_whoop_sleep_data` to retrieve the data.
        - Summarise the data and display it as bullet list. Be sure to include
        the date and sleep efficiency.
        """,
    }
]

TOOLS = [get_whoop_auth_url, import_whoop_data, get_whoop_sleep_data]
