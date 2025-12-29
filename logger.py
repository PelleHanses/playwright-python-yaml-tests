#!/usr/bin/env python3

import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logger():
    logger = logging.getLogger("runner")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(LOG_DIR / "runner.log")
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
