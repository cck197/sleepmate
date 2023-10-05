import importlib
from pathlib import Path


def import_tools(dir=None):
    if dir is None:
        dir = Path(__file__).parent
    all_tools = []
    # print(f"{dir=}")
    for p in dir.glob("*.py"):
        try:
            import_path = f"{dir.name}.{p.stem}"
            # print(f"{import_path=}")
            all_tools.extend(importlib.import_module(import_path).TOOLS)
        except AttributeError as e:
            # print(f"import_tools {e=}")
            continue
    return all_tools
