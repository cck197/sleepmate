import logging
import warnings
from typing import List

from langchain.agents import AgentExecutor, OpenAIFunctionsAgent
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
from langchain.schema import AgentAction, BaseMessage
from tqdm import TqdmExperimentalWarning

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)
    from tqdm.autonotebook import tqdm

from .agent import BaseAgent
from .audio import play
from .cache import setup_cache
from .config import (
    MONGODB_URI,
    SLEEPMATE_AGENT_MODEL_NAME,
    SLEEPMATE_DEFAULT_MODEL_NAME,
    SLEEPMATE_MEMORY_LENGTH,
    SLEEPMATE_SAMPLING_TEMPERATURE,
)
from .db import *
from .goal import add_goal_refused
from .helpful_scripts import (
    Goal,
    display_markdown,
    flatten_dict,
    import_attrs,
    setup_logging,
)
from .prompt import (
    GoalRefusedHandler,
    MessageHandler,
    get_last_human_message,
    get_system_prompt,
    get_tools,
)
from .user import get_user_from_id, get_user_from_username

log = logging.getLogger(__name__)


class X(BaseAgent):
    DEFAULT_GOAL_LIST = [
        "wearable_probe",
        "whoop_import",
        "meet",
        "health_history",
        "bmi",
        "sleep50",
        "back_pain",  # contingent on back pain in health_history
        "insomnia_severity_index",  # contingent on insomnia in SLEEP-50
        "stop_bang",  # contingent on apnea in SLEEP-50
        "diary_entry",  # contingent on no wearable in wearable_probe
        "whoop_sleep",  # contingent on whoop in wearable_probe
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
        username: str = None,
        goal_list: List[str] = None,
        fixed_goal: bool = False,
        log_: logging.Logger = None,
        cache: bool = False,
    ) -> None:
        if log_ is None:
            setup_logging()
            self.log = log
        else:
            self.log = log_
        if cache:
            setup_cache()
        self.fixed_goal = False
        self.goal_list = goal_list or X.DEFAULT_GOAL_LIST
        self.memory = None
        self.tools = import_attrs(["TOOLS"])["TOOLS"]
        self.log.debug(f"X() len(self.tools)={len(self.tools)}")
        self.goals = flatten_dict(
            import_attrs(["GOALS", "GOAL_HANDLERS", "GOAL_OPTIONS"])
        )
        assert set(self.goal_list).issubset(set(self.goals["GOAL_HANDLERS"].keys()))

        self.audio = audio
        self.display = display
        self.add_user = add_user
        self.db_user_id = get_user_from_username(username).id if username else None
        self.goal_refused = False
        self.callbacks = [
            GoalRefusedHandler(self.set_goal_refused),
            MessageHandler(self.set_chat_model_start),
        ]
        self.fixed_goal = fixed_goal
        self.goal = None
        if goal:
            self.goal = Goal(key=goal, description=self.goals["GOALS"][goal])
        self.load_memory()
        self.set_agent()
        if hello is not None:
            self(hello)

    def get_next_goal(self) -> str:
        """Returns the next goal. Calls a function in each of the goal modules
        in a predefined order and return the first goal that returns True."""
        if self.fixed_goal:
            return self.goal

        goal = next(
            (
                goal_
                for goal_ in self.goal_list
                if self.goals["GOAL_HANDLERS"][goal_](self.db_user_id)
            ),
            "",
        )
        return Goal(key=goal, description=self.goals["GOALS"][goal]) if goal else None

    def set_agent(self):
        agent = OpenAIFunctionsAgent(
            llm=ChatOpenAI(temperature=0, model=SLEEPMATE_AGENT_MODEL_NAME),
            tools=get_tools(self),
            prompt=self.get_agent_prompt(),
        )
        self.agent_executor = AgentExecutor(
            agent=agent, tools=agent.tools, memory=self.memory
        )

    def set_goal_refused(self, action: AgentAction, goal_refused: bool = True) -> None:
        self.goal_refused = goal_refused
        if goal_refused:
            add_goal_refused(self.db_user_id, self.goal.key)

    def __call__(self, *args, **kwargs) -> str:
        return self.run(*args, **kwargs)

    def proceed(self, utterance: str = "") -> Goal:
        """Returns the next goal. If the goal has changed, then the agent is
        reset."""
        self.goal_refused = False
        goal = self.get_next_goal()
        if goal != self.goal:
            self.log.info(f"{self.db_user_id} {self.goal} -> {goal}")
            self.goal = goal
            self.set_agent()
        return goal

    def set_chat_model_start(self, messages: List[List[BaseMessage]]):
        """Save the last message in the chat history as the chat model
        starts."""
        # annoying hack -- when the agent runs a tool to extract an object from
        # the chat history the last message is missing unless the agent
        # summarises the data it just collected, which it doesn't always do
        # if the last message is missing, then the object extraction fails, so
        # save the message here to add to the chat history on extraction.
        self.last_message = get_last_human_message(messages[0])
        log.debug(f"set_chat_model_start: {self.last_message=}")

    def get_latest_messages(self, k: int) -> List[BaseMessage]:
        return self.memory.chat_memory.messages[-k:] + [self.last_message]

    def run(self, utterance: str = "") -> str:
        goal = self.proceed(utterance)
        if not utterance:
            utterance = goal.key
        output = self.agent_executor.run(
            input=utterance,
            callbacks=self.callbacks,
        )
        # print(output)
        if self.audio:
            play(output)
        if self.display:
            display_markdown(output)
        self.clear_old_goal_chat_history()
        return output

    async def arun(self, utterance: str = "") -> str:
        goal = self.proceed(utterance)
        if not utterance:
            utterance = goal.key
        output = await self.agent_executor.arun(
            input=utterance,
            callbacks=self.callbacks,
        )
        self.clear_old_goal_chat_history()
        return output

    def load_memory(
        self,
        k: int = SLEEPMATE_MEMORY_LENGTH,
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
                MONGODB_URI,
                self.db_user_id,
                database_name=MONGODB_NAME,
            ),
        )
        self.ro_memory = ReadOnlySharedMemory(memory=self.memory)

    def clear_old_goal_chat_history(self):
        goal = self.get_next_goal()
        # clear the chat history if the goal has changed
        if self.goal is not None and self.goal != goal:
            log.info(
                f"clear_chat_history: {self.goal} -> {goal} ({self.db_user_id} cleared)"
            )
            self.memory.clear()

    def clear_chat_history_tail(self, N=10):
        """Delete the last N chat history entries."""
        collection = self.memory.chat_memory.collection
        cursor = (
            collection.find({"SessionId": self.db_user_id}).sort([("_id", -1)]).limit(N)
        )
        ids_to_delete = [doc["_id"] for doc in cursor]
        log.info(f"clear_chat_history_tail: deleting {ids_to_delete=}")
        collection.delete_many({"_id": {"$in": ids_to_delete}})

    def clear_db(self):
        clear_db_for_user(self.db_user_id)

    def get_agent_prompt(self, rigid=None) -> ChatPromptTemplate:
        system = get_system_prompt(self.goal, get_user_from_id(self.db_user_id))
        messages = [
            SystemMessagePromptTemplate.from_template(system),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        # nuclear option - set the goal as a system message, thus overriding the
        # agent's prediction of what to do next
        if rigid is None and self.goal:
            rigid = (
                self.goals["GOAL_OPTIONS"].get(self.goal.key, {}).get("rigid", False)
            )
        if rigid:
            messages.insert(
                -1, SystemMessagePromptTemplate.from_template(self.goal.description)
            )

        return ChatPromptTemplate.from_messages(messages)
