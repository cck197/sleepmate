import logging
from datetime import datetime

from langchain.pydantic_v1 import BaseModel, Field
from mongoengine import ReferenceField

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import mongo_to_json, set_attribute
from .structured import pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)
from .goal import goal_refused
from .history import DBHealthHistory
from .structured import SummaryResult, get_document_summary


class BackPainSeen(BaseModel):
    date: datetime = Field(description="date of entry", default=datetime.now())


DBBackPainSeen = pydantic_to_mongoengine(
    BackPainSeen,
    extra_fields={"user": ReferenceField(DBUser, required=True)},
)

DBBackPainSummary = pydantic_to_mongoengine(
    SummaryResult,
    extra_fields={"history": ReferenceField(DBHealthHistory, required=True)},
)


def save_back_pain_seen_to_db(user: str, entry: BackPainSeen) -> DBBackPainSeen:
    # delete any existing entries for this date
    DBBackPainSeen.objects(user=user).delete()
    # save the new entry
    return DBBackPainSeen(**{"user": user, **entry}).save()


@set_attribute("return_direct", False)
def get_back_pain_seen(x: BaseAgent, utterance: str):
    """Returns True if the human has already seen the back pain recommendations."""
    db_entry = DBBackPainSeen.objects(user=x.db_user_id).first()
    if db_entry is None:
        return f"The human hasn't seen the back pain recommendations yet."
    return mongo_to_json(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def get_back_pain_summary(x: BaseAgent, utterance: str):
    """Returns the back pain summary for the human."""
    db_entry = get_back_pain_summary_(x.db_user_id)
    if db_entry is None:
        return f"The human doesn't have back pain."
    d = db_entry.to_mongo().to_dict()
    # avoid circular reference
    d.pop("history")
    return mongo_to_json(d)


@set_attribute("return_direct", False)
def save_back_pain_seen(x: BaseAgent, utterance: str):
    """Saves a record of the human having seen the back pain recommendations to
    the database."""
    entry = BackPainSeen(date=datetime.now()).dict()
    log.info(f"save_back_pain_seen {entry=}")
    save_back_pain_seen_to_db(x.db_user_id, entry)


def get_back_pain_summary_(db_user_id: str) -> DBBackPainSummary:
    db_history = DBHealthHistory.objects(user=db_user_id).first()
    db_summary = DBBackPainSummary.objects(history=db_history).first()
    if db_summary is not None:
        return db_summary
    if db_history is None:
        return None
    summary = get_document_summary("back pain", db_history)
    if summary is None:
        return None
    return DBBackPainSummary(**{"history": db_history, **summary.dict()}).save()


def back_pain(db_user_id: str):
    """Returns True if back pain recommendations should happen."""
    if goal_refused(db_user_id, "back_pain"):
        return False
    db_entry = get_back_pain_summary_(db_user_id)
    if db_entry is None:
        return False
    return db_entry.found


GOAL_HANDLERS = [
    {
        "back_pain": back_pain,
    },
]

GOALS = [
    {
        "back_pain": """
        Your goal is to help the human with back pain. Steps:
        - Get the summary of the human's back pain by calling
        `get_back_pain_summary`.
        - Ask the human if now is a good time to talk about their back pain.
        - If they say yes, call `get_knowledge_answer` with the query `back pain`.
        - Give the answer to the human.
        - Ask them if they have any questions.
        - Important! Record a record of them having seen the back pain
        recommendations by calling `save_back_pain_seen`.
        """
    }
]

TOOLS = [get_back_pain_seen, save_back_pain_seen, get_back_pain_summary]
