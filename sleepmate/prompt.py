from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

from .config import SLEEPMATE_STOP_SEQUENCE, SLEEPMATE_SYSTEM_DESCRIPTION
from .helpful_scripts import Goal
from .user import get_user_by_id


def get_system_prompt(
    goal: Goal,
    db_user,
    stop_sequence: str = SLEEPMATE_STOP_SEQUENCE,
) -> str:
    system = SLEEPMATE_SYSTEM_DESCRIPTION
    if goal is not None:
        system = (
            f"{system}\n{goal.description}\n"
            "Very important! Don't ask the human how you can assist them. "
            "Instead, get to the goal as quickly as possible.\n"
        )
        if stop_sequence:
            system = (
                f"{system}\nIf and only if the human refuses the goal, "
                "output a listening statement followed by "
                f"{stop_sequence} to end the conversation."
            )
        system = (
            f"{system}\nWhen the goal is achieved, ask the human to say `ahoy' to "
            "let you know when they're ready to continue on their health journey."
        )
    if db_user is not None:
        system = (
            f"{system}\n\nThe human's name is {db_user.name}"
            f", and their email is {db_user.email}"
        )
    return system


def get_template(goal: Goal, db_user_id: str, prompt: str) -> ChatPromptTemplate:
    db_user = get_user_by_id(db_user_id)
    system = get_system_prompt(goal, db_user)
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(f"{system}\n{prompt}"),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )
