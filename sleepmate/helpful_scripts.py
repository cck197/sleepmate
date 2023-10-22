import importlib
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from dateutil.parser import ParserError
from dateutil.parser import parse as date_parser
from IPython.display import Markdown, display
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage

from .config import SLEEPMATE_STOP_SEQUENCE, SLEEPMATE_SYSTEM_DESCRIPTION


def display_markdown(text: str) -> None:
    """Display markdown in Jupyter Notebooks."""
    display(Markdown(text))


def set_attribute(attr_name, attr_value):
    def decorator(func):
        setattr(func, attr_name, attr_value)
        return func

    return decorator


def json_dumps(d: object) -> str:
    return json.dumps(
        d, default=lambda o: o.isoformat() if isinstance(o, datetime) else o
    )


def mongo_to_json(entry: dict) -> str:
    for k in ("_id", "user"):
        entry.pop(k, None)
    return json_dumps(entry)


def import_attrs(attrs: List[str], dir: str = None) -> dict:
    """Import all the attributes from all the .py files in dir. Return a list of
    all the attributes with the given name."""
    if dir is None:
        dir = Path(__file__).parent
    imported = defaultdict(list)
    # print(f"{dir=}")
    for p in dir.glob("*.py"):
        try:
            import_path = f"{dir.name}.{p.stem}"
            # print(f"{import_path=}")
            for attr in attrs:
                imported[attr].extend(
                    getattr(importlib.import_module(import_path), attr)
                )
        except AttributeError as e:
            # print(f"import_attrs {e=}")
            continue
    return imported


def flatten_list_of_dicts(dicts_list):
    result = {}
    for d in dicts_list:
        result.update(d)
    return result


def flatten_dict(d):
    result = {}
    for k, v in d.items():
        result[k] = flatten_list_of_dicts(v)
    return result


def flatten_list(lst):
    return [
        item
        for sublist in lst
        for item in (sublist if isinstance(sublist, list) else [sublist])
    ]


def get_date_fields(cls):
    return [f.name for f in cls.__fields__.values() if f.type_ == datetime]


def parse_date(date: str, default_days=0) -> datetime:
    """Parse a date string."""
    try:
        # print(f"parse_date {date=}")
        return date_parser(date)
    except ParserError:
        return datetime.now() - timedelta(days=default_days)


def get_start_end(date: datetime = None) -> (datetime, datetime):
    """Return the start and end of a day."""
    if date is None:
        date = datetime.now()
    return (
        datetime(
            year=date.year, month=date.month, day=date.day, hour=0, minute=0, second=0
        ),
        datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=23,
            minute=59,
            second=59,
        ),
    )


@dataclass
class Goal:
    key: str
    description: str

    def __eq__(self, other):
        if not isinstance(other, Goal):
            return False
        return self.key == other.key

    def __repr__(self) -> str:
        return self.key


def get_system_prompt(
    goal: Goal,
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
            f"{system}\nWhen the goal is achieved, ask the human to "
            "let you know when they're ready to continue on their health journey."
        )
    return system


def get_template(goal: Goal, prompt: str) -> ChatPromptTemplate:
    system = get_system_prompt(goal)
    return ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(f"{system}\n{prompt}"),
            # The `variable_name` here is what must align with memory
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{input}"),
        ]
    )


def find_human_messages(messages, queries):
    """Find the human messages that follow the given queries."""
    # queries = ["what's your name?", "what's your email?"]
    results = {}
    for query in queries:
        for i, msg in enumerate(messages):
            if isinstance(msg, AIMessage) and msg.content == query:
                if i + 1 < len(messages) and isinstance(messages[i + 1], HumanMessage):
                    results[query] = messages[i + 1].content
                    break
    return results
