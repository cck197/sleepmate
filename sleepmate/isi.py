from datetime import datetime

from dateutil.parser import parse as date_parser
from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import BaseMemory
from mongoengine import ReferenceField

from .helpful_scripts import fix_schema, get_date_fields, json_dumps, set_attribute
from .structured import get_parsed_output, pydantic_to_mongoengine
from .user import DBUser, get_current_user


class ISIEntry_(BaseModel):
    date: datetime = Field(description="date of entry")
    difficulty_falling_asleep: int = Field(description="difficulty falling asleep")
    difficulty_staying_asleep: int = Field(description="difficulty staying asleep")
    problems_waking_up_too_early: int = Field(
        description="problems waking up too early"
    )
    sleep_pattern_satisfaction: int = Field(description="sleep pattern satisfaction")
    sleep_problem_noticeability: int = Field(description="sleep problem noticeability")
    sleep_problem_worry: int = Field(description="sleep problem worry")
    sleep_problem_interference: int = Field(description="sleep problem interference")


date_fields = get_date_fields(ISIEntry_)


class ISIEntry(ISIEntry_):
    @classmethod
    def schema(cls):
        return fix_schema(ISIEntry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return date_parser(value)


DBISIEntry = pydantic_to_mongoengine(
    ISIEntry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_isi_entry_from_memory(memory: BaseMemory) -> ISIEntry:
    return get_parsed_output(
        "summarise the last Insomnia Severity Index entry", memory, ISIEntry
    )


def save_isi_entry_to_db(user: DBUser, entry: ISIEntry) -> DBISIEntry:
    # delete any existing entries for this date
    entry = entry.dict()
    DBISIEntry.objects(user=user, date=entry["date"]).delete()
    # save the new entry
    return DBISIEntry(**{"user": user, **entry}).save()


def get_json_isi_entry(entry: dict) -> str:
    """Returns the Insomnia Severity Index entry in JSON format."""
    for k in ("_id", "user"):
        entry.pop(k, None)
    return json_dumps(entry)


@set_attribute("return_direct", False)
def save_isi_entry(memory: ReadOnlySharedMemory, *_, **__):
    """Saves the Insomnia Severity Index entry to the database. Takes any number of
    arguments but only uses memory. Assumes the entry is already in memory."""
    entry = get_isi_entry_from_memory(memory)
    print(f"save_isi_entry {entry=}")
    save_isi_entry_to_db(get_current_user(), entry)


@set_attribute("return_direct", False)
def get_last_isi_entry(memory: ReadOnlySharedMemory, *_, **__):
    """Returns the last Insomnia Severity Index entry."""
    entry = DBISIEntry.objects(user=get_current_user()).first().to_mongo().to_dict()
    print(f"get_last_isi_entry {entry=}")
    return get_json_isi_entry(entry)


@set_attribute("return_direct", False)
def get_date_isi_entry(memory: ReadOnlySharedMemory, goal: str, utterance: str, **__):
    """Returns the Insomnia Severity Index entry for a given date."""
    date = date_parser(utterance)
    db_entry = DBISIEntry.objects(user=get_current_user(), date=date).first()
    if db_entry is None:
        return f"No sleep ISI found for {date.date()}"
    return get_json_isi_entry(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def get_date_isi_diary_entry(
    memory: ReadOnlySharedMemory, _: str, utterance: str, **__
):
    """Returns the Insomnia Severity Index entry for a given date."""
    date = date_parser(utterance)
    db_entry = DBISIEntry.objects(user=get_current_user(), date=date).first()
    if db_entry is None:
        return f"No ISI entry found for {date.date()}"
    return get_json_isi_entry(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def get_isi_dates(memory: ReadOnlySharedMemory, goal: str, utterance: str, **__):
    """Returns the dates of all Insomnia Severity Index entries in JSON format.
    Call with exactly one argument."""
    return json_dumps([e.date for e in DBISIEntry.objects(user=get_current_user())])


GOALS = [
    {
        "insomnia_severity_index": """
        Your goal is to survey the human for their Insomnia Severity Index (ISI)
        using the standard 7-item questionnaire, but don't ask until you've
        asked an open question, and the human has confirmed the accuracy of at
        least one listening statement. Ask if now would be a good time then the
        following questions:
        
        0. Date of entry (get today's date and make that the default)
        1. Difficulty falling asleep.
        2. Difficulty staying asleep.
        3. Problems waking up too early.
        4. How satisfied/dissatisfied are you with your current sleep pattern?
        5. How noticeable to others do you think your sleep problem is in terms
           of impairing the quality of your life?
        6. How worried/distressed are you about your current sleep problem?
        7. To what extent do you consider your sleep problem to interfere with
        your daily functioning (e.g., daytime fatigue, ability to function at
        work/daily chores, concentration, memory, mood, etc.)?
        
        Be sure to ask the questions with their corresponding labels as shown
        below.
        
        Questions 1-3 are rated on a 5-point scale from 0 to 4:
        0: None
        1: Mild
        2: Moderate
        3: Severe
        4: Very severe

        Question 4 is rated on a 5-point scale from 0 to 4:
        0: Very satisfied
        1: Satisfied
        2: Moderately satisfied
        3: Dissatisfied
        4: Very dissatisfied

        Questions 5-7 are rated on a 5-point scale from 0 to 4:
        0: Not at all
        1: A little bit
        2: Moderately
        3: Quite a bit
        4: Very much

        When you've got the answer to all seven questions, summarise including
        the date and ask if they're correct.
        
        Add them up and report the total, which should be
        between 0 and 28. Add the following interpretation:
        0-7: No clinically significant insomnia
        8-14: Subthreshold insomnia
        15-21: Clinical insomnia (moderate severity)
        22-28: Clinical insomnia (severe)
        """
    },
]

TOOLS = [
    get_last_isi_entry,
    get_date_isi_diary_entry,
    get_isi_dates,
    save_isi_entry,
]
