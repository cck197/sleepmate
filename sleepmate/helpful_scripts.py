import importlib
import json
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

import coloredlogs
from dateutil.parser import ParserError
from dateutil.parser import parse as date_parser
from IPython.display import Markdown, display
from rich.console import Console
from rich.markdown import Markdown as RichMarkdown

from .config import SLEEPMATE_CONFIRMATION_WORDS


def timedelta_in_years(td):
    return td.days / 365.25


def strip_all_whitespace(s: str, replacement: str = " ") -> str:
    return re.sub(r"\s+", replacement, s)


def get_delay(base: int, n: int) -> int:
    return base ** (1 + n / 10.0)


def setup_logging(log_level=logging.INFO):
    fmt = "{asctime} {levelname:<8} {name} {message}"
    datefmt = "%Y-%m-%d %H:%M:%S"
    coloredlogs.install(level=log_level, fmt=fmt, datefmt=datefmt, style="{")


def get_confirmation_str():
    return '"{}"'.format('", "'.join(SLEEPMATE_CONFIRMATION_WORDS))


def display_markdown(text: str) -> None:
    """Display markdown in Jupyter Notebooks."""
    display(Markdown(text))


def display_rich_markdown(text: str) -> None:
    """Display markdown in console."""
    markdown = RichMarkdown(text)

    console = Console()
    console.print(markdown)


def set_attribute(attr_name, attr_value):
    def decorator(func):
        setattr(func, attr_name, attr_value)
        return func

    return decorator


def json_dumps(d: object) -> str:
    return json.dumps(
        d, default=lambda o: o.isoformat() if isinstance(o, datetime) else o
    )


def json_loads(s: str) -> object:
    return json.loads(s)


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
