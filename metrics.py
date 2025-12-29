from pathlib import Path
import time

METRIC_DIR = Path("metrics")
METRIC_FILE = METRIC_DIR / "playwright.prom"

METRIC_DIR.mkdir(exist_ok=True)

def clear_metrics():
    METRIC_FILE.write_text("")

def write_metric(name, value, labels=None):
    ts = int(time.time())
    label_str = ""

    if labels:
        label_str = "{" + ",".join(
            f'{k}="{v}"' for k, v in labels.items()
        ) + "}"

    with METRIC_FILE.open("a") as f:
        f.write(f"{name}{label_str} {value} {ts}\n")
