import logging
from datetime import datetime

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .agent import BaseAgent
from .bmi import calculate_bmi
from .goal import goal_refused
from .helpful_scripts import (
    get_date_fields,
    get_start_end,
    mongo_to_json,
    set_attribute,
)
from .history import calculate_age_in_years, get_is_hypertensive, get_is_male
from .sleep50 import get_last_sleep50_entry_from_db, sum_category
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)


class StopBang_(BaseModel):
    date: datetime = Field(description="date of entry")
    snoring: bool = Field(description="snores loudly")
    tired: bool = Field(description="tired during the day")
    observed: bool = Field(description="observed to stop breathing")
    neck: float = Field(description="neck circumference")


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
    log.info(f"{entry=}")
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
    # get the results of the SLEEP-50 questionnaire
    db_entry = get_last_sleep50_entry_from_db(db_user_id)
    if db_entry is None:
        return False
    # check the apnea questions
    (n, total) = sum_category(db_entry, "sleep_apnea")
    if n == total:
        return False  # no problem here
    if goal_refused(db_user_id, "stop_bang"):
        return False
    return DBStopBang.objects(user=db_user_id).count() == 0


@set_attribute("return_direct", False)
def calculate_stop_bang(x: BaseAgent, utterance: str):
    """Use this to calculate the STOP-Bang score."""
    stop_bang = DBStopBang.objects(user=x.db_user_id).order_by("-id").first()
    if stop_bang is None:
        return "No StopBang found"
    male = get_is_male(x, "")
    bmi = calculate_bmi(x, "")
    age = calculate_age_in_years(x, "")
    hypertension = get_is_hypertensive(x, "")
    score = 0
    log.info(
        f"{stop_bang.to_mongo().to_dict()=}, {male=}, {bmi=}, {age=}, {hypertension=}"
    )
    if stop_bang.snoring:
        score += 1
    if stop_bang.tired:
        score += 1
    if stop_bang.observed:
        score += 1
    if hypertension:
        score += 1
    if bmi > 35:
        score += 1
    if age > 50:
        score += 1
    if stop_bang.neck > 40:
        score += 1
    if male:
        score += 1
    return score


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
        - Get the Health History database entry by calling `get_last_health_history`
        - Get the height and weight by calling `get_last_body_measures`
        - Calculate the age in years by calling `calculate_age_in_years`
        - Calculate the BMI by calling `calculate_bmi`
        - Summarise the sex, age, height, weight, medical conditions and BMI
        - Ask the following questions:
            - (S) Do you snore loudly (louder than talking or loud enough to be heard
            through closed doors)? (+1 point)
            - (T) Do you often feel tired, fatigued, or sleepy during daytime?
            - (O) Has anyone observed you stop breathing during your sleep? (+1 point)
        - Summarise from the Health History and BMI:
            - (P) High blood pressure if hypertension or high blood pressure in
            medical_conditions (+1 point)
            - (B) BMI > 35 kg/m2 (+1 point)
            - (A) Calculated age > 50 years (think step by step) (+1 point)
        - Ask:
            - (N) What is your neck circumference (convert to cm if necessary)?
        - Summarise from the Health History:
            - (G) Gender male (+1 point)
        - Important! Save the StopBang entry to the database
        - Calculate the STOP-Bang score by calling `calculate_stop_bang`
        - Summarise the STOP-Bang entry in order
        - Explain the risk
        """,
    },
]

TOOLS = [get_last_stop_bang, save_stop_bang, calculate_stop_bang]
