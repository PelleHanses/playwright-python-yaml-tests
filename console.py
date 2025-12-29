import sys

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
