import logging
from datetime import date, datetime, time, timedelta

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import (
    get_date_fields,
    get_start_end,
    json_dumps,
    mongo_to_json,
    parse_date,
    set_attribute,
)
from .mi import get_completion, get_template
from .prompt import get_template
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser
from .wearable import user_integrated_supported_wearable

log = logging.getLogger(__name__)


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


def get_sleep_diary_entry_from_memory(x: BaseAgent) -> SleepDiaryEntry:
    return get_parsed_output(
        "summarise the last sleep diary entry", x.get_latest_messages, SleepDiaryEntry
    )


def calculate_sleep_efficiency(entry: dict) -> None:
    try:
        total_asleep = (
            entry["final_wake_up"] - entry["tried_to_fall_asleep"]
        ).total_seconds() / 60
        total_asleep -= entry["time_to_fall_asleep"]
        total_asleep -= entry["time_awake"]

        total_in_bed = (entry["out_of_bed"] - entry["in_bed"]).total_seconds() / 60

        entry["sleep_duration"] = total_asleep
        entry["sleep_efficiency"] = (total_asleep / total_in_bed) * 100
    except ZeroDivisionError:
        log.exception("ZeroDivisionError in calculate_sleep_efficiency")


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
    db_user_id: str, entry: SleepDiaryEntry
) -> DBSleepDiaryEntry:
    entry = adjust_to_baseline_date(entry.dict())
    # delete any existing entries for this date
    (start, end) = get_start_end(entry["date"])
    DBSleepDiaryEntry.objects(user=db_user_id, date__gte=start, date__lte=end).delete()
    # save the new entry
    return DBSleepDiaryEntry(**{"user": db_user_id, **entry}).save()


def get_json_diary_entry(entry: dict) -> str:
    """Returns the sleep diary entry in JSON format with sleep duration and
    efficiency calculated."""
    calculate_sleep_efficiency(entry)
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_sleep_diary_entry(x: BaseAgent, utterance: str):
    """Use this once all the sleep diary questions have been answered and the
    human has confirmed their correctness. Saves the diary entry to the
    database."""
    entry = get_sleep_diary_entry_from_memory(x)
    if entry is None:
        return
    log.info(f"save_sleep_diary_entry {entry=}")
    save_sleep_diary_entry_to_db(x.db_user_id, entry)


@set_attribute("return_direct", False)
def get_sleep_diary_dates(x: BaseAgent, utterance: str):
    """Returns the dates of all sleep diary entries in JSON format."""
    return json_dumps(
        [e.date for e in DBSleepDiaryEntry.objects(user=x.db_user_id).order_by("-id")]
    )


@set_attribute("return_direct", False)
def get_last_sleep_diary_entry(x: BaseAgent, utterance: str):
    """Returns the last sleep diary entry."""
    db_entry = DBSleepDiaryEntry.objects(user=x.db_user_id).order_by("-id").first()
    if db_entry is None:
        return "No sleep diary entries found"
    entry = db_entry.to_mongo().to_dict()
    log.info(f"get_last_sleep_diary_entry {entry=}")
    return get_json_diary_entry(entry)


@set_attribute("return_direct", False)
def get_date_sleep_diary_entry(x: BaseAgent, utterance: str):
    """Returns the sleep diary entry for a given date. Use this when the human
    asks what their sleep efficiency is."""
    date = parse_date(utterance, default_days=1)
    (start, end) = get_start_end(date)
    db_entry = (
        DBSleepDiaryEntry.objects(user=x.db_user_id, date__gte=start, date__lte=end)
        .order_by("-id")
        .first()
    )
    if db_entry is None:
        return f"No sleep diary entry found for {date.date()}"
    return get_json_diary_entry(db_entry.to_mongo().to_dict())


def diary_entry(db_user_id: str):
    """Returns True if it's time to ask the human to record a sleep diary
    entry."""
    if goal_refused(db_user_id, "diary_entry"):
        return False

    # don't ask if the user has integrated a supported wearable device
    if user_integrated_supported_wearable(db_user_id):
        return False

    end = datetime.combine(date.today(), time())
    start = end - timedelta(days=1)

    return DBSleepDiaryEntry.objects(user=db_user_id, date__gte=start).count() == 0


GOAL_HANDLERS = [
    {
        "diary_entry": diary_entry,
    },
]

SLEEP_EFFICIENCY = """
Very important! Include sleep sleep duration in hours and minutes and efficiency
as a percentage.

Sleep efficiency is the percentage of time spent asleep while in bed. To give
the human a rough sense of how their sleep efficiency compares, tell them
anything over 85%% is considered normal.
"""

GOALS = [
    {
        "diary_entry_retrieval": f"""
        Your goal is to summarise a sleep diary entry for a given date as a
        bullet list. Convert ISO 8601 strings to a human readable format.  After
        the list, {SLEEP_EFFICIENCY}
        """,
    },
    {
        "diary_entry": f"""
        Your goal is to record a sleep diary entry for a given night. Guide the
        human through the following steps one at a time.  Don't give all the
        questions at once. Wait for them to answer each question.
        
        - Ask if now is a good time to record a sleep diary entry
        - Get the date for yesterday by calling get_date(1)
        - Time you went to bed yesterday (print the full date)
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
        - Summarise their answers in a bullet list and ask if they're correct
        
        Only once the human has confirmed correctness, save the diary entry to
        the database.
        
        Finally, retrieve the entry from the database and
        summarise.  {SLEEP_EFFICIENCY}
    """,
    },
]


def get_sleep_diary_description(x: BaseAgent, utterance: str) -> str:
    """Use this when the human asks what a sleep diary is. They're asking about
    the Consensus Sleep Diary so describe that."""
    return get_completion(
        x.ro_memory,
        utterance,
        get_template(x, get_sleep_diary_description.__doc__),
    )


TOOLS = [
    get_sleep_diary_description,
    get_last_sleep_diary_entry,
    get_date_sleep_diary_entry,
    get_sleep_diary_dates,
    save_sleep_diary_entry,
]
