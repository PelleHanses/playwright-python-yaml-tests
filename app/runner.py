#!/usr/bin/env python3
import argparse
import yaml
from datetime import datetime
from pathlib import Path
import importlib
import inspect
 
from playwright.sync_api import sync_playwright
from logger import setup_logger
from metric import write_test_metric
 
logger = setup_logger()
 
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
    logger.error(
        f"\n=== STEP FAILED ===\n"
        f"Step         : {step_name}\n"
        f"Exception    : {exception}\n"
        f"Expected URL : {expected_url or 'N/A'}\n"
        f"Current URL  : {current_url}\n"
        f"URL history  :\n" +
        "\n".join(f"  - {u}" for u in url_history) +
        "\n=================="
    )
 
# --- Run a single test ---
def run_test(test, browser_name, headless):
    print(f"\n=== Running test: {test['name']} ({browser_name}) ===")
    success = True
    url_history = []
 
    with sync_playwright() as p:
        if browser_name.lower() == "chromium":
            # Lägg till fake media, fil för kamera, auto-grant permissions
            args = [
                "--use-fake-ui-for-media-stream",
                "--use-fake-device-for-media-stream",
                "--use-file-for-fake-video-capture=test.y4m"  # din testfilm
            ]
            browser = p.chromium.launch(headless=headless)
        elif browser_name.lower() == "firefox":
            browser = p.firefox.launch(headless=headless)
        elif browser_name.lower() == "safari":
            browser = p.webkit.launch(headless=headless)
        else:
            browser = p.chromium.launch(headless=headless)
        # Permissions för kamera och mikrofon
        context = browser.new_context(
            permissions=["camera", "microphone"]
        )
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
                    kwargs["logger"] = logger
                if "url_history" in sig.parameters:
                    kwargs["url_history"] = url_history
 
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
    # Create logger
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
        test_success = True
 
        browsers = [args.browser] if args.browser != "all" else ["Chromium", "Firefox", "Safari"]
        for browser_name in browsers:
            if not run_test(test, browser_name, headless):
                test_success = False
                failed += 1
            else:
                passed += 1
 
        # 🔥 Skriv Prometheus-metric (trunkerar filen)
        write_test_metric(
            test_name=test["name"],
            success=test_success
        )
 
 
    print("\n=== TEST SUMMARY ===")
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
 
if __name__ == "__main__":
    main()
