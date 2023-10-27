from typing import List

from langchain.memory import ReadOnlySharedMemory
from langchain.schema import BaseMessage

from .helpful_scripts import Goal


class BaseAgent(object):
    db_user_id: str = None
    goal: Goal = None
    ro_memory: ReadOnlySharedMemory = None

    def get_latest_messages(self) -> List[List[BaseMessage]]:
        assert False, "Must implement get_latest_messages"
