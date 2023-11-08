import logging
from datetime import date, datetime, time, timedelta

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import (
    get_confirmation_str,
    get_date_fields,
    mongo_to_json,
    parse_date,
    set_attribute,
)
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)

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


def get_seed_pod_from_memory(x: BaseAgent) -> SeedPod:
    return get_parsed_output("summarise the SEEDS", x.get_latest_messages, SeedPod)


def save_seed_pod_to_db(user: str, entry: SeedPod) -> DBSeedPod:
    return DBSeedPod(**{"user": user, **entry.dict()}).save()


def get_json_seed_pod(entry: dict) -> str:
    """Returns the SEEDS in JSON format"""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_seed_pod(x: BaseAgent, utterance: str):
    """Use this to save a SEEDS to the database."""
    entry = get_seed_pod_from_memory(x)
    log.info(f"save_seed_pod {entry=}")
    if entry is None:
        return
    save_seed_pod_to_db(x.db_user_id, entry)


def get_current_seed_pod(db_user_id: str) -> DBSeedPod:
    """Returns current SEEDS."""
    return DBSeedPod.objects(user=db_user_id).order_by("-id").first()


@set_attribute("return_direct", False)
def get_seed_pod(x: object, utterance: str):
    """Returns predefined SEEDS tasks from the database."""
    entry = get_current_seed_pod(x.db_user_id)
    if entry is not None:
        return get_json_seed_pod(entry.to_mongo().to_dict())


######################################################################
# SeedsDiaryEntry (a completed set of SEEDS tasks diary entry)
######################################################################


class SeedsDiaryEntry_(BaseModel):
    """A list of completed tasks"""

    date: datetime = Field(description="date of entry")
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
        return parse_date(value, default_days=1)


DBSeedsDiaryEntry = pydantic_to_mongoengine(
    SeedsDiaryEntry, extra_fields={"pod": ReferenceField(DBSeedPod, required=True)}
)


def get_seeds_from_memory(x: BaseAgent) -> SeedsDiaryEntry:
    return get_parsed_output(
        "summarise the SEEDS diary entry", x.get_latest_messages, SeedsDiaryEntry
    )


def save_seeds_diary_entry_to_db(
    pod: DBSeedPod, entry: SeedsDiaryEntry
) -> DBSeedsDiaryEntry:
    return DBSeedsDiaryEntry(**{"pod": pod, **entry.dict()}).save()


def get_json_seeds(entry: dict) -> str:
    """Returns the SEEDS diary entry in JSON format"""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_seeds_diary_entry(x: BaseAgent, utterance: str):
    """Use this to save a SEEDS diary entry to the database."""
    entry = get_seeds_from_memory(x)
    log.info(f"save_seeds_diary_entry {entry=}")
    if entry is None:
        return
    save_seeds_diary_entry_to_db(get_current_seed_pod(x.db_user_id), entry)


def get_current_seeds(db_user_id: str) -> DBSeedsDiaryEntry:
    """Returns the last SEEDS diary entry."""
    return (
        DBSeedsDiaryEntry.objects(pod=get_current_seed_pod(db_user_id))
        .order_by("-id")
        .first()
    )


@set_attribute("return_direct", False)
def get_seeds_diary_entry(x: BaseAgent, utterance: str):
    """Returns the last SEEDS diary entry from the database."""
    db_entry = get_current_seeds(x.db_user_id)
    log.info(f"get_seeds_diary_entry {db_entry=}")
    if db_entry is not None:
        entry = db_entry.to_mongo().to_dict()
        entry["pod"] = get_json_seed_pod(db_entry.pod.to_mongo().to_dict())
        return get_json_seeds(entry)


@set_attribute("return_direct", False)
def delete_seeds_diary_entry(x: BaseAgent, utterance: str):
    """Deletes the last SEEDS diary entry from the database."""
    db_entry = get_current_seeds(x.db_user_id)
    log.info(f"delete_seeds_diary_entry {db_entry=}")
    if db_entry is not None:
        db_entry.delete()
        return True
    return False


@set_attribute("return_direct", False)
def get_seeds_diary_entry_score(x: BaseAgent, utterance: str):
    """Returns the total number of tasks completed in the SEEDS diary entry."""
    db_entry = get_current_seed_pod(x.db_user_id)
    if db_entry is None:
        return
    entry = db_entry.to_mongo().to_dict()
    # get the keys for all the predefined SEEDS tasks
    keys = [k for (k, v) in entry.items() if type(v) is str and v]
    db_entry = get_current_seeds(x.db_user_id)
    if db_entry is None:
        return
    entry = db_entry.to_mongo().to_dict()
    # return the total number of tasks completed
    return sum([entry[k] for k in keys])


def seeds_entry(db_user_id: str) -> bool:
    if goal_refused(db_user_id, "seeds_probe", days=None) or goal_refused(
        db_user_id, "seeds_entry"
    ):
        return False

    end = datetime.combine(date.today(), time())
    start = end - timedelta(days=1)

    return (
        DBSeedsDiaryEntry.objects(
            pod=get_current_seed_pod(db_user_id), date__gte=start
        ).count()
        == 0
    )


def seeds_probe(db_user_id: str) -> bool:
    return (
        not goal_refused(db_user_id, "seeds_probe", days=7)
        and DBSeedPod.objects(user=db_user_id).count() == 0
    )


GOAL_HANDLERS = [
    {
        "seeds_probe": seeds_probe,
        "seeds_entry": seeds_entry,
    },
]

GOALS = [
    {
        "seeds_probe": f"""
        Your goal is to ask the human to do the SEEDS exercise created by Simon
        Marshall, PhD. Explain briefly what's involved and then ask if they'd
        like to know more. Once they confirm by saying something like
        {get_confirmation_str()}, summarise the exercise using the following:
        
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

        Before collecting SEEDS from the human, give some examples:
        - Be in bed by 9.30 pm.
        - Go to bed *only* when sleepy.
        - Set an alarm and get up at the same time every day.
        - Go for 2 min walk when you feel the need for a nap.
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

        Once you have all the SEEDS defined, STOP! Summarise the results
        in a bullet list and ask if they're correct.

        Only once the human has confirmed correctness, save the SEEDS to
        the database.
        
        Finally, retrieve the entry from the database and
        summarise
        """,
    },
    {
        "seeds_entry": """
        Your goal is to help the human record a SEEDS diary entry.

        Steps: 
        - Ask if now is a good time to record a SEEDS diary entry
        - Get their predefined SEEDS from the database and summarise all the
        predefined tasks in a bullet list
        - Date of entry (ask to confirm default of yesterday's date)
        - Ask what they got done today
        - Summarise all the tasks in a bullet list and ask if correct
        - If they didn't specify a date, get the date for yesterday and use that
        - Save the SEEDS diary entry to the database
        - Get N, the total number of tasks completed in the SEEDS diary entry
        - Give them a score N out of 15
        """,
    },
]

TOOLS = [
    get_seed_pod,
    save_seed_pod,
    get_seeds_diary_entry,
    save_seeds_diary_entry,
    get_seeds_diary_entry_score,
    delete_seeds_diary_entry,
]
