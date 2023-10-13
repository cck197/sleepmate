from datetime import datetime

from dateutil.parser import parse as date_parser
from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import BaseMemory
from mongoengine import ReferenceField

from .helpful_scripts import (
    fix_schema,
    get_date_fields,
    json_dumps,
    mongo_to_json,
    set_attribute,
)
from .structured import get_parsed_output, pydantic_to_mongoengine
from .user import DBUser, get_current_user


class ExerciseEntry_(BaseModel):
    date: datetime = Field(description="date of entry")
    name: str = Field(description="name of exercise")
    notes: str = Field(
        description="feelings before and after the exercise", required=False
    )


date_fields = get_date_fields(ExerciseEntry_)


class ExerciseEntry(ExerciseEntry_):
    @classmethod
    def schema(cls):
        return fix_schema(ExerciseEntry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, _):
        return datetime.now()


DBExerciseEntry = pydantic_to_mongoengine(
    ExerciseEntry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_exercise_entry_from_memory(memory: BaseMemory) -> ExerciseEntry:
    return get_parsed_output("summarise the last exercise", memory, ExerciseEntry)


def save_exercise_entry_to_db(user: DBUser, entry: ExerciseEntry) -> DBExerciseEntry:
    entry = entry.dict()
    # delete any existing entries for this date
    # DBExerciseEntry.objects(user=user, date=entry["date"]).delete()
    # save the new entry
    return DBExerciseEntry(**{"user": user, **entry}).save()


def get_json_exercise_entry(entry: dict) -> str:
    """Returns the exercise entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_exercise_entry(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Saves the exercise entry to the database. Input should be the empty string."""
    entry = get_exercise_entry_from_memory(memory)
    print(f"save_exercise_entry {entry=}")
    save_exercise_entry_to_db(get_current_user(), entry)


@set_attribute("return_direct", False)
def get_last_exercise_entry(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns the last exercise entry."""
    entry = (
        DBExerciseEntry.objects(user=get_current_user()).first().to_mongo().to_dict()
    )
    print(f"get_last_exercise_entry {entry=}")
    return get_json_exercise_entry(entry)


@set_attribute("return_direct", False)
def get_date_exercise_entry(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns the exercise entry for a given date."""
    date = date_parser(utterance)
    db_entry = DBExerciseEntry.objects(user=get_current_user(), date=date).first()
    if db_entry is None:
        return f"No exercise entry found for {date.date()}"
    return get_json_exercise_entry(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def get_exercise_dates(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns the dates of all exercise entries in JSON format.
    Call with exactly one argument."""
    return json_dumps(
        [e.date for e in DBExerciseEntry.objects(user=get_current_user())]
    )


THOUGHT_EDITING_LIMITATIONS = """
Explain changing thoughts in a given direction means taking their content
seriously. You have to notice them and evaluate them to try to change them,
which may strengthen their hold over your mind and wake you up.
"""

EXERCISE_CONFIRMATION = """
Ask if now is a good time to perform the exercise then guide them through one
step at a time. Don't give all the steps at once. Wait for them to complete each
step. When the human completed the exercise, ask how they're feeling. Summarise
with the following fields:

- name of the exercise
- how the human was feeling before and after the exercise.

Finally, after the summary ask the human if they'd like to save the record of
exercise to the database. Only after they've confirmed, save the entry. 
"""

GOALS = [
    {
        "open_focus": """Your goal is to help the human perform the "open focus" exercise."""
        f"{THOUGHT_EDITING_LIMITATIONS}"
        """It is helpful to broaden your focus rather than changing the content of
        your thoughts. Explain that the open focus exercise is a way to do this."""
        f"{EXERCISE_CONFIRMATION}",
    },
    {
        "leaves_on_a_stream": """Your goal is to help the human perform the "leaves on a stream"
        exercise."""
        f"{THOUGHT_EDITING_LIMITATIONS}"
        """Defusion helps us use our minds in a more open, aware, and values-based
        way. It helps us turn off our compulsive problem-solving for a while. It
        opens the door to our power to change, allowing us to acknowledge our
        unhelpful thoughts while charting a course beyond them. Explain that the
        leaves on a stream exercise is a way to do this."""
        f"{EXERCISE_CONFIRMATION}",
    },
    {
        "valued_living": """
        Your goal is to survey the human using the "Valued Living Questionnaire
        (VLQ)". First ask if now is a good time to do the survey. Then guide them
        through the following questions one at a time. Don't give all the questions
        at once.  Wait for them to answer each question. Explain that it's is best
        to plan not to let anyone see this so you can answer as honestly as
        possible, setting aside as best you can social pressures and the wagging
        mental fingers of should and have to. This is between you and you.
        
        1. family relations (other than marriage or parent)
        2. marriage/couples/intimate relations
        3. being a parent
        4. friendships/social relations
        5. work
        6. education/personal growth and development
        7. recreation/leisure
        8. spirituality/religion
        9. citizenship/community life
        10. physical self-care (e.g., exercise, diet, sleep)
        11. environmental issues (e.g., pollution, conservation)
        12. art, creative expression, aesthetics

        For each question, For each domain, ask the human to rate:
        a) The importance of that domain to them.
        b) How consistently they have lived in accordance with their values in that
        domain over the past week.

        Summarise the results in a bullet list and ask if they're correct.

        Explain there are a number of ways to assess the results. The first is to
        look at all domains that have relatively high importance scores (a score of
        9 or 10) and also have relatively low consistency scores (6 or less). These
        are clear problem areas, and I suggest doing your initial values work with
        any one of them. Then you can move on to other areas.

        Also calculate the human's overall score. Multiply the two numbers from the
        first and second parts for each domain. So if for family, in the first part
        you scored it as 10 and in the second part you circled 4, for that domain
        you'd get 40. Add all of those numbers and then divide them by 12 to get
        your composite score. Let the human know that to get a rough sense of how
        their score compares to those of the broad public, the average composite
        result is 61.

        Tell the human that this is a discovery process, not a critique, and after
        all, they've embarked on this journey and they should give themselves some
        credit for that.  They're here to embrace change.
        """,
    },
]

TOOLS = [
    get_date_exercise_entry,
    get_last_exercise_entry,
    save_exercise_entry,
    get_exercise_dates,
]
