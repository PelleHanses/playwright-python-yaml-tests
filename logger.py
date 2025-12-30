#!/usr/bin/env python3

import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# --- ANSI colors ---
RESET = "\033[0m"
WHITE = "\033[37m"
YELLOW = "\033[33m"
RED = "\033[31m"

LEVEL_COLORS = {
    "INFO": WHITE,
    "WARNING": YELLOW,
    "ERROR": RED,
    "CRITICAL": RED,
}

class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelname, RESET)
        record.levelname = f"{color}{record.levelname}{RESET}"
        return super().format(record)

def setup_logger():
    logger = logging.getLogger("runner")
    logger.setLevel(logging.INFO)

    # ⚠️ Viktigt: undvik dubbla handlers vid flera imports
    if logger.handlers:
        return logger

    # --- File handler (timestamp, no colors) ---
    file_handler = logging.FileHandler(LOG_DIR / "runner.log")
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    file_handler.setFormatter(file_formatter)

    # --- Console handler (colors, no timestamp) ---
    console_handler = logging.StreamHandler()
    console_formatter = ColorFormatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
