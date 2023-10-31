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


class StopBang_(BaseModel):
    date: datetime = Field(description="date of entry")
    snoring: bool = Field(description="snores loudly")
    tired: bool = Field(description="tired during the day")
    observed: bool = Field(description="observed to stop breathing")
    pressure: bool = Field(description="high blood pressure")
    neck: float = Field(description="neck circumference")
    score: int = Field(description="STOP-Bang score")


date_fields = get_date_fields(StopBang_)


class StopBang(StopBang_):
    @classmethod
    def schema(cls):
        return fix_schema(StopBang_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return datetime.now()


DBStopBang = pydantic_to_mongoengine(
    StopBang, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_stop_bang_from_memory(x: BaseAgent) -> StopBang:
    return get_parsed_output(
        "summarise the answers the human gave for the STOP-Bang Questionnaire",
        x.get_latest_messages,
        StopBang,
    )


def save_stop_bang_to_db(db_user_id: str, entry: StopBang) -> DBStopBang:
    entry = entry.dict()
    # delete any existing entries for this date
    (start, end) = get_start_end(entry["date"])
    DBStopBang.objects(user=db_user_id, date__gte=start, date__lte=end).delete()
    # save the new entry
    return DBStopBang(**{"user": db_user_id, **entry}).save()


def get_json_stop_bang(entry: dict) -> str:
    """Returns the StopBang entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_stop_bang(x: BaseAgent, utterance: str):
    """Saves the StopBang to the database."""
    entry = get_stop_bang_from_memory(x)
    print(f"{entry=}")
    if entry is not None:
        log.info(f"save_stop_bang {entry=}")
        save_stop_bang_to_db(x.db_user_id, entry)


@set_attribute("return_direct", False)
def get_last_stop_bang(x: BaseAgent, utterance: str):
    """Returns the last StopBang entry."""
    entry = DBStopBang.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No StopBang found"
    entry = entry.to_mongo().to_dict()
    log.info(f"get_last_stop_bang {entry=}")
    return get_json_stop_bang(entry)


def stop_bang(db_user_id: str):
    """Returns True if StopBang should be collected."""
    if goal_refused(db_user_id, "stop_bang"):
        return False
    return DBStopBang.objects(user=db_user_id).count() == 0


GOAL_HANDLERS = [
    {
        "stop_bang": stop_bang,
    },
]

GOALS = [
    {
        "stop_bang": """
        Your goal is to complete the STOP-Bang Questionnaire.
        
        Low risk of OSA (Obstructive Sleep Apnoea): 0-2 points
        Intermediate risk of OSA: 3-4 points
        High risk of OSA: 5-8 points
            or Yes to 2 or more of 4 STOP questions + male
            or Yes to 2 or more of 4 STOP questions + BMI > 35 kg/m2
            or Yes to 2 or more of 4 STOP questions + neck circumference
            (17”/43cm in male, 16”/41cm in female)

        Steps:
        - Ask if now is a good time to complete the STOP-Bang Questionnaire.
        - Get the Health History database entry
        - Calculate the age in years
        - Calculate the BMI
        - Summarise the sex, age, height, weight, medical conditions and BMI
        - Ask the following questions:
            - (S) Do you snore loudly (louder than talking or loud enough to be heard
            through closed doors)?
            - (T) Do you often feel tired, fatigued, or sleepy during daytime?
            - (O) Has anyone observed you stop breathing during your sleep?
        - Summarise from the Health History and BMI:
            - (P) High blood pressure if hypertension or high blood pressure in
            medical_conditions
            - (B) BMI > 35 kg/m2
            - (A) Calculated age > 50 years (think step by step)
        - Ask:
            - (N) What is your neck circumference (convert to cm if necessary)?
        - Summarise from the Health History:
            - (G) Gender male
        - Calculate the STOP-Bang score (think step by step)
        - Summarise the STOP-Bang entry in order
        - Explain the risk
        - Important! Save the StopBang entry to the database
        """,
    },
]

TOOLS = [get_last_stop_bang, save_stop_bang]
