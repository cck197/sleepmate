from functools import partial
import pickle

from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import ReadOnlySharedMemory
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)

from typing import Any
from langchain.schema import AgentAction

from .tools import import_tools
from .audio import play

TEST_GOAL_PROMPTS = [
    """Ask the human their favourite colour.""",
]

model_name = "gpt-4"

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

class GoalAchievedHandler(BaseCallbackHandler):
    STOP_SEQUENCE: str = "🚀🚀🚀"

    def __init__(self, callback) -> None:
        super().__init__()
        self.callback = callback

    def on_agent_finish(self, action: AgentAction, **kwargs: Any) -> Any:
            #print(f"on_agent_finish {action}")
            if self.STOP_SEQUENCE in action.return_values["output"]:
                 self.callback(action)


class X:
    def __init__(self, *args, **kwargs) -> None:
        self.audio = kwargs.pop("audio", False)
        self.agent_executor = get_agent(*args, **kwargs)
        self.goal_accomplished = False
        self.stop_handler = GoalAchievedHandler(self.set_goal_accomplished)

    def set_goal_accomplished(self, action: AgentAction, goal_accomplished: bool = True) -> None:
        self.goal_accomplished = goal_accomplished

    def __call__(self, utterance: str) -> bool:
        output = self.agent_executor.run(utterance, callbacks=[self.stop_handler])
        print(output)
        if self.audio:
            play(output)
        return self.goal_accomplished
    
    def save_memory(self, filename):
        with open(filename, "wb") as f:
            pickle.dump(self.agent_executor.memory, f)

    @staticmethod
    def load_memory(filename):
        with open(filename, "rb") as f:
            return pickle.load(f)


def get_agent(
    system_description,
    goal="",
    tools=None,
    memory=None,
    model_name="gpt-4-0613",
    memory_key="chat_history",
    stop_sequence=GoalAchievedHandler.STOP_SEQUENCE):
    if tools is None:
        tools = import_tools()
    print(f"get_agent len(tools)={len(tools)}")
    if memory is None:
        memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
    ro_memory = ReadOnlySharedMemory(memory=memory)
    tools = get_tools(tools, ro_memory, goal)
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(
                f"{system_description}"
                f"{goal}"
                f"Once the above goal is complete, output {stop_sequence} to end the conversation." if stop_sequence else "",
            ),
            MessagesPlaceholder(variable_name=memory_key),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = OpenAIFunctionsAgent(
        llm=ChatOpenAI(temperature=0, model=model_name),
        tools=tools,
        prompt=prompt,
    )
    return AgentExecutor(agent=agent, tools=tools, memory=memory)
