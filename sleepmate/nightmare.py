import logging
from datetime import date, datetime, time, timedelta

from langchain.pydantic_v1 import BaseModel, Field
from mongoengine import ReferenceField

from .agent import BaseAgent
from .diary import DBSleepDiaryEntry
from .goal import goal_refused
from .helpful_scripts import mongo_to_json, set_attribute
from .sleep50 import get_last_sleep50_entry_from_db, sum_category
from .structured import pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)
from .goal import goal_refused
from .structured import SummaryResult, get_document_summary


class NightmareSeen(BaseModel):
    date: datetime = Field(description="date of entry", default=datetime.now())


DBNightmareSeen = pydantic_to_mongoengine(
    NightmareSeen,
    extra_fields={"user": ReferenceField(DBUser, required=True)},
)

DBNightmareDailySeen = pydantic_to_mongoengine(
    NightmareSeen,
    extra_fields={"user": ReferenceField(DBUser, required=True)},
)

DBNightmareSummary = pydantic_to_mongoengine(
    SummaryResult,
    extra_fields={"diary_entry": ReferenceField(DBSleepDiaryEntry, required=True)},
)


def save_nightmare_seen_to_db(user: str, entry: NightmareSeen) -> DBNightmareSeen:
    # save the new entry
    return DBNightmareSeen(**{"user": user, **entry}).save()


@set_attribute("return_direct", False)
def get_nightmare_seen(x: BaseAgent, utterance: str):
    """Returns True if the human has already seen the nightmare recommendations."""
    db_entry = DBNightmareSeen.objects(user=x.db_user_id).first()
    if db_entry is None:
        return f"The human hasn't seen the nightmare recommendations yet."
    return mongo_to_json(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def save_nightmare_seen(x: BaseAgent, utterance: str):
    """Saves a record of the human having seen the nightmare recommendations to
    the database."""
    entry = NightmareSeen(date=datetime.now()).dict()
    log.info(f"save_nightmare_seen {entry=}")
    save_nightmare_seen_to_db(x.db_user_id, entry)


def nightmare(db_user_id: str):
    """Returns True if nightmare recommendations should happen."""
    # check the frightening dreams questions
    db_entry = get_last_sleep50_entry_from_db(db_user_id)
    (n, total) = sum_category(db_entry, "nightmares")
    if n == total:
        return False  # no problem here
    if goal_refused(db_user_id, "nightmare"):
        return False
    return DBNightmareSeen.objects(user=db_user_id).count() == 0


def get_nightmare_summary_(db_user_id: str) -> DBNightmareSummary:
    db_entry = DBSleepDiaryEntry.objects(user=db_user_id).order_by("-id").first()
    db_summary = DBNightmareSummary.objects(diary_entry=db_entry).first()
    if db_summary is not None:
        return db_summary
    if db_entry is None:
        return None
    summary = get_document_summary("frightening dreams", db_entry)
    if summary is None:
        return None
    return DBNightmareSummary(**{"diary_entry": db_entry, **summary.dict()}).save()


def nightmare_daily(db_user_id: str):
    """Returns True if nightmare recommendations should happen."""
    # check for nightmares in the last sleep diary entry
    if goal_refused(db_user_id, "nightmare_daily"):
        return False

    end = datetime.combine(date.today(), time())
    start = end - timedelta(days=1)
    if DBNightmareSeen.objects(user=db_user_id, date__gte=start).count() > 0:
        return False

    db_entry = get_nightmare_summary_(db_user_id)
    if db_entry is None:
        return False
    return db_entry.found


GOAL_HANDLERS = [
    {
        "nightmare": nightmare,
        "nightmare_daily": nightmare_daily,
    },
]

IRT_PROMPT = """
Your goal is to help the human with nightmares or frightening dreams
using Imagery Rehearsal Therapy. Steps:
- Ask the human if now is a good time to talk about their unpleasant
dreams.
- Ask them how long they have been having the dreams.
- Explain that early on, nightmares might help to relive the experience
and remember important details that might be meaningful to the human;
the dreams might provide useful information for emotional processing,
either spontaneously through dreaming, rapid eye movement sleep.
- If the dreams have been going on for a long time, explain it's
questionable if they are still useful.
- So if the dreams are no longer useful, why have they persisted so long?
- Nightmares are a learned behaviour, a broken record that keeps playing
the same tune.
- Give some examples.
- Explain that Imagery Rehearsal Therapy is a way to change the record.
- Use Imagery Rehearsal Therapy to help the human change their
nightmare.
- Important! Record a record of them having seen the nightmare
recommendations by calling `save_nightmare_seen`.
"""

GOALS = [
    {
        "nightmare": IRT_PROMPT,
        "nightmare_daily": IRT_PROMPT,
    }
]

TOOLS = [get_nightmare_seen, save_nightmare_seen]
