from datetime import datetime

from dateutil.parser import parse as date_parser
from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field, validator
from langchain.schema import BaseMemory
from mongoengine import ReferenceField

from .mi import get_completion, get_template
from .structured import get_parsed_output, pydantic_to_mongoengine
from .user import DBUser


class SleepDiaryEntry_(BaseModel):
    quality: str = Field(description="sleep quality")
    in_bed: datetime = Field(description="time you went to bed")
    tried_to_fall_asleep: str = Field(description="time you tried to fall asleep")
    time_to_fall_asleep: str = Field(description="time it took you to fall asleep")
    times_woke_up: str = Field(
        description="number of times you woke up during the night"
    )
    time_awake: str = Field(description="total time you were awake during the night")
    final_wake_up: str = Field(description="final wake up time")
    out_of_bed: str = Field(description="time you got out of bed")
    medications: str = Field(description="medications or aids used")
    notes: str = Field(description="any other notes you'd like to add")


date_fields = ["in_bed"]


class SleepDiaryEntry(SleepDiaryEntry_):
    @classmethod
    def schema(cls):
        s = SleepDiaryEntry_.schema()
        for key in date_fields:
            try:
                del s["properties"][key]["format"]
            except KeyError:
                pass
        return s

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return date_parser(value)


DBSleepDiaryEntry = pydantic_to_mongoengine(
    SleepDiaryEntry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_sleep_diary_entry(memory: BaseMemory) -> SleepDiaryEntry:
    return get_parsed_output(
        "summarise the last sleep diary entry", memory, SleepDiaryEntry
    )


model_name = "gpt-4"

SLEEP_EFFICIENCY = """
Include sleep efficiency as a percentage. Sleep efficiency is the percentage of
time spent asleep while in bed.

To give the human a rough sense of how their sleep efficiency compares, tell
them anything over 85%% is considered normal.
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
        Your goal is to summarise the JSON object to display a sleep diary entry
        for a given date. Convert ISO 8601 strings to a human readable format.
        {SLEEP_EFFICIENCY}
        """,
    },
    {
        "diary_entry": f"""
        Your goal is to record a sleep diary entry for a given night. First ask
        if now is a good time to record a diary entry. Then guide them through
        the following questions one at a time. Don't give all the questions at
        once.  Wait for them to answer each question. If they've recorded a
        diary entry previously, suggest using the same answer for the new entry.
        
        1. Date of the night you're recording (suggest yesterday's date)
        2. Sleep quality, one of the following: "very good", "good", "okay",
        "bad", "very bad"
        3. Time you went to bed
        4. Time you tried to fall asleep
        5. How long it took you to fall asleep
        6. How many times you woke up during the night
        7. Total time you were awake during the night
        8. Final wake up time
        9. Time you got out of bed
        10. Any medications or aids you used to help you sleep
        11. Any other notes you'd like to add

        End with a summary of the data you've collected and asking if it's
        correct. {SLEEP_EFFICIENCY}
    """,
    },
]


def get_sleep_diary_description(
    memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
) -> str:
    """Use this when the human asks what a sleep diary is. Summarise the
    numbered list of questions only:"""
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


# def get_sleep_diary_entry(
#     memory: ReadOnlySharedMemory, goal: str, utterance: str, model_name=model_name
# ) -> str:
#     """Use this when the user asks to display a sleep diary entry. Find the
#     given date and display the entry."""
#     return get_completion(
#         memory,
#         utterance,
#         get_template(goal, get_sleep_diary_entry.__doc__),
#         model_name,
#     )


TOOLS = [get_sleep_diary_description]  # , get_sleep_diary_entry]
