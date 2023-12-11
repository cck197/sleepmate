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
    parse_date,
    set_attribute,
    timedelta_in_years,
)
from .structured import (
    fix_schema,
    get_document_summary,
    get_parsed_output,
    pydantic_to_mongoengine,
)
from .user import DBUser

log = logging.getLogger(__name__)


class HealthHistory_(BaseModel):
    date: datetime = Field(description="date of entry")
    sex: str = Field(description="biological sex")
    date_of_birth: datetime = Field(description="date of birth")
    occupation: str = Field(description="current occupation")
    work_hours: str = Field(description="typical work hours")
    smoking: str = Field(description="smoking status")
    alcohol: str = Field(description="alcohol consumption")
    physical_activity: str = Field(description="physical activity level")
    diet: str = Field(description="typical diet")
    medical_conditions: str = Field(description="existing medical conditions")
    medications: str = Field(description="current medications")
    supplements: str = Field(description="current supplements")
    family_history: str = Field(description="family history of sleep disorders")
    mental_health: str = Field(description="history of mental health conditions")
    psychological_treatment: str = Field(description="current psychological treatment")
    living_with: str = Field(description="living with")
    residence_type: str = Field(description="type of residence")
    noise_level: str = Field(description="noise level in the living area")
    goal: str = Field(description="what does success look like?")
    helpful: str = Field(description="what have you tried previously that helped?")
    unhelpful: str = Field(
        description="what have you tried previously that didn't help?"
    )
    notes: str = Field(description="any other notes you'd like to add")


date_fields = get_date_fields(HealthHistory_)


class HealthHistory(HealthHistory_):
    @classmethod
    def schema(cls):
        return fix_schema(HealthHistory_, date_fields)

    @validator("date", pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value)

    @validator("date_of_birth", pre=True)
    def validate_dob(cls, value):
        date_of_birth = parse_date(value)
        current_date = datetime.now()
        # manually adjust the year if it is in the future
        if date_of_birth.year > current_date.year:
            date_of_birth = date_of_birth.replace(year=date_of_birth.year - 100)
        return date_of_birth


DBHealthHistory = pydantic_to_mongoengine(
    HealthHistory, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_health_history_from_memory(x: BaseAgent) -> HealthHistory:
    return get_parsed_output(
        "summarise the answers the human gave for their health history",
        x.get_latest_messages,
        HealthHistory,
    )


def save_health_history_to_db(db_user_id: str, entry: HealthHistory) -> DBHealthHistory:
    entry = entry.dict()
    # delete any existing entries for this date
    (start, end) = get_start_end(entry["date"])
    DBHealthHistory.objects(user=db_user_id, date__gte=start, date__lte=end).delete()
    # save the new entry
    return DBHealthHistory(**{"user": db_user_id, **entry}).save()


def get_json_health_history(entry: dict) -> str:
    """Returns the Health History entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def calculate_age_in_years(x: BaseAgent, utterance: str):
    """Call this when you need to calculate the age from the date of birth."""
    entry = DBHealthHistory.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No Health History found"
    return timedelta_in_years(datetime.now() - entry.date_of_birth)


@set_attribute("return_direct", False)
def save_health_history(x: BaseAgent, utterance: str):
    """Saves the Health History to the database."""
    entry = get_health_history_from_memory(x)
    print(f"{entry=}")
    if entry is not None:
        log.info(f"save_health_history {entry=}")
        save_health_history_to_db(x.db_user_id, entry)


@set_attribute("return_direct", False)
def get_last_health_history(x: BaseAgent, utterance: str):
    """Returns the last Health History entry."""
    entry = DBHealthHistory.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No Health History found"
    entry = entry.to_mongo().to_dict()
    log.info(f"get_last_health_history {entry=}")
    return get_json_health_history(entry)


@set_attribute("return_direct", False)
def get_is_male(x: BaseAgent, utterance: str):
    entry = DBHealthHistory.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No Health History found"
    sex = entry.sex.lower()
    return "male" in sex or "man" in sex


@set_attribute("return_direct", False)
def get_is_hypertensive(x: BaseAgent, utterance: str):
    """Use this to determine if the human is hypertensive."""
    db_entry = DBHealthHistory.objects(user=x.db_user_id).order_by("-id").first()
    if db_entry is None:
        return "No Health History found"
    summary = get_document_summary("hypertension or high blood pressure", db_entry)
    log.info(f"{summary=}")
    return summary.found


def health_history(db_user_id: str):
    """Returns True if a Health History should happen."""
    if goal_refused(db_user_id, "health_history"):
        return False
    return DBHealthHistory.objects(user=db_user_id).count() == 0


GOAL_HANDLERS = [
    {
        "health_history": health_history,
    },
]

GOALS = [
    {
        "health_history": """
        Your goal is to survey the human for their Health History using the 19
        point questionnaire below, but don't ask until you've asked an open
        question, and the human has confirmed the accuracy of at least one
        listening statement. Ask if now would be a good time then the following
        questions. Ask one question at a time. There's no need to confirm the
        answers until the end.
        
        0. Date of entry (default to today's date)
        1. Sex
        2. Date of birth
        3. Current Occupation
        4. Typical work hours
        5. Smoking
        6. Alcohol
        7. Physical Activity Level
        8. What does a typical day of eating look like?
        9. Any existing medical conditions (diabetes, hypertension, etc.)
        10. List of current medications
        11. List of current nutritional supplements
        12. Family history of insomnia or other sleep disorders
        13. History of mental health conditions (depression, anxiety, etc.)
        14. Any current psychological treatment
        15. Living with (Alone, Family, Friends)
        16. Type of residence (House, Apartment, etc.)
        17. Noise Level in the living area
        18. When it comes to sleep, what does success look like?
        19. What have you tried previously that helped?
        20. What have you tried previously that didn't help?
        21. Anything else you'd like to add?

        Once you have ALL the answers to the above, save the Health History to
        the database. Retrieve the last Health History entry from the database
        and summarise it to the human.
        """
    }
]

TOOLS = [
    get_last_health_history,
    save_health_history,
    calculate_age_in_years,
    get_is_hypertensive,
]
