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


class BMI_(BaseModel):
    date: datetime = Field(description="date of entry")
    height: float = Field(description="height in metres")
    weight: float = Field(description="weight in kilograms")


date_fields = get_date_fields(BMI_)


class BMI(BMI_):
    @classmethod
    def schema(cls):
        return fix_schema(BMI_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return datetime.now()


DBBMI = pydantic_to_mongoengine(
    BMI, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_bmi_from_memory(x: BaseAgent) -> BMI:
    return get_parsed_output(
        "summarise the answers the human gave for their height and weight",
        x.get_latest_messages,
        BMI,
    )


def save_bmi_to_db(db_user_id: str, entry: BMI) -> DBBMI:
    entry = entry.dict()
    # delete any existing entries for this date
    (start, end) = get_start_end(entry["date"])
    DBBMI.objects(user=db_user_id, date__gte=start, date__lte=end).delete()
    # save the new entry
    return DBBMI(**{"user": db_user_id, **entry}).save()


def get_json_bmi(entry: dict) -> str:
    """Returns the BMI entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_bmi(x: BaseAgent, utterance: str):
    """Saves the BMI to the database."""
    entry = get_bmi_from_memory(x)
    print(f"{entry=}")
    if entry is not None:
        log.info(f"save_bmi {entry=}")
        save_bmi_to_db(x.db_user_id, entry)


@set_attribute("return_direct", False)
def calculate_bmi(x: BaseAgent, utterance: str):
    """Use this to calculate the BMI."""
    entry = DBBMI.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No BMI found"
    return entry.weight / (entry.height * entry.height)


@set_attribute("return_direct", False)
def get_last_bmi(x: BaseAgent, utterance: str):
    """Returns the last BMI entry."""
    entry = DBBMI.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No BMI found"
    entry = entry.to_mongo().to_dict()
    log.info(f"get_last_bmi {entry=}")
    return get_json_bmi(entry)


def bmi(db_user_id: str):
    """Returns True if BMI should be collected."""
    if goal_refused(db_user_id, "bmi"):
        return False
    return DBBMI.objects(user=db_user_id).count() == 0


GOAL_HANDLERS = [
    {
        "bmi": bmi,
    },
]

GOALS = [
    {
        "bmi": """
        Your goal is to calculate the human's BMI. Ask the following questions:
        - What is your height?
        - What is your weight?

        Steps:
        - Convert the height to metres
        - Convert the weight to kilograms
        - Calculate the BMI using the formula: weight / (height * height)
        - Save the BMI to the database
        - Return the BMI to the human (normal BMI is between 20 and 25)
        """
    },
]

TOOLS = [get_last_bmi, save_bmi, calculate_bmi]
