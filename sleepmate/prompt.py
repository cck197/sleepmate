import logging
from datetime import datetime, timedelta
from functools import partial
from typing import Any, Dict, List, Tuple, Union

from langchain.callbacks.base import BaseCallbackHandler
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AgentAction, BaseMessage, HumanMessage
from langchain.tools import BaseTool, Tool

from .agent import BaseAgent
from .config import SLEEPMATE_STOP_SEQUENCE, SLEEPMATE_SYSTEM_DESCRIPTION
from .helpful_scripts import Goal, json_dumps, set_attribute, strip_all_whitespace
from .user import get_user_from_id

log = logging.getLogger(__name__)


class MessageHandler(BaseCallbackHandler):
    def __init__(self, callback) -> None:
        super().__init__()
        self.callback = callback

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any,
    ) -> Any:
        self.callback(messages)


class GoalRefusedHandler(BaseCallbackHandler):
    def __init__(self, callback) -> None:
        super().__init__()
        self.callback = callback

    def on_agent_finish(self, action: AgentAction, **kwargs: Any) -> Any:
        # print(f"on_agent_finish {action}")
        if SLEEPMATE_STOP_SEQUENCE in action.return_values["output"]:
            self.callback(action)


@set_attribute("return_direct", False)
def get_date(x: object, utterance: str):
    """Use this whenever you need to get the date. This function take one
    argument that is the number of days to subtract from today's date. For
    example, if you want to get yesterday's date, you would call this function
    with 1 as the argument. And if you wanted today's date you would call this
    with 0."""
    # return the date formatted like like November 8th, 2023
    return (datetime.now() - timedelta(days=int(utterance))).strftime("%B %d, %Y")


TOOLS = [get_date]


class CustomTool(Tool):
    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        """Convert tool input to pydantic model."""
        args, kwargs = BaseTool._to_args_and_kwargs(self, tool_input)
        # For backwards compatibility. The tool must be run with a single input
        all_args = list(args) + list(kwargs.values())
        if len(all_args) > 1:
            all_args = [json_dumps(all_args)]
        # print(f"_to_args_and_kwargs {self.name=} {all_args=}")
        return tuple(all_args), {}


def get_tools(x: object) -> list[Tool]:
    return [
        CustomTool.from_function(
            func=partial(f, x),
            name=f.__name__,
            description=f.__doc__,
            return_direct=getattr(f, "return_direct", True),
        )
        for f in x.tools
    ]


def get_system_prompt(
    x: BaseAgent,
    stop_sequence: str = SLEEPMATE_STOP_SEQUENCE,
) -> str:
    system = SLEEPMATE_SYSTEM_DESCRIPTION
    if x.goal is not None:
        system = (
            f"{system}{x.goal.description}"
            "Very important! Don't ask the human how you can assist them. "
            "Instead, get to the goal as quickly as possible."
        )
        if stop_sequence:
            system = (
                f"{system} If and only if the human refuses the goal, "
                "output a listening statement followed by "
                f"{stop_sequence} to end the conversation."
            )
        system = (
            f"{system} When the goal is achieved, ask the human to say hey to "
            "let you know when they're ready to continue on their health journey."
        )
    if x.db_user_id is not None:
        db_user = get_user_from_id(x.db_user_id)
        system = (
            f"{system} The human's name is '{db_user.name}'"
            f", and their email is <{db_user.email}>"
        )
    return strip_all_whitespace(system)


def get_template(x: BaseAgent, prompt: str) -> ChatPromptTemplate:
    system = get_system_prompt(x)
    prompt_ = strip_all_whitespace(system + prompt)
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(prompt_),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )


def get_last_human_message(messages: List[BaseMessage]):
    return [m for m in messages if type(m) is HumanMessage][-1]
