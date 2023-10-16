from datetime import datetime, timedelta

from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import BaseMemory
from mongoengine import ReferenceField

from .helpful_scripts import (
    get_date_fields,
    json_dumps,
    mongo_to_json,
    parse_date,
    set_attribute,
)
from .mi import get_completion, get_template
from .structured import (
    create_from_positional_args,
    fix_schema,
    get_parsed_output,
    pydantic_to_mongoengine,
)
from .user import DBUser, get_current_user

model_name = "gpt-4"


class SleepDiaryEntry_(BaseModel):
    date: datetime = Field(description="date of entry")
    in_bed: datetime = Field(description="time you went to bed")
    tried_to_fall_asleep: datetime = Field(description="time you tried to fall asleep")
    time_to_fall_asleep: int = Field(description="how long it took you to fall asleep")
    times_awake: int = Field(description="how many times you woke up during the night")
    time_awake: int = Field(description="total time you were awake during the night")
    final_wake_up: datetime = Field(description="final wake up time")
    out_of_bed: datetime = Field(description="time you got out of bed")
    sleep_quality: str = Field(description="sleep quality")
    medications: str = Field(
        description="medications or aids you used to help you sleep"
    )
    notes: str = Field(description="any other notes you'd like to add")


date_fields = get_date_fields(SleepDiaryEntry_)


class SleepDiaryEntry(SleepDiaryEntry_):
    @classmethod
    def schema(cls):
        return fix_schema(SleepDiaryEntry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value, default_days=1)


def get_sleep_diary_entry_from_memory(memory: BaseMemory) -> SleepDiaryEntry:
    return get_parsed_output(
        "summarise the last sleep diary entry", memory, SleepDiaryEntry
    )


def calculate_sleep_efficiency(entry: dict) -> None:
    total_asleep = (
        entry["final_wake_up"] - entry["tried_to_fall_asleep"]
    ).total_seconds() / 60
    total_asleep -= entry["time_to_fall_asleep"]
    total_asleep -= entry["time_awake"]

    total_in_bed = (entry["out_of_bed"] - entry["in_bed"]).total_seconds() / 60

    entry["sleep_duration"] = total_asleep
    entry["sleep_efficiency"] = (total_asleep / total_in_bed) * 100


def adjust_to_baseline_date(sleep_data: dict) -> dict:
    """Adjust datetimes to a baseline date."""
    baseline_date = sleep_data[date_fields[0]]

    for index, key in enumerate(date_fields[1:]):
        time_component = sleep_data[key].time()
        adjusted_datetime = datetime.combine(baseline_date.date(), time_component)
        if index == 0:
            baseline_date = adjusted_datetime
        elif adjusted_datetime < baseline_date:
            adjusted_datetime += timedelta(days=1)

        sleep_data[key] = adjusted_datetime

    return sleep_data


DBSleepDiaryEntry = pydantic_to_mongoengine(
    SleepDiaryEntry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def save_sleep_diary_entry_to_db(
    user: DBUser, entry: SleepDiaryEntry
) -> DBSleepDiaryEntry:
    entry = adjust_to_baseline_date(entry.dict())
    # delete any existing entries for this date
    DBSleepDiaryEntry.objects(user=user, date=entry["date"]).delete()
    # save the new entry
    return DBSleepDiaryEntry(**{"user": user, **entry}).save()


def get_json_diary_entry(entry: dict) -> str:
    """Returns the sleep diary entry in JSON format with sleep duration and
    efficiency calculated."""
    calculate_sleep_efficiency(entry)
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_sleep_diary_entry(memory: ReadOnlySharedMemory, goal: str, text: str):
    """Saves the exercise entry to the database. Important: call with exactly
    one string argument."""
    entry = create_from_positional_args(SleepDiaryEntry, text)
    if entry is None:
        entry = get_sleep_diary_entry_from_memory(memory)
    print(f"save_sleep_diary_entry {entry=}")
    save_sleep_diary_entry_to_db(get_current_user(), entry)


@set_attribute("return_direct", False)
def get_sleep_diary_dates(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns the dates of all sleep diary entries in JSON format. Call with
    exactly one string argument."""
    return json_dumps(
        [e.date for e in DBSleepDiaryEntry.objects(user=get_current_user())]
    )


@set_attribute("return_direct", False)
def get_last_sleep_diary_entry(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns the last sleep diary entry."""
    db_entry = DBSleepDiaryEntry.objects(user=get_current_user()).first()
    if db_entry is None:
        return "No sleep diary entries found"
    entry = db_entry.to_mongo().to_dict()
    print(f"get_last_sleep_diary_entry {entry=}")
    return get_json_diary_entry(entry)


@set_attribute("return_direct", False)
def get_date_sleep_diary_entry(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns the sleep diary entry for a given date."""
    date = parse_date(utterance)
    db_entry = DBSleepDiaryEntry.objects(user=get_current_user(), date=date).first()
    if db_entry is None:
        return f"No sleep diary entry found for {date.date()}"
    return get_json_diary_entry(db_entry.to_mongo().to_dict())


SLEEP_EFFICIENCY = """
Include sleep sleep duration in hours and minutes and efficiency as a
percentage.

Sleep efficiency is the percentage of time spent asleep while in bed. To give
the human a rough sense of how their sleep efficiency compares, tell them
anything over 85%% is considered normal.
"""

GOALS = [
    {
        "diary_probe": """
        Your goal is find out if the human has ever kept a sleep diary, but
        don't ask until they've confirmed the accuracy of at least one listening
        statement. If they haven't kept a sleep diary, ask if they'd like the AI
        to help them keep one. If they have, ask if they'd like to share it with
        the AI.
        """,
    },
    {
        "diary_entry_retrieval": f"""
        Your goal is to summarise a sleep diary entry for a given date as a
        bullet list. Convert ISO 8601 strings to a human readable format.  After
        the list, {SLEEP_EFFICIENCY}
        """,
    },
    {
        "diary_entry": f"""
        Your goal is to record a sleep diary entry for a given night. First ask
        if now is a good time to record a diary entry.  Then guide them through
        the following questions one at a time.  Don't give all the questions at
        once.  Wait for them to answer each question.
        
        - Date of entry (default to yesterday's date)
        - Time you went to bed 
        - Time you tried to fall asleep
        - How long it took you to fall asleep (in minutes)
        - How many times you woke up during the night (number)
          - If zero then skip the next question, the answer is zero
        - Total time you were awake during the night (in minutes)
        - Final wake up time
        - Time you got out of bed
        - Sleep quality, one of the following: "very good", "good", "okay",
           "bad", "very bad"
        - Any medications or aids you used to help you sleep
        - Any other notes you'd like to add
        
        Once you have all the answers to the above, STOP! Summarise the results
        in a bullet list and ask if they're correct.

        Important: don't save the entry until the human has confirmed! Then save
        the diary entry to the database.
        
        Finally, retrieve the entry from the database and
        summarise.  {SLEEP_EFFICIENCY}
    """,
    },
]


def get_sleep_diary_description(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this when the human asks what a sleep diary is. Summarise the
    numbered list of questions only. Call with exactly one string argument."""
    return get_completion(
        memory,
        utterance,
        get_template(
            goal,
            get_sleep_diary_description.__doc__
            + GOALS[0]["diary_probe"]
            + "End by asking if they'd like the AI to help them keep a sleep diary.",
        ),
        model_name,
    )


TOOLS = [
    get_sleep_diary_description,
    get_last_sleep_diary_entry,
    get_date_sleep_diary_entry,
    get_sleep_diary_dates,
    save_sleep_diary_entry,
]
