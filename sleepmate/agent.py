import os
import pickle
from functools import partial
from pathlib import Path

import langchain
from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.tools import Tool

langchain.verbose = True  # langchain.debug = True
from typing import Any

from langchain.schema import AgentAction

from .audio import play
from .helpful_scripts import flatten_list_of_dicts, import_attrs

GOALS = [
    {
        "test": """Ask the human their favourite colour.""",
    }
]

model_name = "gpt-4"

SLEEPMATE_MEMORY_PATH = os.environ.get("SLEEPMATE_MEMORY_PATH")


def get_tools(funcs, memory: ReadOnlySharedMemory, goal: str) -> list[Tool]:
    return [
        Tool.from_function(
            func=partial(f, memory, goal),
            name=f.__name__,
            description=f.__doc__,
            return_direct=True,
        )
        for f in funcs
    ]


def get_goals() -> list[dict]:
    return flatten_list_of_dicts(import_attrs("GOALS"))


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
        self.agent_executor = get_agent(*args, **kwargs)
        self.goal_accomplished = False
        self.stop_handler = GoalAchievedHandler(self.set_goal_accomplished)

    def set_goal_accomplished(
        self, action: AgentAction, goal_accomplished: bool = True
    ) -> None:
        self.goal_accomplished = goal_accomplished

    def __call__(self, utterance: str, save: bool = True) -> bool:
        output = self.agent_executor.run(utterance, callbacks=[self.stop_handler])
        print(output)
        if self.audio:
            play(output)
        if save:
            self.save_memory()
        return self.goal_accomplished

    def save_memory(self, filename: str = SLEEPMATE_MEMORY_PATH) -> None:
        # print(f"save_memory {filename=}")
        with open(filename, "wb") as f:
            pickle.dump(self.agent_executor.memory, f)

    @staticmethod
    def load_memory(filename: str = SLEEPMATE_MEMORY_PATH) -> ConversationBufferMemory:
        if Path(filename).exists():
            print(f"load_memory {filename=}")
            with open(filename, "rb") as f:
                return pickle.load(f)
        return ConversationBufferMemory(memory_key="chat_history", return_messages=True)


def get_agent_prompt(
    system_description: str,
    goal: str = "",
    stop_sequence: str = GoalAchievedHandler.STOP_SEQUENCE,
) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                f"{system_description}\n"
                "Your goals is below surrounded by triple backticks:"
                f"```{goal}```\n"
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


def get_agent(
    system_description, goal="", tools=None, memory=None, model_name="gpt-4-0613"
):
    if tools is None:
        tools = import_attrs("TOOLS")
    print(f"get_agent len(tools)={len(tools)}")
    if memory is None:
        memory = X.load_memory()
    ro_memory = ReadOnlySharedMemory(memory=memory)
    agent = OpenAIFunctionsAgent(
        llm=ChatOpenAI(temperature=0, model=model_name),
        tools=get_tools(tools, ro_memory, goal),
        prompt=get_agent_prompt(system_description, goal),
    )
    return AgentExecutor(agent=agent, tools=agent.tools, memory=memory)
