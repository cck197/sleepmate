import os
import pickle
from datetime import date
from functools import partial
from pathlib import Path
from typing import Any

from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory, ReadOnlySharedMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AgentAction
from langchain.tools import Tool

from .audio import play
from .db import *
from .helpful_scripts import (
    display_markdown,
    flatten_list_of_dicts,
    import_attrs,
    set_attribute,
)
from .meta import MetaX
from .user import get_user_from_email

DEBUG = os.environ.get("DEBUG", False)
if DEBUG:
    import langchain

    langchain.verbose = True  # langchain.debug = True

SYSTEM_DESCRIPTION = """
You are an AI clinician skilled in Acceptance and Commitment Therapy and
Motivational Interviewing.
"""

# MAX_TOKENS = 8192

GOALS = [
    {
        "test": """Ask the human their favourite colour.""",
    }
]

model_name = "gpt-4"

SLEEPMATE_MEMORY_PATH = os.environ.get("SLEEPMATE_MEMORY_PATH")


def get_template(goal: str, prompt: str) -> ChatPromptTemplate:
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                f"{SYSTEM_DESCRIPTION}\n{goal}\n{prompt}"
            ),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )


def get_date(word: str) -> date:
    """Returns todays date, use this for any questions related to knowing todays
    date. This function takes any arguments and will always return today's date
    - any date mathematics should occur outside this function."""
    return str(date.today())


def get_tools(funcs, memory: ReadOnlySharedMemory, goal: str) -> list[Tool]:
    tools = [
        Tool.from_function(
            func=partial(f, memory, goal),
            name=f.__name__,
            description=f.__doc__,
            return_direct=getattr(f, "return_direct", True),
        )
        for f in funcs
    ]
    tools.extend(
        [
            Tool(name=t.__name__, func=t, description=t.__doc__, return_direct=False)
            for t in [
                get_date,
            ]
        ]
    )
    return tools


def get_goals() -> list[dict]:
    return flatten_list_of_dicts(import_attrs("GOALS"))


goals = get_goals()


class GoalAchievedHandler(BaseCallbackHandler):
    STOP_SEQUENCE: str = "🚀🚀🚀"

    def __init__(self, callback) -> None:
        super().__init__()
        self.callback = callback

    def on_agent_finish(self, action: AgentAction, **kwargs: Any) -> Any:
        # print(f"on_agent_finish {action}")
        if self.STOP_SEQUENCE in action.return_values["output"]:
            self.callback(action)


class X(object):
    def __init__(self, *args, **kwargs) -> None:
        self.audio = kwargs.pop("audio", False)
        self.display = kwargs.pop("display", True)
        self.hello = kwargs.pop("hello", True)
        self.add_user = kwargs.pop("add_user", True)
        self.db_user = get_user_from_email(kwargs.pop("email", None))
        self.agent_executor = get_agent(*args, **kwargs)
        self.goal_accomplished = False
        self.stop_handler = GoalAchievedHandler(self.set_goal_accomplished)
        if self.hello:
            self("hey")

    def set_goal_accomplished(
        self, action: AgentAction, goal_accomplished: bool = True
    ) -> None:
        self.goal_accomplished = goal_accomplished

    def add_user_to_memory(self) -> None:
        self.agent_executor.memory.chat_memory.add_ai_message("what's your name?")
        self.agent_executor.memory.chat_memory.add_user_message(self.db_user.name)
        self.agent_executor.memory.chat_memory.add_ai_message("what's your email?")
        self.agent_executor.memory.chat_memory.add_user_message(self.db_user.email)

    def __call__(self, utterance: str, save: bool = True) -> bool:
        self.goal_accomplished = False
        if self.add_user:
            self.add_user_to_memory()
            self.add_user = False

        output = self.agent_executor.run(utterance, callbacks=[self.stop_handler])
        # print(output)
        if self.audio:
            play(output)
        if save:
            self.save_memory()
        if self.display:
            display_markdown(output)
        return output

    def save_memory(self, filename: str = SLEEPMATE_MEMORY_PATH) -> None:
        # print(f"save_memory {filename=}")
        with open(filename, "wb") as f:
            pickle.dump(self.agent_executor.memory, f)

    @staticmethod
    def load_memory(
        filename: str = SLEEPMATE_MEMORY_PATH,
        k: int = 50,
        memory_key: str = "chat_history",
    ) -> ConversationBufferWindowMemory:
        if Path(filename).exists():
            print(f"load_memory {filename=}")
            with open(filename, "rb") as f:
                return pickle.load(f)
        return ConversationBufferWindowMemory(
            llm=ChatOpenAI(),
            memory_key=memory_key,
            return_messages=True,
            k=k,
        )


class Runner(object):
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        self.kwargs["memory"] = X.load_memory()

    def run(self):
        self.kwargs["goal"] = None
        while True:
            if self.kwargs["goal"] is None:
                # use the memory (chat_history) to determine the goal
                goal = MetaX(self.kwargs["memory"])()
                goal_ = goals.get(goal)
                if goal_ is not None:
                    self.kwargs["goal"] = goal_
                print(f"X.run {goal=}")
                x = X(*self.args, **self.kwargs)

            utterance = input("> ")
            bot_message = x(utterance)
            print(f"> {bot_message}")
            if x.goal_accomplished:
                self.kwargs["goal"] = None


def get_agent_prompt(
    system_description: str = SYSTEM_DESCRIPTION,
    goal: str = "",
    stop_sequence: str = GoalAchievedHandler.STOP_SEQUENCE,
) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                f"{system_description}\n{goal}"
                "Don't ask the human how you can assist them. "
                "Instead, get to the goal as quickly as possible.\n"
                "Once the above goal is complete, output "
                f"{stop_sequence} to end the conversation."
                if stop_sequence
                else "",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )


def get_agent(goal="", tools=None, memory=None, model_name="gpt-4-0613"):
    if tools is None:
        tools = import_attrs("TOOLS")
    print(f"get_agent len(tools)={len(tools)}")
    if memory is None:
        memory = X.load_memory()
    ro_memory = ReadOnlySharedMemory(memory=memory)
    agent = OpenAIFunctionsAgent(
        llm=ChatOpenAI(temperature=0, model=model_name),
        tools=get_tools(tools, ro_memory, goal),
        prompt=get_agent_prompt(goal),
    )
    return AgentExecutor(agent=agent, tools=agent.tools, memory=memory)
