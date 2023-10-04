from functools import partial

from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory, ReadOnlySharedMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.callbacks.base import BaseCallbackHandler

from typing import Any
from langchain.schema import AgentAction

from .tools import TOOLS

TEST_GOAL_PROMPTS = [
    """Ask the human their favourite colour.""",
]


def get_tools(funcs, memory: ReadOnlySharedMemory) -> list[Tool]:
    return [
        Tool.from_function(
            func=partial(f, memory),
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
        self.agent_executor = get_agent(*args, **kwargs)
        self.goal_accomplished = False
        self.stop_handler = GoalAchievedHandler(self.set_goal_accomplished)

    def set_goal_accomplished(self, action: AgentAction, goal_accomplished: bool = True) -> None:
        self.goal_accomplished = goal_accomplished

    def __call__(self, utterance: str) -> bool:
        print(self.agent_executor.run(utterance, callbacks=[self.stop_handler]))
        return self.goal_accomplished


def get_agent(
    system_description,
    goal,
    tools=TOOLS,
    memory=None,
    model_name="gpt-4-0613",
    memory_key="chat_history",
    stop_sequence=GoalAchievedHandler.STOP_SEQUENCE):
    if memory is None:
        memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
        memory.save_context({"input": "what's your goal?"}, {"output": goal})
    ro_memory = ReadOnlySharedMemory(memory=memory)
    tools = get_tools(tools, ro_memory)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                f"{system_description}"
                "Greet the human by asking how they're feeling."
                "Ask their name if you don't know it."
                f"{goal}"
                f"Once the above goal is complete, output {stop_sequence} to end the conversation." if stop_sequence else "",
            ),
            MessagesPlaceholder(variable_name=memory_key),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
    agent = OpenAIFunctionsAgent(
        llm=ChatOpenAI(temperature=0, model=model_name),
        tools=tools,
        prompt=prompt,
    )
    return AgentExecutor(agent=agent, tools=tools, memory=memory)
