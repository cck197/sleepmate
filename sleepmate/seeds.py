from datetime import datetime, timedelta
from typing import List

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
from .mi import get_completion, get_template
from .structured import get_parsed_output, pydantic_to_mongoengine
from .user import DBUser, get_current_user

model_name = "gpt-4"

# Super simple schema optimised for marshalling in and out of the chat history
# memory. Not normalised but meh. It's too hard to translate between the chat
# history (Pydantic) and the database (Mongoengine).

# TODO detect and reject goals, e.g. bench press 100kg, run 5km, etc.
# TODO Traffic Light segmentation and prioritisation.

######################################################################
# SeedPod (set of predefined SEEDS tasks)
######################################################################


class SeedPod(BaseModel):
    """A list of tasks"""

    sleep_1: str = Field(description="sleep 1", default="")
    sleep_2: str = Field(description="sleep 2", default="")
    sleep_3: str = Field(description="sleep 3", default="")
    exercise_1: str = Field(description="exercise 1", default="")
    exercise_2: str = Field(description="exercise 2", default="")
    exercise_3: str = Field(description="exercise 3", default="")
    eating_1: str = Field(description="eating 1", default="")
    eating_2: str = Field(description="eating 2", default="")
    eating_3: str = Field(description="eating 3", default="")
    drinking_1: str = Field(description="drinking 1", default="")
    drinking_2: str = Field(description="drinking 2", default="")
    drinking_3: str = Field(description="drinking 3", default="")
    stress_1: str = Field(description="stress 1", default="")
    stress_2: str = Field(description="stress 2", default="")
    stress_3: str = Field(description="stress 3", default="")


DBSeedPod = pydantic_to_mongoengine(
    SeedPod, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_seed_pod_from_memory(memory: BaseMemory) -> SeedPod:
    return get_parsed_output("summarise the SEEDS", memory, SeedPod)


def save_seed_pod_to_db(user: DBUser, entry: SeedPod) -> DBSeedPod:
    return DBSeedPod(**{"user": user, **entry.dict()}).save()


def get_json_seed_pod(entry: dict) -> str:
    """Returns the SEEDS in JSON format"""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_seed_pod(memory: ReadOnlySharedMemory, goal: str, text: str):
    """Saves SEEDS to the database. Call with exactly one string argument."""
    entry = get_seed_pod_from_memory(memory)
    print(f"save_seed_pod {entry=}")
    save_seed_pod_to_db(get_current_user(), entry)


def get_current_seed_pod() -> DBSeedPod:
    """Returns current SEEDS."""
    return DBSeedPod.objects(user=get_current_user()).order_by("-id").first()


@set_attribute("return_direct", False)
def get_seed_pod(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns predefined SEEDS tasks from the database. Call with exactly one
    string argument."""
    entry = get_current_seed_pod()
    print(f"get_seed_pod {entry=}")
    if entry is not None:
        return get_json_seed_pod(entry.to_mongo().to_dict())


######################################################################
# SeedsDiaryEntry (a completed set of SEEDS tasks diary entry)
######################################################################


class SeedsDiaryEntry_(BaseModel):
    """A list of completed tasks"""

    date: datetime = Field(description="date of entry", default=0)
    sleep_1: int = Field(description="Sleep 1", default=0)
    sleep_2: int = Field(description="Sleep 2", default=0)
    sleep_3: int = Field(description="Sleep 3", default=0)
    exercise_1: int = Field(description="exercise 1", default=0)
    exercise_2: int = Field(description="exercise 2", default=0)
    exercise_3: int = Field(description="exercise 3", default=0)
    eating_1: int = Field(description="eating 1", default=0)
    eating_2: int = Field(description="eating 2", default=0)
    eating_3: int = Field(description="eating 3", default=0)
    drinking_1: int = Field(description="drinking 1", default=0)
    drinking_2: int = Field(description="drinking 2", default=0)
    drinking_3: int = Field(description="drinking 3", default=0)
    stress_1: int = Field(description="stress 1", default=0)
    stress_2: int = Field(description="stress 2", default=0)
    stress_3: int = Field(description="stress 3", default=0)


date_fields = get_date_fields(SeedsDiaryEntry_)


class SeedsDiaryEntry(SeedsDiaryEntry_):
    @classmethod
    def schema(cls):
        return fix_schema(SeedsDiaryEntry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return date_parser(value)


DBSeedsDiaryEntry = pydantic_to_mongoengine(
    SeedsDiaryEntry, extra_fields={"pod": ReferenceField(DBSeedPod, required=True)}
)


def get_seeds_from_memory(memory: BaseMemory) -> SeedsDiaryEntry:
    return get_parsed_output("summarise the SEEDS diary entry", memory, SeedsDiaryEntry)


def save_seeds_to_db(pod, DBSeedPod, entry: SeedsDiaryEntry) -> DBSeedPod:
    return DBSeedPod(**{"pod": pod, **entry.dict()}).save()


def get_json_seeds(entry: dict) -> str:
    """Returns the SEEDS diary entry in JSON format"""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_seeds_diary_entry(memory: ReadOnlySharedMemory, goal: str, text: str):
    """Saves a SEEDS diary entry to the database. Call with exactly one string
    argument."""
    entry = get_seeds_from_memory(memory)
    print(f"save_seeds {entry=}")
    save_seeds_to_db(get_current_seed_pod(), entry)


def get_current_seeds() -> DBSeedsDiaryEntry:
    """Returns the last SEEDS diary entry."""
    return DBSeedsDiaryEntry.objects(pod=get_current_seed_pod()).order_by("-id").first()


@set_attribute("return_direct", False)
def get_seeds_diary_entry(memory: ReadOnlySharedMemory, goal: str, utterance: str):
    """Returns SEEDS diary entry from the database. Call with exactly one string
    argument."""
    entry = get_current_seeds()
    print(f"get_seeds {entry=}")
    if entry is not None:
        return get_json_seeds(entry.to_mongo().to_dict())


GOALS = [
    {
        "seeds_probe": """
        Your goal is to ask the human to do the SEEDS exercise created by Simon
        Marshall, PhD. Summarise the exercise using the text below surrounded by
        triple backticks.

        ```   
        The pillars of good health are Sleep, Exercise, Eating, Drinking, and
        Stress management (SEEDS). Yes, "SEEDS" is cheesy as fuck, but the
        metaphor of planting small SEEDS (i.e., behaviors that are good for you)
        and watering them every day so they can take root (i.e., become habits
        that you don't have to constantly think about them) is consistent with
        the science of behavior change and habit formation. So, while the
        acronym may be the Celine Dion of behavior change, it WORKS. Besides,
        what's life without cheese?

        For each of these pillars of good health, think of a tiny thing that you
        can do to contribute to it. This is not the place for grandiose,
        aspirational intentions (e.g., "run 5km" or "eat no added sugar" if
        you've never come close this in the past), or the fat-chance outcomes
        (e.g., "get sleep 8 hours per night" when you're currently getting 5
        hrs). In SEEDS, we're focusing on tiny little behaviors that contribute
        to good outcomes. The behavioral science is that focusing on SMALL
        behaviors builds the correct mindset and contributes to knock-on effects
        on other changes in that Pillar.  In short, progress begets progress.
        So, a good way to think about each SEED is that your reaction to it
        should be "shit, even I could do that," not "urgh, I mean, I'll give it
        a go but don't hold your breath."

        Simon likes to use three SEEDS per pillar, for a total of 15 teeny-weeny
        daily habits. If that sounds like A LOT to you, he recommends you
        prioritize them.  The top line is what you'll start with. Once you've
        done these consistently, add the second line, and so on. Regardless, try
        to first WRITE IN all fifteen in this exercise.

        You'll see that this also gives us a way to way to measure progress and
        consistency. Later we'll ask what you got done and give you a score
        (/15) for how many you managed to do that day. The importance of the
        score will become more evident when we progress to Phase 2 of our Celine
        Dion exercise, the veritable Kenny G of stress management mojo - a
        Traffic Light system to avoid catastrophizing, awfulizing, and
        why-can't-I-do this-izing, when life gets in the way (because it will).
        We need to give ourselves permission to occasionally suck at adulting.
        ```

        Before collecting SEEDS from the human, give some examples:
        - Be in bed by 9.30 pm.
        - Turn off my cell phone by 8 pm.
        - Walk outside for 10 ten minutes before 9:30 am.
        - Do 10 push-ups while the coffee is brewing.
        - Eat one meal with chopsticks (to slow down eating).
        - Eat 50g of protein with every meal.
        - Don't drink out of anything plastic.
        - Drink fizzy water from 6-8 pm (for booze cravings).
        - Write down three tiny things I've been grateful for today.
        - No caffeine after 12 pm.
        - Do the "leaves on a stream" or "open focus" exercises (for stress).
        - ...you get the idea.

        Collect the SEEDS from the human one category at a time. 

        Finish by giving a summary of the SEEDS they defined for each category
        and asking if they're correct. Only after they've confirmed, save the
        SEEDS to the database.
        """,
    },
    {
        "seeds_entry": """
        Your goals to ask the human about what SEEDS they managed to do today.
        First, ask if now is a good time to record a SEEDS diary entry.
        Summarise the SEEDS they gave earlier. Ask what date the entry is for,
        suggest today as a default. Then, for each SEED in each pillar, ask what
        they got done today. Then summarise and ask if it's correct. Give them a
        score (/15) for how many they managed to do that day.

        Only after they've confirmed, save the SEEDS diary entry to the database.
        """,
    },
]

TOOLS = [get_seed_pod, save_seed_pod, get_seeds_diary_entry, save_seeds_diary_entry]
