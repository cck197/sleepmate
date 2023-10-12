import importlib
import json
from datetime import datetime
from pathlib import Path

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
