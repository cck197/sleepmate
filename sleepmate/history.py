from datetime import datetime

from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import BaseMemory
from mongoengine import ReferenceField

from .goal import goal_refused
from .helpful_scripts import (
    Goal,
    get_date_fields,
    get_start_end,
    mongo_to_json,
    parse_date,
    set_attribute,
)
from .structured import (
    create_from_positional_args,
    fix_schema,
    get_parsed_output,
    pydantic_to_mongoengine,
)
from .user import DBUser


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

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value)


DBHealthHistory = pydantic_to_mongoengine(
    HealthHistory, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_health_history_from_memory(memory: BaseMemory) -> HealthHistory:
    return get_parsed_output("summarise the last Health History", memory, HealthHistory)


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
def save_health_history(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Saves the Health History to the database *only* after all the questions
    have been answered."""
    entry = create_from_positional_args(HealthHistory, utterance)
    if entry is None:
        entry = get_health_history_from_memory(memory)
    if entry is not None:
        print(f"save_health_history {entry=}")
        save_health_history_to_db(db_user_id, entry)


@set_attribute("return_direct", False)
def get_last_health_history(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Returns the last Health History entry."""
    entry = DBHealthHistory.objects(user=db_user_id).order_by("-id").first()
    if entry is None:
        return "No Health History found"
    entry = entry.to_mongo().to_dict()
    print(f"get_last_health_history {entry=}")
    return get_json_health_history(entry)


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
        3. Sex
        4. Date of birth
        5. Current Occupation
        6. Typical work hours
        7. Smoking
        8. Alcohol
        9. Physical Activity Level
        10. What does a typical day of eating look like?
        9. Any existing medical conditions (diabetes, hypertension, etc.)
        10. List of current medications
        11. Family history of insomnia or other sleep disorders
        12. History of mental health conditions (depression, anxiety, etc.)
        13. Any current psychological treatment
        14. Living with (Alone, Family, Friends)
        15. Type of residence (House, Apartment, etc.)
        16. Noise Level in the living area
        17. What does success look like?
        18. What have you tried previously that helped?
        19. What have you tried previously that didn't help?
        20. Anything else you'd like to add?

        Once you have ALL the answers to the above, STOP! Summarise the results
        in a bullet list and ask if they're correct.

        Important: don't save the entry until the human has confirmed! Then save
        the Health History to the database.
        """
    }
]

TOOLS = [get_last_health_history, save_health_history]
