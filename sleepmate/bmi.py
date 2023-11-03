import logging
from datetime import datetime

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import (
    get_date_fields,
    get_start_end,
    mongo_to_json,
    set_attribute,
)
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)


class BodyMeasures_(BaseModel):
    date: datetime = Field(description="date of entry")
    height: float = Field(description="height in metres")
    weight: float = Field(description="weight in kilograms")


date_fields = get_date_fields(BodyMeasures_)


class BodyMeasures(BodyMeasures_):
    @classmethod
    def schema(cls):
        return fix_schema(BodyMeasures_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return datetime.now()


DBBodyMeasures = pydantic_to_mongoengine(
    BodyMeasures, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_body_measures_from_memory(x: BaseAgent) -> BodyMeasures:
    return get_parsed_output(
        "summarise the answers the human gave for their body measures",
        x.get_latest_messages,
        BodyMeasures,
    )


def save_body_measures_to_db(db_user_id: str, entry: BodyMeasures) -> DBBodyMeasures:
    entry = entry.dict()
    # delete any existing entries for this date
    (start, end) = get_start_end(entry["date"])
    DBBodyMeasures.objects(user=db_user_id, date__gte=start, date__lte=end).delete()
    # save the new entry
    return DBBodyMeasures(**{"user": db_user_id, **entry}).save()


def get_json_body_measures(entry: dict) -> str:
    """Returns the BodyMeasures entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_body_measures(x: BaseAgent, utterance: str):
    """Saves the BodyMeasures to the database."""
    entry = get_body_measures_from_memory(x)
    print(f"{entry=}")
    if entry is not None:
        log.info(f"save_body_measures {entry=}")
        save_body_measures_to_db(x.db_user_id, entry)


@set_attribute("return_direct", False)
def calculate_bmi(x: BaseAgent, utterance: str):
    """Use this to calculate the BMI."""
    entry = DBBodyMeasures.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No BodyMeasures found"
    return entry.weight / (entry.height * entry.height)


@set_attribute("return_direct", False)
def get_last_body_measures(x: BaseAgent, utterance: str):
    """Returns the last BodyMeasures entry."""
    entry = DBBodyMeasures.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No BodyMeasures found"
    entry = entry.to_mongo().to_dict()
    log.info(f"get_last_body_measures {entry=}")
    return get_json_body_measures(entry)


def bmi(db_user_id: str):
    """Returns True if BodyMeasures should be collected."""
    if goal_refused(db_user_id, "bmi"):
        return False
    return DBBodyMeasures.objects(user=db_user_id).count() == 0


GOAL_HANDLERS = [
    {
        "bmi": bmi,
    },
]

GOALS = [
    {
        "bmi": """
        Your goal is to collect the human's body measures.
        Ask the following questions:
        - What is your height?
        - What is your weight?

        Steps:
        - Convert the height to metres
        - Convert the weight to kilograms
        - Save the BodyMeasures to the database
        - Calculate the BMI using the formula: weight / (height * height)
        - Return the BMI to the human (normal BodyMeasures is between 20 and 25)
        """
    },
]

TOOLS = [get_last_body_measures, save_body_measures, calculate_bmi]
