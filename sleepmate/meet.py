import logging

from langchain.memory import ReadOnlySharedMemory
from langchain.schema import BaseMemory

from .goal import goal_refused
from .helpful_scripts import Goal, get_confirmation_str, set_attribute
from .structured import get_parsed_output
from .user import User, get_user_from_id

log = logging.getLogger(__name__)


def get_user_from_memory(memory: BaseMemory) -> User:
    return get_parsed_output("summarise the human's details", memory, User)


def edit_user_(db_user_id: str, key: str, utterance: str):
    db_user = get_user_from_id(db_user_id)
    setattr(db_user, key, utterance)
    log.info(f"edit_user {db_user.to_mongo().to_dict()=}")
    db_user.save()


@set_attribute("return_direct", False)
def edit_user_name(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Use this to change the human's name."""
    return edit_user_(db_user_id, "name", utterance)


@set_attribute("return_direct", False)
def edit_user_email(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Use this to change the human's email."""
    return edit_user_(db_user_id, "email", utterance)


@set_attribute("return_direct", False)
def save_user(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Use this to save the human's name and email address to the database."""
    entry = get_user_from_memory(memory)
    log.info(f"save_user {entry=}")
    if entry is not None:
        db_user = get_user_from_id(db_user_id)
        if db_user is None:
            return
        # only update the database user fields if they haven't already been set
        if db_user.name is None:
            db_user.name = entry.name
        if db_user.email is None:
            db_user.email = entry.email
        db_user.save()


def meet(db_user_id: str) -> bool:
    if goal_refused(db_user_id, "meet", days=7):
        return False
    db_user = get_user_from_id(db_user_id)
    return db_user.name is None or db_user.email is None


GOAL_HANDLERS = [
    {
        "meet": meet,
    },
]

GOALS = [
    {
        "meet": f"""
        Greet the human then ask the following questions:
        - What is your name?
        - What is your email address? (so that we can be in contact offline)
        - Confirm that the name and email address are correct.
         
        Only once they confirm by saying something like
        {get_confirmation_str()}, save their details to the database."""
    }
]

TOOLS = [save_user, edit_user_name, edit_user_email]
