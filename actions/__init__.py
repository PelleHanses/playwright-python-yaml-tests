# actions/__init__.py
import os
import importlib
from pathlib import Path

ACTIONS = {}

# Hitta alla .py-filer i samma katalog (förutom __init__.py)
actions_dir = Path(__file__).parent
for f in actions_dir.glob("*.py"):
    if f.name == "__init__.py" or f.suffix != ".py":
        continue

    module_name = f.stem
    module = importlib.import_module(f"actions.{module_name}")

    # Lägg in alla funktioner i ACTIONS-dict
    for attr in dir(module):
        if callable(getattr(module, attr)):
            ACTIONS[attr] = getattr(module, attr)
