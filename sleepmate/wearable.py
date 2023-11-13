import logging

from langchain.pydantic_v1 import BaseModel, Field
from mongoengine import ReferenceField

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import mongo_to_json, set_attribute
from .structured import get_parsed_output, pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)


class Wearables(BaseModel):
    whoop: bool = Field(description="WHOOP Strap")
    fitbit: bool = Field(description="Fitbit Devices")
    apple_watch: bool = Field(description="Apple Watch")
    garmin: bool = Field(description="Garmin Wearables")
    samsung: bool = Field(description="Samsung Galaxy Watch")
    oura: bool = Field(description="Oura Ring")
    xiaomi: bool = Field(description="Xiaomi Mi Band")
    polar: bool = Field(description="Polar Watches")
    withings: bool = Field(description="Withings Sleep Tracking Mat")
    amazfit: bool = Field(description="Amazfit Smartwatches")
    other: str = Field(description="Other (specify)", default=None)


DBWearables = pydantic_to_mongoengine(
    Wearables, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_json_wearables(entry: dict) -> str:
    """Returns the wearables record in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def get_wearables(x: BaseAgent, utterance: str):
    """Returns wearables record."""
    db_entry = DBWearables.objects(user=x.db_user_id).first()
    if db_entry is None:
        return f"No record of wearables for {x.db_user_id}."
    return get_json_wearables(db_entry.to_mongo().to_dict())


def get_wearables_from_memory(x: BaseAgent) -> Wearables:
    return get_parsed_output(
        "summarise the wearables", x.get_latest_messages, Wearables
    )


def save_wearables_to_db(user: str, entry: Wearables) -> DBWearables:
    entry = entry.dict()
    # delete any existing entry
    DBWearables.objects(user=user).delete()
    # save the new entry
    return DBWearables(**{"user": user, **entry}).save()


@set_attribute("return_direct", False)
def save_wearables(x: BaseAgent, utterance: str):
    """Use this to save the wearables record to the database."""
    entry = get_wearables_from_memory(x)
    if entry is not None:
        log.info(f"save_wearables {entry=}")
        save_wearables_to_db(x.db_user_id, entry)


def wearable_probe(db_user_id: str) -> bool:
    return not goal_refused(db_user_id, "wearable_probe") and (
        DBWearables.objects(user=db_user_id).count() == 0
    )


GOAL_HANDLERS = [
    {
        "wearable_probe": wearable_probe,
    },
]

GOALS = [
    {
        "wearable_probe": """
        Your goal is to ask the human if they have any wearable device they'd
        like to integrate. Once integrated, we can pull objective data rather
        than ask subjective questions. Make a bullet list of these devices and
        Ask the human if they have any of them:
        
        - WHOOP Strap
        - Fitbit Devices (e.g., Fitbit Charge, Fitbit Versa, Fitbit Sense)
        - Apple Watch
        - Garmin Wearables (e.g., Garmin Vivosmart, Garmin Fenix)
        - Samsung Galaxy Watch
        - Oura Ring
        - Xiaomi Mi Band
        - Polar Watches (e.g., Polar Vantage, Polar Ignite)
        - Withings Sleep Tracking Mat
        - Amazfit Smartwatches
        - Other (specify)

        Once the humans has confirmed what devices they have, save a record of
        the wearables to the database.
        """,
    }
]

TOOLS = [
    get_wearables,
    save_wearables,
]
