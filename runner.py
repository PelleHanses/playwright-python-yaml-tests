#!/usr/bin/env python3
import argparse
import yaml
import logging
from datetime import datetime
from pathlib import Path
import importlib
import inspect
from playwright.sync_api import sync_playwright

# --- Setup logging ---
log_dir = Path("log")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# --- Metrics ---
metrics_dir = Path("metrics")
metrics_dir.mkdir(exist_ok=True)
prom_file = metrics_dir / "test_metrics.prom"

# --- Dynamically load all actions from actions/ ---
actions = {}
actions_dir = Path("actions")
for py_file in actions_dir.glob("*.py"):
    module_name = py_file.stem
    module = importlib.import_module(f"actions.{module_name}")
    for name, func in inspect.getmembers(module, inspect.isfunction):
        actions[name] = func

# --- Helper: log errors nicely ---
def log_error_step(step_name, exception, current_url, url_history, expected_url=None):
    logging.error(
        f"\n=== STEP FAILED ===\n"
        f"Step         : {step_name}\n"
        f"Exception    : {exception}\n"
        f"Expected URL : {expected_url or 'N/A'}\n"
        f"Current URL  : {current_url}\n"
        f"URL history  :\n" + "\n".join(f"  - {u}" for u in url_history) + "\n"
        f"=================="
    )

# --- Run a single test ---
def run_test(test, browser_name, headless):
    print(f"\n=== Running test: {test['name']} ({browser_name}) ===")
    success = True
    url_history = []

    with sync_playwright() as p:
        if browser_name.lower() == "chromium":
            browser = p.chromium.launch(headless=headless)
        elif browser_name.lower() == "firefox":
            browser = p.firefox.launch(headless=headless)
        elif browser_name.lower() == "safari":
            browser = p.webkit.launch(headless=headless)
        else:
            browser = p.chromium.launch(headless=headless)

        context = browser.new_context()
        page = context.new_page()

        # Log URL history
        page.on("framenavigated", lambda frame: url_history.append(frame.url) if frame == page.main_frame else None)

        for step in test.get("steps", []):
            action_name, action_params = list(step.items())[0]
            info_text = step.get("info", "")

            if action_name not in actions:
                print(f"[WARN] Action '{action_name}' not found in actions/")
                continue

            action_func = actions[action_name]

            try:
                # Build kwargs based on action signature
                sig = inspect.signature(action_func)
                kwargs = {}
                if "page" in sig.parameters:
                    kwargs["page"] = page
                if "params" in sig.parameters:
                    kwargs["params"] = action_params or {}
                if "logger" in sig.parameters:
                    kwargs["logger"] = logging
                if "url_history" in sig.parameters:
                    kwargs["url_history"] = url_history

                # Call the action
                action_func(**kwargs)

                # Info output
                if info_text:
                    print(f"[INFO] {action_name} : {info_text}")
                else:
                    print(f"[INFO] {action_name} OK")

            except Exception as e:
                current_url = page.url if 'page' in locals() else 'N/A'
                expected_url = action_params.get("expected_url") if action_params else None
                log_error_step(action_name, e, current_url, url_history, expected_url)
                success = False

        browser.close()
    return success

# --- Main ---
def main():
    parser = argparse.ArgumentParser(description="Playwright Test Runner")
    parser.add_argument("-f", "--file", required=True, help="Yaml test file")
    parser.add_argument("-t", "--test", help="Specific test name to run")
    parser.add_argument("--browser", choices=["Chromium", "Firefox", "Safari", "all"], default="Chromium")
    parser.add_argument("--clear-metrics", action="store_true")
    parser.add_argument("--headless", choices=["true", "false"], default="false", help="Run browser in headless mode")
    args = parser.parse_args()

    headless = args.headless.lower() == "true"

    if args.clear_metrics and prom_file.exists():
        prom_file.unlink()

    with open(args.file) as f:
        tests = yaml.safe_load(f)

    total = 0
    passed = 0
    failed = 0
    for test in tests:
        if args.test and test["name"] != args.test:
            continue
        total += 1
        browsers = [args.browser] if args.browser != "all" else ["Chromium", "Firefox", "Safari"]
        for browser_name in browsers:
            if run_test(test, browser_name, headless):
                passed += 1
            else:
                failed += 1

    print("\n=== TEST SUMMARY ===")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    # Write metrics
    with open(prom_file, "a") as f:
        f.write(f"test_passed {passed} {int(datetime.now().timestamp())}\n")
        f.write(f"test_failed {failed} {int(datetime.now().timestamp())}\n")
        f.write(f"test_total {total} {int(datetime.now().timestamp())}\n")

if __name__ == "__main__":
    main()
