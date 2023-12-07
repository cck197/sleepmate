import logging

from .agent import BaseAgent
from .goal import goal_refused
from .helpful_scripts import get_confirmation_str, set_attribute
from .structured import get_parsed_output
from .user import User, get_user_from_id

log = logging.getLogger(__name__)


def get_user_from_memory(x: BaseAgent) -> User:
    return get_parsed_output(
        "summarise the human's details", x.get_latest_messages, User
    )


def edit_user_(db_user_id: str, key: str, utterance: str):
    db_user = get_user_from_id(db_user_id)
    setattr(db_user, key, utterance)
    log.info(f"edit_user {db_user.to_mongo().to_dict()=}")
    db_user.save()


@set_attribute("return_direct", False)
def edit_user_name(x: BaseAgent, utterance: str):
    """Use this to change the human's name."""
    return edit_user_(x.db_user_id, "name", utterance)


@set_attribute("return_direct", False)
def edit_user_email(x: BaseAgent, utterance: str):
    """Use this to change the human's email."""
    return edit_user_(x.db_user_id, "email", utterance)


@set_attribute("return_direct", False)
def save_user(x: BaseAgent, utterance: str):
    """Use this to save the human's name and email address to the database."""
    entry = get_user_from_memory(x)
    log.info(f"save_user {entry=}")
    if entry is not None:
        db_user = get_user_from_id(x.db_user_id)
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
        - What is your email address? (don't worry, I won't spam you)
        - Confirm that the name and email address are correct.
         
        Only once they confirm by saying something like
        {get_confirmation_str()}, save their details to the database."""
    }
]

TOOLS = [save_user, edit_user_name, edit_user_email]
