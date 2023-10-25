import logging

from langchain.memory import ReadOnlySharedMemory
from langchain.schema import BaseMemory

from .goal import goal_refused
from .helpful_scripts import Goal, get_confirmation_str, set_attribute
from .structured import get_parsed_output
from .user import DBUser, User, get_user_by_id

log = logging.getLogger(__name__)


def get_user_from_memory(memory: BaseMemory) -> User:
    return get_parsed_output("summarise the human's details", memory, User)


@set_attribute("return_direct", False)
def save_user(
    memory: ReadOnlySharedMemory, goal: Goal, db_user_id: str, utterance: str
):
    """Use this to save the human's name and email address to the database."""
    entry = get_user_from_memory(memory)
    log.info(f"save_user {entry=}")
    if entry is not None:
        d = entry.dict()
        d.pop("username", None)
        db_user = get_user_by_id(db_user_id)
        db_user.update(**d)
        db_user.save()


def meet(db_user_id: str) -> bool:
    if goal_refused(db_user_id, "meet", days=7):
        return False
    db_user = get_user_by_id(db_user_id)
    return db_user.name is None or db_user.email is None


GOAL_HANDLERS = [
    {
        "meet": meet,
    },
]

GOALS = [
    {
        "meet": f"""
        Greet the human then ask their name and email address. The email address
        is so that we can be in contact offline. Once you have both their name
        and email address, confirm they are correct.  Only once they confirm by
        saying something like {get_confirmation_str()}, save their details to
        the database."""
    }
]

TOOLS = [save_user]
