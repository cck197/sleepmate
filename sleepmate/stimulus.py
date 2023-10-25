import logging
from datetime import datetime

from langchain.memory import ReadOnlySharedMemory
from langchain.pydantic_v1 import BaseModel, Field
from mongoengine import ReferenceField

from .goal import goal_refused
from .helpful_scripts import Goal, mongo_to_json, set_attribute
from .structured import pydantic_to_mongoengine
from .user import DBUser

log = logging.getLogger(__name__)


class StimulusControlSeen(BaseModel):
    date: datetime = Field(description="date of entry", default=datetime.now())


DBStimulusControlSeen = pydantic_to_mongoengine(
    StimulusControlSeen, extra_fields={"user": ReferenceField(DBUser, required=True)}
)


def save_stimulus_control_seen_to_db(
    user: str, entry: StimulusControlSeen
) -> DBStimulusControlSeen:
    # delete any existing entries for this date
    DBStimulusControlSeen.objects(user=user).delete()
    # save the new entry
    return DBStimulusControlSeen(**{"user": user, **entry}).save()


@set_attribute("return_direct", False)
def get_stimulus_control_seen(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Returns True if the human has already seen the Stimulus Control Therapy
    instructions."""
    db_entry = DBStimulusControlSeen.objects(user=db_user_id).first()
    if db_entry is None:
        return f"The human hasn't seen the stimulus control yet."
    return mongo_to_json(db_entry.to_mongo().to_dict())


@set_attribute("return_direct", False)
def save_stimulus_control_seen(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Saves a record of the human having seen the Stimulus Control Therapy
    Instructions to the database."""
    entry = StimulusControlSeen(date=datetime.now()).dict()
    log.info(f"save_stimulus_control_seen {entry=}")
    save_stimulus_control_seen_to_db(db_user_id, entry)


def stimulus_control(db_user_id: str) -> bool:
    return (
        not goal_refused(db_user_id, "stimulus_control")
        and DBStimulusControlSeen.objects(user=db_user_id).count() == 0
    )


GOAL_HANDLERS = [
    {
        "stimulus_control": stimulus_control,
    },
]

GOALS = [
    {
        "stimulus_control": """
        Your goal is to ask the human what they do in bed other than sleep.
        
        Only if they say they do anything other than sleep, ask them if they're
        open to hearing about Stimulus Control Therapy as described by Richard
        R. Bootzin.
        
        Summarise the rationale for the therapy and the instructions for
        implementing it. Ask them if they're willing to try it.

        Always record a record of them having seen Stimulus Control Therapy in
        the database.
        
        If they agree to try it, explain you'll help them get it done using the
        SEEDS exercise later.
        """
    }
]

TOOLS = [get_stimulus_control_seen, save_stimulus_control_seen]
