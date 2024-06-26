import logging
from datetime import datetime, timedelta
from functools import partial
from typing import Tuple

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import (
    get_confirmation_str,
    get_date_fields,
    json_dumps,
    mongo_to_json,
    parse_date,
    set_attribute,
)
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)

######################################################################
# Exercise Entry - a record of an exercise session
######################################################################


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


def get_exercise_entry_from_memory(x: BaseAgent) -> ExerciseEntry:
    return get_parsed_output(
        "summarise the last exercise", x.get_latest_messages, ExerciseEntry
    )


def save_exercise_entry_to_db(user: str, entry: ExerciseEntry) -> DBExerciseEntry:
    entry = entry.dict()
    # delete any existing entries for this date
    # DBExerciseEntry.objects(user=user, date=entry["date"]).delete()
    # save the new entry
    return DBExerciseEntry(**{"user": user, **entry}).save()


def get_json_exercise_entry(entry: dict) -> str:
    """Returns the exercise entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_exercise_entry(x: BaseAgent, utterance: str):
    """Use this to save the exercise entry to the database."""
    entry = get_exercise_entry_from_memory(x)
    if entry is not None:
        log.info(f"save_exercise_entry {entry=}")
        save_exercise_entry_to_db(x.db_user_id, entry)


@set_attribute("return_direct", False)
def get_last_exercise_entry(x: BaseAgent, utterance: str):
    """Returns the last exercise entry."""
    entry = DBExerciseEntry.objects(user=x.db_user_id).order_by("-id").first()
    if entry is None:
        return "No exercise entries found"
    entry = entry.to_mongo().to_dict()
    log.info(f"get_last_exercise_entry {entry=}")
    return get_json_exercise_entry(entry)


@set_attribute("return_direct", False)
def get_date_exercise_entry(x: BaseAgent, utterance: str):
    """Returns the exercise entry for a given date."""
    date = parse_date(utterance)
    db_entry = DBExerciseEntry.objects(user=x.db_user_id, date=date).first()
    if db_entry is None:
        return f"No exercise entry found for {date.date()}"
    return get_json_exercise_entry(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def get_exercise_dates(x: BaseAgent, utterance: str):
    """Returns the dates of all exercise entries in JSON format."""
    return json_dumps([e.date for e in DBExerciseEntry.objects(user=x.db_user_id)])


######################################################################
# VLQ - Valued Living Questionnaire
######################################################################


class VLQEntry_(BaseModel):
    date: datetime = Field(description="date of entry")
    family_relations: Tuple[int, int] = Field(description="family relations")
    marriage: Tuple[int, int] = Field(description="marriage/couples/intimate relations")
    parenting: Tuple[int, int] = Field(description="being a parent")
    friendships: Tuple[int, int] = Field(description="friendships/social relations")
    work: Tuple[int, int] = Field(description="work")
    education: Tuple[int, int] = Field(
        description="education/personal growth and development"
    )
    recreation: Tuple[int, int] = Field(description="recreation/leisure")
    spirituality: Tuple[int, int] = Field(description="spirituality/religion")
    citizenship: Tuple[int, int] = Field(description="citizenship/community life")
    physical_self_care: Tuple[int, int] = Field(
        description="physical self-care (e.g., exercise, diet, sleep)"
    )
    environmental_issues: Tuple[int, int] = Field(
        description="environmental issues (e.g., pollution, conservation)"
    )
    art: Tuple[int, int] = Field(description="art, creative expression, aesthetics")


date_fields = get_date_fields(VLQEntry_)


class VLQEntry(VLQEntry_):
    @classmethod
    def schema(cls):
        return fix_schema(VLQEntry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, _):
        return datetime.now()


DBVLQEntry = pydantic_to_mongoengine(
    VLQEntry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_vlq_entry_from_memory(x: BaseAgent) -> VLQEntry:
    return get_parsed_output("summarise the VLQ", x.get_latest_messages, VLQEntry)


def save_vlq_entry_to_db(user: str, entry: VLQEntry) -> DBVLQEntry:
    return DBVLQEntry(**{"user": user, **entry.dict()}).save()


def get_json_vlq_entry(entry: dict) -> str:
    """Returns the VLQ entry in JSON format"""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_vlq_entry(x: BaseAgent, utterance: str):
    """Saves VLQ entry to the database. Call *only* after all the VLQ questions
    have been answered."""
    entry = get_vlq_entry_from_memory(x)
    log.info(f"save_vlq_entry {entry=}")
    if entry is not None:
        save_vlq_entry_to_db(x.db_user_id, entry)


def get_current_vlq_entry(db_user_id: str) -> DBVLQEntry:
    """Returns current VLQ entry."""
    return DBVLQEntry.objects(user=db_user_id).order_by("-id").first()


@set_attribute("return_direct", False)
def get_vlq_entry(x: BaseAgent, utterance: str):
    """Returns VLQ entry from the database."""
    entry = get_current_vlq_entry(x.db_user_id)
    log.info(f"get_vlq_entry {entry=}")
    if entry is not None:
        return get_json_vlq_entry(entry.to_mongo().to_dict())


THOUGHT_EDITING_LIMITATIONS = """
Explain changing thoughts in a given direction means taking their content
seriously. You have to notice them and evaluate them to try to change them,
which may strengthen their hold over your mind and wake you up.
"""

EXERCISE_CONFIRMATION = f"""
Steps (go slow, don't skip any steps):
-  Ask if now is a good time to perform the exercise. Note the irony of using a
digital device for this purpose, mentioning that this system has built-in
obsolescence.
- Guide them through the exercise one step at a time.  Don't give all
the steps at once. Wait for them to complete each step.
- When the human completed the exercise, ask how they're feeling.
- Summarise with the following fields:
- Name of the exercise
- How the human was feeling before and after the exercise
- Confirm the summary is correct.
- Save the exercise entry to the database by calling the function
`save_exercise_entry`.
"""


def exercise_time(name: str, db_user_id: str) -> bool:
    start = datetime.now() - timedelta(days=5)
    return (
        not goal_refused(db_user_id, name)
        and DBExerciseEntry.objects(
            name__icontains=name.replace("_", " "),
            user=db_user_id,
            date__gte=start,
        ).count()
        == 0
    )


def valued_living(db_user_id: str) -> bool:
    start = datetime.now() - timedelta(days=7)

    return not goal_refused(db_user_id, "valued_living") and (
        DBVLQEntry.objects(user=db_user_id, date__gte=start).count() == 0
    )


GOAL_HANDLERS = [
    {
        "open_focus": partial(exercise_time, "open_focus"),
        "leaves_on_a_stream": partial(exercise_time, "leaves_on_a_stream"),
        "valued_living": valued_living,
    },
]

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
        
        Only after they've confirmed, save the VLQ diary entry to the database.
        """,
    },
]

TOOLS = [
    get_date_exercise_entry,
    get_last_exercise_entry,
    save_exercise_entry,
    get_exercise_dates,
    get_vlq_entry,
    save_vlq_entry,
]
