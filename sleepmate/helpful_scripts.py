import importlib
import json
from datetime import datetime, timedelta
from pathlib import Path

from dateutil.parser import ParserError
from dateutil.parser import parse as date_parser
from IPython.display import Markdown, display


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


def import_attrs(attr: str, dir: str = None) -> list:
    """Import all the attributes from all the .py files in dir. Return a list of
    all the attributes with the given name."""
    if dir is None:
        dir = Path(__file__).parent
    attrs = []
    # print(f"{dir=}")
    for p in dir.glob("*.py"):
        try:
            import_path = f"{dir.name}.{p.stem}"
            # print(f"{import_path=}")
            attrs.extend(getattr(importlib.import_module(import_path), attr))
        except AttributeError as e:
            # print(f"import_attrs {e=}")
            continue
    return attrs


def flatten_list_of_dicts(dicts_list):
    result = {}
    for d in dicts_list:
        result.update(d)
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
