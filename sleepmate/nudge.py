from datetime import datetime, timedelta

from langchain.pydantic_v1 import BaseModel, Field
from mongoengine import ReferenceField

from .agent import BaseAgent
from .config import SLEEPMATE_NUDGE_TIME
from .mi import get_greeting_no_memory
from .structured import pydantic_to_mongoengine
from .user import DBUser, get_user_from_id

######################################################################
# Nudge model
######################################################################


class Nudge(BaseModel):
    text: str = Field(description="nudge text", default="")
    last_seen: datetime = Field(description="last time user was seen")
    job_id: str = Field(description="job id of the nudge", default="")


DBNudge = pydantic_to_mongoengine(
    Nudge, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def get_nudge(db_user_id: str):
    db_user = get_user_from_id(db_user_id)
    return DBNudge.objects(user=db_user).first()


def get_or_create_nudge(x: BaseAgent, seen: bool = False) -> bool:
    """Create a nudge for a user or return the existing one."""

    def inner():
        db_user = get_user_from_id(x.db_user_id)
        db_nudge = DBNudge.objects(user=db_user).first()
        last_seen = datetime.now()
        if db_nudge is None:
            db_nudge = DBNudge(user=db_user, last_seen=last_seen)
        if seen:
            db_nudge.last_seen = last_seen
        return db_nudge

    db_nudge = inner()
    if not db_nudge.text:
        db_nudge.text = get_greeting_no_memory(x, "hey")
    db_nudge.save()
    return db_nudge


def should_send_nudge(db_nudge: DBNudge, seconds: int = SLEEPMATE_NUDGE_TIME) -> bool:
    """Return True if the nudge should be sent."""
    return db_nudge.last_seen + timedelta(seconds=seconds) < datetime.now()


def set_nudge(db_nudge: DBNudge, job_id, reset_text=False) -> None:
    """Reset the nudge."""
    db_nudge.job_id = job_id
    if reset_text:
        db_nudge.text = ""
    db_nudge.save()
