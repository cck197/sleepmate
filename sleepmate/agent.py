import pickle
from datetime import date
from functools import partial
from pathlib import Path
from typing import Any, Dict, Tuple, Union

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
from langchain.tools import BaseTool, Tool

from .audio import play
from .config import (
    SLEEPMATE_AGENT_MODEL_NAME,
    SLEEPMATE_DEFAULT_MODEL_NAME,
    SLEEPMATE_MEMORY_PATH,
    SLEEPMATE_SAMPLING_TEMPERATURE,
    SLEEPMATE_SYSTEM_DESCRIPTION,
)
from .db import *
from .goal import set_goal_refused
from .helpful_scripts import display_markdown, flatten_dict, import_attrs, json_dumps
from .user import get_user_from_email

GOALS = [
    {
        "test": """Your goal is to find out the human's favourite colour.""",
    }
]


def get_date(*args, **kwargs) -> date:
    """Returns todays date, use this for any questions related to knowing todays
    date. This function takes any arguments and will always return today's date
    - any date mathematics should occur outside this function."""
    return str(date.today())


class CustomTool(Tool):
    def _to_args_and_kwargs(self, tool_input: Union[str, Dict]) -> Tuple[Tuple, Dict]:
        """Convert tool input to pydantic model."""
        args, kwargs = BaseTool._to_args_and_kwargs(self, tool_input)
        # For backwards compatibility. The tool must be run with a single input
        all_args = list(args) + list(kwargs.values())
        if len(all_args) > 1:
            all_args = [json_dumps(all_args)]
        # import pdb

        # pdb.set_trace()
        print(f"_to_args_and_kwargs {self.name=} {all_args=}")
        return tuple(all_args), {}


def get_tools(funcs, memory: ReadOnlySharedMemory, goal: str) -> list[Tool]:
    tools = [
        CustomTool.from_function(
            func=partial(f, memory, goal),
            name=f.__name__,
            description=f.__doc__,
            return_direct=getattr(f, "return_direct", True),
        )
        for f in funcs
    ]
    tools.extend(
        [
            CustomTool(
                name=t.__name__, func=t, description=t.__doc__, return_direct=False
            )
            for t in [
                get_date,
            ]
        ]
    )
    return tools


class GoalRefusedHandler(BaseCallbackHandler):
    STOP_SEQUENCE: str = "🛑🛑🛑"

    def __init__(self, callback) -> None:
        super().__init__()
        self.callback = callback

    def on_agent_finish(self, action: AgentAction, **kwargs: Any) -> Any:
        # print(f"on_agent_finish {action}")
        if self.STOP_SEQUENCE in action.return_values["output"]:
            self.callback(action)


class X(object):
    def __init__(
        self,
        goal: str = "",
        audio: bool = False,
        display: bool = True,
        hello: bool = True,
        add_user: bool = True,
        email: str = None,
    ) -> None:
        self.fixed_goal = False
        self.memory = None
        self.tools = import_attrs(["TOOLS"])["TOOLS"]
        print(f"X() len(self.tools)={len(self.tools)}")
        self.goals = flatten_dict(import_attrs(["GOALS", "GOAL_HANDLERS"]))

        self.audio = audio
        self.display = display
        self.hello = hello
        self.add_user = add_user
        self.db_user = get_user_from_email(email)
        self.goal_refused = False
        self.stop_handler = GoalRefusedHandler(self.set_goal_refused)
        if goal:
            self.goal = self.goals["GOALS"][goal]
            self.fixed_goal = True
            self.set_agent()
        else:
            self.goal = ""
        if self.hello:
            self("hey")

    def get_next_goal(self) -> str:
        """Returns the next goal. Calls a function in each of the goal modules
        in a predefined order and return the first goal that returns True."""
        if self.fixed_goal:
            return self.goal

        goal_list = [
            "health_history",
            "insomnia_severity_index",
            "diary_probe",
        ]
        goal = ""
        for goal_ in goal_list:
            if self.goals["GOAL_HANDLERS"][goal_]():
                goal = goal_
                break

        print(f"X.get_next_goal {goal=}")
        return goal

    def set_agent(self):
        if self.memory is None:
            self.memory = X.load_memory()
            self.ro_memory = ReadOnlySharedMemory(memory=self.memory)
            self.add_user_to_memory()

        # the model is fine tuned for selecting a function
        # sampling temperature is set to 0 (no sampling)
        agent = OpenAIFunctionsAgent(
            llm=ChatOpenAI(temperature=0, model=SLEEPMATE_AGENT_MODEL_NAME),
            tools=get_tools(self.tools, self.ro_memory, self.goal),
            prompt=get_agent_prompt(self.goals["GOALS"][self.goal]),
        )
        self.agent_executor = AgentExecutor(
            agent=agent, tools=agent.tools, memory=self.memory
        )

    def set_goal_refused(self, action: AgentAction, goal_refused: bool = True) -> None:
        self.goal_refused = goal_refused
        if goal_refused:
            set_goal_refused(self.goal)

    def add_user_to_memory(self) -> None:
        if self.add_user:
            self.memory.chat_memory.add_ai_message("what's your name?")
            self.memory.chat_memory.add_user_message(self.db_user.name)
            self.memory.chat_memory.add_ai_message("what's your email?")
            self.memory.chat_memory.add_user_message(self.db_user.email)
            # TODO what happens when this falls off the end of the chat history?
            self.add_user = False

    def __call__(self, utterance: str, save: bool = True) -> bool:
        self.goal_refused = False
        goal = self.get_next_goal()
        if goal != self.goal:
            # print(f"X.__call__ {goal=}")
            self.goal = goal
            self.set_agent()

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
        k: int = 30,
        memory_key: str = "chat_history",
    ) -> ConversationBufferWindowMemory:
        if Path(filename).exists():
            print(f"X.load_memory {filename=}")
            with open(filename, "rb") as f:
                return pickle.load(f)
        return ConversationBufferWindowMemory(
            llm=ChatOpenAI(
                temperature=SLEEPMATE_SAMPLING_TEMPERATURE,
                model_name=SLEEPMATE_DEFAULT_MODEL_NAME,
            ),
            memory_key=memory_key,
            return_messages=True,
            k=k,
        )


def get_agent_prompt(
    goal: str = "",
    stop_sequence: str = GoalRefusedHandler.STOP_SEQUENCE,
) -> ChatPromptTemplate:
    system = SLEEPMATE_SYSTEM_DESCRIPTION
    if goal:
        system = (
            f"{system}\n{goal}\n"
            "Don't ask the human how you can assist them. "
            "Instead, get to the goal as quickly as possible.\n"
        )
        if stop_sequence:
            system = (
                f"{system}\nIf the human refuses the goal, "
                "output a listening statement followed by "
                f"{stop_sequence} to end the conversation."
            )
    return ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(system),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
