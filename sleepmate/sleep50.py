import logging
from datetime import datetime

from langchain.pydantic_v1 import BaseModel, Field, validator
from mongoengine import ReferenceField

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import (
    get_date_fields,
    json_dumps,
    mongo_to_json,
    parse_date,
    set_attribute,
)
from .structured import fix_schema, get_parsed_output, pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)


class Sleep50Entry_(BaseModel):
    date: datetime = Field(description="date of entry")
    sleep_apnea_1: int = Field(description="snore")
    sleep_apnea_2: int = Field(description="sweat during the night")
    sleep_apnea_3: int = Field(description="hold breath when sleeping")
    sleep_apnea_4: int = Field(description="wake up gasping for air")
    sleep_apnea_5: int = Field(description="wake up with a dry mouth")
    sleep_apnea_6: int = Field(
        description="wake up during the night while coughing or being short of breath"
    )
    sleep_apnea_7: int = Field(description="wake up with a sour taste")
    sleep_apnea_8: int = Field(description="wake up with a headache")
    insomnia_9: int = Field(description="difficulty falling asleep")
    insomnia_10: int = Field(
        description="thoughts go through my head and keep me awake"
    )
    insomnia_11: int = Field(description="worry and find it hard to relax")
    insomnia_12: int = Field(description="wake up during the night")
    insomnia_13: int = Field(
        description="fall asleep slowly after waking up during night"
    )
    insomnia_14: int = Field(description="wake up early and cannot get back to sleep")
    insomnia_15: int = Field(description="sleep lightly")
    insomnia_16: int = Field(description="sleep too little")
    narcolepsy_17: int = Field(description="see dreamlike images when falling asleep")
    narcolepsy_18: int = Field(description="fall asleep on a social occasion")
    narcolepsy_19: int = Field(description="sleep attacks during the day")
    narcolepsy_20: int = Field(description="muscles sometimes collapse during the day")
    narcolepsy_21: int = Field(
        description="cannot move when falling asleep or waking up"
    )
    restless_legs_22: int = Field(description="kick my legs when I sleep")
    restless_legs_23: int = Field(
        description="cramps or pain in my legs during the night"
    )
    restless_legs_24: int = Field(
        description="little shocks in my legs during the night"
    )
    restless_legs_25: int = Field(
        description="cannot keep my legs at rest when falling asleep"
    )
    circadian_rhythm_26: int = Field(description="go to bed at a different time")
    circadian_rhythm_27: int = Field(description="go to bed at very different times")
    circadian_rhythm_28: int = Field(description="do shift work")
    sleepwalking_29: int = Field(description="walk when I am sleeping")
    sleepwalking_30: int = Field(
        description="wake up in a different place than where I fell asleep"
    )
    sleepwalking_31: int = Field(
        description="find evidence of having performed an action during the night I do not remember"
    )
    nightmares_32: int = Field(description="have frightening dreams")
    nightmares_33: int = Field(description="wake up from these dreams")
    nightmares_34: int = Field(description="remember the content of these dreams")
    nightmares_35: int = Field(description="can orientate quickly after these dreams")
    nightmares_36: int = Field(
        description="have physical symptoms during or after these dreams"
    )
    factors_37: int = Field(description="too light in my bedroom during the night")
    factors_38: int = Field(description="too noisy in my bedroom during the night")
    factors_39: int = Field(description="drink alcoholic beverages during the evening")
    factors_40: int = Field(description="smoke during the evening")
    factors_41: int = Field(description="use other substances during the evening")
    factors_42: int = Field(description="feel sad")
    factors_43: int = Field(
        description="have no pleasure or interest in daily occupations"
    )
    impact_44: int = Field(description="feel tired at getting up")
    impact_45: int = Field(
        description="feel sleepy during the day and struggle to remain alert"
    )
    impact_46: int = Field(description="would like to have more energy during the day")
    impact_47: int = Field(description="am told that I am easily irritated")
    impact_48: int = Field(
        description="have difficulty in concentrating at work or school"
    )
    impact_49: int = Field(description="worry whether I sleep enough")
    impact_50: int = Field(description="generally, I sleep badly")
    additional_a: int = Field(description="rate my sleep as")
    additional_b: int = Field(description="sleep hours")


date_fields = get_date_fields(Sleep50Entry_)


class Sleep50Entry(Sleep50Entry_):
    @classmethod
    def schema(cls):
        return fix_schema(Sleep50Entry_, date_fields)

    @validator(*date_fields, pre=True)
    def convert_date_to_datetime(cls, value):
        return parse_date(value, default_days=0)


DBSleep50Entry = pydantic_to_mongoengine(
    Sleep50Entry, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def sum_category(db_entry: DBSleep50Entry, category: str) -> int:
    """Returns the number of items in the category and the sum of the values. If
    the sum of the values for the category is greater than the length, then the
    human answered something greater than or equal to "somewhat" for at least
    one of the questions."""
    values = [
        getattr(db_entry, key) for key in db_entry._fields.keys() if category in key
    ]
    return len(values), sum(values)


def get_sleep50_entry_from_memory(x: BaseAgent) -> Sleep50Entry:
    return get_parsed_output(
        "summarise the last sleep history entry",
        x.get_latest_messages,
        Sleep50Entry,
    )


def save_sleep50_entry_to_db(user: str, entry: Sleep50Entry) -> DBSleep50Entry:
    # delete any existing entries for this date
    entry = entry.dict()
    DBSleep50Entry.objects(user=user, date=entry["date"]).delete()
    # save the new entry
    return DBSleep50Entry(**{"user": user, **entry}).save()


def get_json_sleep50_entry(entry: dict) -> str:
    """Returns the sleep history entry in JSON format."""
    return mongo_to_json(entry)


@set_attribute("return_direct", False)
def save_sleep50_entry(x: BaseAgent, utterance: str):
    """Saves the sleep history entry to the database. Call *only* after all 50
    questions have been answered."""
    entry = get_sleep50_entry_from_memory(x)
    if entry is not None:
        log.info(f"save_sleep50_entry {entry=}")
        save_sleep50_entry_to_db(x.db_user_id, entry)


def get_last_sleep50_entry_from_db(db_user_id: str) -> DBSleep50Entry:
    """Returns the last sleep history entry from the database."""
    return DBSleep50Entry.objects(user=db_user_id).order_by("-id").first()


@set_attribute("return_direct", False)
def get_last_sleep50_entry(x: BaseAgent, utterance: str):
    """Returns the last sleep history entry."""
    db_entry = get_last_sleep50_entry_from_db(x.db_user_id)
    if db_entry is None:
        return "No sleep history entries found"
    entry = db_entry.to_mongo().to_dict()
    log.info(f"get_last_sleep50_entry {entry=}")
    return get_json_sleep50_entry(entry)


@set_attribute("return_direct", False)
def get_date_sleep50_diary_entry(x: BaseAgent, utterance: str):
    """Returns the sleep history entry for a given date."""
    date = parse_date(utterance)
    db_entry = DBSleep50Entry.objects(user=x.db_user_id, date=date).first()
    if db_entry is None:
        return f"No sleep50 entry found for {date.date()}"
    return get_json_sleep50_entry(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def get_sleep50_dates(x: BaseAgent, utterance: str):
    """Returns the dates of all sleep history entries in JSON format.
    Call with exactly one argument."""
    return json_dumps([e.date for e in DBSleep50Entry.objects(user=x.db_user_id)])


def sleep50(db_user_id: str) -> bool:
    if goal_refused(db_user_id, "sleep50"):
        return False
    return DBSleep50Entry.objects(user=db_user_id).count() == 0


GOAL_HANDLERS = [
    {
        "sleep50": sleep50,
    },
]

GOALS = [
    {
        "sleep50": """
        Your goal is to survey the human using the questionnaire below. Ask if
        now would be a good time then ask the following questions. Get today's
        date and display it. Step through the questionnaire one section at a
        time, starting with Sleep Apnea. Show progress as you go step N of 10.
        
        Please respond to what extent a statement (item) has been applicable to
        you during the past 4 weeks. Each item is scored on a 4-point-scale: 1
        (not at all), 2 (somewhat), 3 (rather much), and 4 (very much).

        Sleep Apnea
        1. I am told that I snore.
        2. I sweat during the night.
        3. I am told that I hold my breath when sleeping.
        4. I am told that I wake up gasping for air.
        5. I wake up with a dry mouth.
        6. I wake up during the night while coughing or being short of breath.
        7. I wake up with a sour taste in my mouth.
        8. I wake up with a headache.

        Insomnia
        1. I have difficulty in falling asleep.
        2. Thoughts go through my head and keep me awake.
        3. I worry and find it hard to relax.
        4. I wake up during the night.
        5. After waking up during the night, I fall asleep slowly.
        6. I wake up early and cannot get back to sleep.
        7. I sleep lightly.
        8. I sleep too little.

        Narcolepsy
        1. I see dreamlike images when falling asleep or waking up.
        2. I sometimes fall asleep on a social occasion.
        3. I have sleep attacks during the day.
        4. With intense emotions, my muscles sometimes collapse during the day.
        5. I sometimes cannot move when falling asleep or waking up.

        Restless Legs/Periodic Limb Movement Disorder (PLMD)
        1. I am told that I kick my legs when I sleep.
        2. I have cramps or pain in my legs during the night.
        3. I feel little shocks in my legs during the night.
        4. I cannot keep my legs at rest when falling asleep.

        Circadian Rhythm Sleep Disorder
        1. I would rather go to bed at a different time.
        2. I go to bed at very different times (more than 2 hr difference).
        3. I do shift work.

        Sleepwalking
        1. I sometimes walk when I am sleeping.
        2. I sometimes wake up in a different place than where I fell asleep.
        3. I sometimes find evidence of having performed an action during the
        night I do not remember.
        
        Nightmares
        1. I have frightening dreams.
        2. I wake up from these dreams.
        3. I remember the content of these dreams.
        4. I can orientate quickly after these dreams.
        5. I have physical symptoms during or after these dreams (e.g.,
        movements, sweating, heart palpitations, shortness of breath).

        Factors Influencing Sleep
        1. It is too light in my bedroom during the night.
        2. It is too noisy in my bedroom during the night.
        3. I drink alcoholic beverages during the evening.
        4. I smoke during the evening.
        5. I use other substances during the evening (e.g., sleep or other
        medication).
        6. I feel sad.
        7. I have no pleasure or interest in daily occupations.

        Impact of Sleep Complaints on Daily Functioning
        1. I feel tired at getting up.
        2. I feel sleepy during the day and struggle to remain alert.
        3. I would like to have more energy during the day.
        4. I am told that I am easily irritated.
        5. I have difficulty in concentrating at work or school.
        6. I worry whether I sleep enough.
        7. Generally, I sleep badly

        Additional Questions
        1. I rate my sleep as _____ (1 = very bad, 10 = very good)
        2. I sleep _____ hours, mostly from _____ to _____.
        
        When you've got the answer to all 50 questions, summarise all the
        questions and answers in a numbered list including the date. Ask if
        they're correct.
        
        Only once the human has confirmed correctness, save the sleep history
        entry to the database.
        """
    },
]

TOOLS = [
    get_last_sleep50_entry,
    get_date_sleep50_diary_entry,
    get_sleep50_dates,
    save_sleep50_entry,
]
