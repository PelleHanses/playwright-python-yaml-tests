import sys

class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = LEVEL_COLORS.get(record.levelname, RESET)
        record.levelname = f"{color}{record.levelname}{RESET}"
        return super().format(record)

def info(msg):
    print(f"▶ {msg}")
    sys.stdout.flush()

def step_ok(msg):
    print(f"  ✔ {msg}")
    sys.stdout.flush()

def step_fail(msg):
    print(f"  ✖ {msg}")
    sys.stdout.flush()

def success(msg):
    print(f"✔ {msg}")
    sys.stdout.flush()

def error(msg):
    print(f"✖ {msg}")
    sys.stdout.flush()
