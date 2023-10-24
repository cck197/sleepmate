from datetime import date
from functools import partial
from typing import Any, Dict, List, Tuple, Union

from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.memory import (
    ConversationBufferWindowMemory,
    MongoDBChatMessageHistory,
    ReadOnlySharedMemory,
)
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
    SLEEPMATE_MONGODB_CONNECTION_STRING,
    SLEEPMATE_SAMPLING_TEMPERATURE,
    SLEEPMATE_STOP_SEQUENCE,
)
from .db import *
from .goal import add_goal_refused
from .helpful_scripts import (
    Goal,
    display_markdown,
    find_human_messages,
    flatten_dict,
    get_system_prompt,
    import_attrs,
    json_dumps,
    set_attribute,
)
from .user import get_user_from_email


@set_attribute("return_direct", False)
def get_date(*args, **kwargs):
    """Returns todays date, use this for any questions related to knowing todays
    date. This function takes any arguments and will always return today's date
    - any date mathematics should occur outside this function."""
    return str(date.today())


TOOLS = [get_date]


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


def get_tools(funcs, memory: ReadOnlySharedMemory, goal: Goal) -> list[Tool]:
    return [
        CustomTool.from_function(
            func=partial(f, memory, goal),
            name=f.__name__,
            description=f.__doc__,
            return_direct=getattr(f, "return_direct", True),
        )
        for f in funcs
    ]


class GoalRefusedHandler(BaseCallbackHandler):
    def __init__(self, callback) -> None:
        super().__init__()
        self.callback = callback

    def on_agent_finish(self, action: AgentAction, **kwargs: Any) -> Any:
        # print(f"on_agent_finish {action}")
        if SLEEPMATE_STOP_SEQUENCE in action.return_values["output"]:
            self.callback(action)


class X(object):
    DEFAULT_GOAL_LIST = [
        "health_history",
        "insomnia_severity_index",
        "diary_entry",
        "daily_routine",
        "stimulus_control",
        "stress_audit",
        "seeds_probe",
        "seeds_entry",
        "open_focus",
        "leaves_on_a_stream",
        "valued_living",
        "all_for_now",
    ]

    def __init__(
        self,
        goal: str = "",
        audio: bool = False,
        display: bool = True,
        hello: str = "",
        add_user: bool = True,
        email: str = None,
        goal_list: List[str] = None,
        fixed_goal: bool = False,
    ) -> None:
        self.fixed_goal = False
        self.goal_list = goal_list or X.DEFAULT_GOAL_LIST
        self.memory = None
        self.tools = import_attrs(["TOOLS"])["TOOLS"]
        print(f"X() len(self.tools)={len(self.tools)}")
        self.goals = flatten_dict(import_attrs(["GOALS", "GOAL_HANDLERS"]))
        assert set(self.goal_list).issubset(set(self.goals["GOAL_HANDLERS"].keys()))

        self.audio = audio
        self.display = display
        self.add_user = add_user
        self.db_user = get_user_from_email(email)
        self.goal_refused = False
        self.stop_handler = GoalRefusedHandler(self.set_goal_refused)
        self.fixed_goal = fixed_goal
        self.goal = None
        if goal:
            self.goal = Goal(key=goal, description=self.goals["GOALS"][goal])
        self.load_memory()
        self.set_agent()
        if hello is not None:
            self.say(hello)

    def get_next_goal(self) -> str:
        """Returns the next goal. Calls a function in each of the goal modules
        in a predefined order and return the first goal that returns True."""
        if self.fixed_goal:
            return self.goal

        goal = next(
            (goal_ for goal_ in self.goal_list if self.goals["GOAL_HANDLERS"][goal_]()),
            "",
        )
        return Goal(key=goal, description=self.goals["GOALS"][goal]) if goal else None

    def set_agent(self):
        # the model is fine tuned for selecting a function
        # sampling temperature is set to 0 (no sampling)
        # goal = self.goals["GOALS"][self.goal] if self.goal else None
        agent = OpenAIFunctionsAgent(
            llm=ChatOpenAI(temperature=0, model=SLEEPMATE_AGENT_MODEL_NAME),
            tools=get_tools(self.tools, self.ro_memory, self.goal),
            prompt=self.get_agent_prompt(),
        )
        self.agent_executor = AgentExecutor(
            agent=agent, tools=agent.tools, memory=self.memory
        )

    def set_goal_refused(self, action: AgentAction, goal_refused: bool = True) -> None:
        self.goal_refused = goal_refused
        if goal_refused:
            add_goal_refused(self.goal.key)

    def __call__(self, *args, **kwargs) -> bool:
        return self.say(*args, **kwargs)

    def say(self, utterance: str = "", save: bool = True) -> bool:
        self.goal_refused = False
        goal = self.get_next_goal()
        if not utterance:
            utterance = goal.key
        if goal != self.goal:
            print(f"X.say {self.goal} -> {goal}")
            # print(f"X.__call__ {goal=}")
            self.goal = goal
            self.set_agent()

        output = self.agent_executor.run(
            input=utterance,
            # name=self.db_user.name,
            # email=self.db_user.email,
            callbacks=[self.stop_handler],
        )
        # print(output)
        if self.audio:
            play(output)
        if self.display:
            display_markdown(output)
        return output

    def load_memory(
        self,
        k: int = 10,
        memory_key: str = "chat_history",
    ) -> None:
        self.memory = ConversationBufferWindowMemory(
            llm=ChatOpenAI(
                temperature=SLEEPMATE_SAMPLING_TEMPERATURE,
                model_name=SLEEPMATE_DEFAULT_MODEL_NAME,
            ),
            memory_key=memory_key,
            return_messages=True,
            k=k,
            chat_memory=MongoDBChatMessageHistory(
                SLEEPMATE_MONGODB_CONNECTION_STRING,
                self.db_user.id,
                database_name=SLEEPMATE_MONGODB_NAME,
            ),
        )
        self.ro_memory = ReadOnlySharedMemory(memory=self.memory)

    def delete_chat_history(self, N=10):
        """Delete the last N chat history entries."""
        collection = self.memory.chat_memory.collection
        cursor = collection.find().sort([("_id", -1)]).limit(N)
        ids_to_delete = [doc["_id"] for doc in cursor]
        collection.delete_many({"_id": {"$in": ids_to_delete}})

    def get_agent_prompt(self, rigid=False) -> ChatPromptTemplate:
        system = get_system_prompt(self.goal, user=self.db_user)
        messages = [
            SystemMessagePromptTemplate.from_template(system),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        # nuclear option - set the goal as a system message, thus overriding the
        # agent's prediction of what to do next
        if rigid:
            messages.insert(
                -1, SystemMessagePromptTemplate.from_template(str(self.goal))
            )

        return ChatPromptTemplate.from_messages(messages)
