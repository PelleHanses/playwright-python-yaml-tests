import importlib
import pkgutil
import inspect
from pathlib import Path

ACTIONS = {}

def load_actions():
    """
    Auto-importerar alla actions från actions-katalogen.
    En action är en funktion som:
      - ligger i actions/*.py
      - inte börjar med _
    """
    package_name = __name__.rsplit(".", 1)[0]
    package_path = Path(__file__).parent

    for module_info in pkgutil.iter_modules([str(package_path)]):
        module_name = module_info.name

        if module_name in ("registry", "__init__"):
            continue

        module = importlib.import_module(f"{package_name}.{module_name}")

        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_"):
                continue

            ACTIONS[name] = obj

    return ACTIONS
