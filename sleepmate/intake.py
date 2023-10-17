from datetime import datetime

from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import BaseMemory
from mongoengine import ReferenceField

from .helpful_scripts import get_date_fields, mongo_to_json, parse_date, set_attribute
from .structured import (
    create_from_positional_args,
    fix_schema,
    get_parsed_output,
    pydantic_to_mongoengine,
)
from .user import DBUser, get_current_user


class Intake_(BaseModel):
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


date_fields = get_date_fields(Intake_)


class Intake(Intake_):
    @classmethod
    def schema(cls):
        return fix_schema(Intake_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value)


DBIntake = pydantic_to_mongoengine(
    Intake, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_intake_from_memory(memory: BaseMemory) -> Intake:
    return get_parsed_output("summarise the last intake", memory, Intake)


def save_intake_to_db(user: DBUser, entry: Intake) -> DBIntake:
    entry = entry.dict()
    # delete any existing entries for this date
    DBIntake.objects(user=user, date=entry["date"]).delete()
    # save the new entry
    return DBIntake(**{"user": user, **entry}).save()


def get_json_intake(entry: dict) -> str:
    """Returns the intake entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_intake(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Saves the intake to the database. Important: call with exactly one string
    argument."""
    entry = create_from_positional_args(Intake, utterance)
    if entry is None:
        entry = get_intake_from_memory(memory)
    print(f"save_intake {entry=}")
    save_intake_to_db(get_current_user(), entry)


@set_attribute("return_direct", False)
def get_last_intake(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns the last intake entry."""
    entry = DBIntake.objects(user=get_current_user()).first().to_mongo().to_dict()
    print(f"get_last_intake {entry=}")
    return get_json_intake(entry)


GOALS = [
    {
        "intake": """
        Your goal is to collect the following information. Walk the human
        through step by step. Don't ask more than one question at a time.
        
        Basic Information:
        - Sex
        - Date of birth

        Occupation and Work Schedule:
        - Current Occupation
        - Typical work hours

        Lifestyle Factors:
        - Smoking (Yes/No)
        - Alcohol (Yes/No)
        - Physical Activity Level
        - What does a typical day of eating look like?

        Medical History:
        - Any existing medical conditions (diabetes, hypertension, etc.)
        - List of current medications
        - Family history of insomnia or other sleep disorders

        Psychological Factors:
        - History of mental health conditions (depression, anxiety, etc.)
        - Any current psychological treatment

        Living Conditions:
        - Living with (Alone, Family, Friends)
        - Type of residence (House, Apartment, etc.)
        - Noise Level in the living area

        Goals:
        - What does success look like?
        - What have you tried previously that helped?
        - What have you tried previously that didn't help?

        Notes:
        - Anything else you'd like to add?

        Once you have all the answers to the above, STOP! Summarise the results
        in a bullet list and ask if they're correct.

        Important: don't save the entry until the human has confirmed! Then save
        the intake to the database.
        """
    }
]

TOOLS = [get_last_intake, save_intake]
