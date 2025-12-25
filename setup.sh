#!/bin/bash

python3 -m venv mytestenv

source mytestenv/bin/activate

pip install playwright
playwright install
playwright install chromium
playwright install firefox
playwright install webkit
pip install argparse



