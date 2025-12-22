#!/bin/bash

python3 -m venv mytestenv

source mytestenv/bin/activate

pip install playwright
playwright install
pip install argparse



