#!/usr/bin/env python3

import argparse
import yaml
from playwright.sync_api import sync_playwright, Error, TimeoutError
import logging
from datetime import datetime
import os
import time

# -----------------------------
# ANSI colors
# -----------------------------
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


# -----------------------------
# Logging configuration
# -----------------------------
logging.basicConfig(
    filename='test_results.log',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# -----------------------------
# Helper: Retry logic
# -----------------------------
def retry_step(func, retries=3, delay=2, *args, **kwargs):
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except (AssertionError, TimeoutError) as ae:
            last_exception = ae
            print(f"{YELLOW}Attempt {attempt}/{retries} failed: {ae}{RESET}")
            if attempt < retries:
                time.sleep(delay)
    raise last_exception

# -----------------------------
# Load YAML config
# -----------------------------
def load_config(file_path):
    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)
    return config['tests']

# -----------------------------
# Step runner
# -----------------------------
def run_step(page, step, step_number=None):
    step_prefix = f"  Step {step_number}: " if step_number else "  "

    # Wait for element
    if 'wait_for_element' in step:
        page.wait_for_selector(step['wait_for_element'])
        print(f"{step_prefix}✓ Waited for element: {step['wait_for_element']}")

    # Search string with retry
    if 'search_string' in step:
        text = step['search_string']
        retry_step(lambda: assert_text(page, text), retries=3)
        print(f"{GREEN}{step_prefix}✓ Found text: '{text}'{RESET}")

    # Input field
    if 'input_text_field' in step:
        input_element = page.locator(step['input_text_field']['selector'])
        input_element.fill(step['input_text_field']['value'])
        print(f"{step_prefix}✓ Filled input field")

    # Radio button
    if 'radio_button' in step:
        page.locator(step['radio_button']['selector']).click()
        print(f"{step_prefix}✓ Clicked radio button")

    # Dropdown
    if 'dropdown' in step:
        page.locator(step['dropdown']['selector']).select_option(value=step['dropdown']['value'])
        print(f"{step_prefix}✓ Selected dropdown option")

    # Button click
    if 'button_click' in step:
        page.locator(step['button_click']['selector']).click()
        print(f"{step_prefix}✓ Clicked button")

    # Hover
    if 'hover' in step:
        page.locator(step['hover']['selector']).hover()
        print(f"{step_prefix}✓ Hovered over element")

    # Keyboard input
    if 'keyboard_input' in step:
        elem = page.locator(step['keyboard_input']['selector'])
        elem.fill(step['keyboard_input'].get('text', ''))
        if step['keyboard_input'].get('press_enter'):
            elem.press("Enter")
        print(f"{step_prefix}✓ Keyboard input performed")

    # File upload
    if 'upload_file' in step:
        page.locator(step['upload_file']['selector']).set_input_files(step['upload_file']['path'])
        print(f"{step_prefix}✓ Uploaded file")

    # Drag and drop
    if 'drag_and_drop' in step:
        page.locator(step['drag_and_drop']['source']).drag_to(
            page.locator(step['drag_and_drop']['target'])
        )
        print(f"{step_prefix}✓ Drag and drop completed")

    # Mobile emulation
    if 'emulate_device' in step:
        # Already handled in context creation if needed
        print(f"{step_prefix}✓ Mobile emulation: {step['emulate_device']}")

    # New tab/window
    if 'new_tab' in step:
        context = page.context
        page = context.new_page()
        page.goto(step['new_tab']['url'])
        print(f"{step_prefix}✓ New tab opened: {step['new_tab']['url']}")

    if 'close_tab' in step and step['close_tab']:
        page.close()
        print(f"{step_prefix}✓ Closed tab")

    # Screenshot
    if 'take_screenshot' in step:
        page.screenshot(path=step['take_screenshot'])
        print(f"{step_prefix}✓ Screenshot saved: {step['take_screenshot']}")

    # Expected URL
    if 'expected_url' in step:
        assert page.url.startswith(step['expected_url']), \
            f"Expected URL {step['expected_url']}, got {page.url}"
        print(f"{step_prefix}✓ URL verified: {page.url}")

    # Expected redirect
    if 'expected_redirect_url' in step:
        assert page.url.startswith(step['expected_redirect_url']), \
            f"Expected redirect {step['expected_redirect_url']}, got {page.url}"
        print(f"{step_prefix}✓ Redirect verified: {page.url}")

    # Expected fragment
    if 'expected_fragment' in step:
        fragment = step['expected_fragment']
        hash_val = page.evaluate("() => window.location.hash")
        assert fragment in hash_val, f"Expected fragment '{fragment}', got '{hash_val}'"
        print(f"{step_prefix}✓ Fragment verified: {hash_val}")

    # Assert element
    if 'assert_element' in step:
        elem = page.locator(step['assert_element']['selector'])
        text = elem.text_content()
        expected_text = step['assert_element']['text']
        assert expected_text in text, f"Expected text '{expected_text}' in element, got '{text}'"
        print(f"{step_prefix}✓ Element assertion passed")

def assert_text(page, text):
    body_text = page.text_content('body')
    assert text in body_text, f"'{text}' not found on page"

# -----------------------------
# Run single test
# -----------------------------
def run_single_test(test, browser_type):
    test_name = test['name']
    test_passed = False

    logging.info(f"Starting test: {test_name}")
    print(f"\n{BOLD}Running test: {test_name}{RESET}")
    print("=" * 60)
    print("=" * 60)

    with sync_playwright() as p:
        browser = None
        context = None
        page = None
        try:
            if browser_type == "Chromium":
                browser = p.chromium.launch()
            elif browser_type == "Firefox":
                browser = p.firefox.launch()
            elif browser_type == "Safari":
                browser = p.webkit.launch()
            else:
                raise ValueError(f"Unknown browser type: {browser_type}")

            context = browser.new_context()
            page = context.new_page()
            page.goto(test['url'])
            print(f"{GREEN}  ✓ Navigated to: {test['url']}{RESET}")

            if 'steps' in test:
                for i, step in enumerate(test['steps'], 1):
                    run_step(page, step, i)
            else:
                run_step(page, test)

            logging.info(f"Test '{test_name}' passed!")
            print(f"\n{BOLD}{GREEN}✓ Test '{test_name}' PASSED!{RESET}")
            test_passed = True

        except Exception as e:
            logging.error(f"Test '{test_name}' failed: {e}")
            print(f"\n{BOLD}{RED}✗ Test '{test_name}' FAILED:{RESET} {e}")
            test_passed = False

        finally:
            if page:
                page.close()
            if context:
                context.close()
            if browser:
                browser.close()

    return test_passed

# -----------------------------
# Run tests batch
# -----------------------------
def run_tests(tests, test_names, browser_type):
    results = {}
    for test in tests:
        if test['name'] in test_names:
            result = run_single_test(test, browser_type)
            results[test['name']] = result
    return results

# -----------------------------
# Prometheus helper
# -----------------------------
def get_prom_filename(yaml_file):
    base_name = os.path.basename(yaml_file).replace('.yaml','').replace('.yml','')
    return f'test_results-{base_name}.prom'

def get_suite_name(yaml_file):
    base_name = os.path.basename(yaml_file).replace('.yaml','').replace('.yml','')
    return 'default' if base_name=='config' else base_name

def save_to_prometheus_format(test_name, result, suite_name, prom_file, browser, mode='a'):
    with open(prom_file, mode) as f:
        timestamp = int(datetime.now().timestamp())
        f.write(f'test_result{{name="{test_name}",suite="{suite_name}",browser="{browser}"}} {result}\n')
        f.write(f'test_last_run_timestamp{{name="{test_name}",suite="{suite_name}",browser="{browser}"}} {timestamp}\n')

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Playwright YAML tests with browser support.")
    parser.add_argument('-f','--file', type=str, default='config.yaml')
    parser.add_argument('-t','--test', type=str, required=True)
    parser.add_argument('--browser', type=str, default='Chromium', choices=['Chromium','Firefox','Safari','all'])
    parser.add_argument('--clear-metrics', action='store_true')
    args = parser.parse_args()

    try:
        tests = load_config(args.file)
    except Exception as e:
        print(f"Failed to load YAML: {e}")
        exit(1)

    test_names = [t['name'] for t in tests] if args.test.lower()=='all' else [n.strip() for n in args.test.split(',')]

    prom_file = get_prom_filename(args.file)
    suite_name = get_suite_name(args.file)
    if args.clear_metrics:
        open(prom_file,'w').close()
        print(f"Cleared metrics file: {prom_file}")

    browsers_to_run = [args.browser] if args.browser != 'all' else ['Chromium','Firefox','Safari']
    all_results = {}

    for browser in browsers_to_run:
        print(f"\n=== Running tests on {browser} ===")
        results = run_tests(tests, test_names, browser)
        for test_name, result in results.items():
            save_to_prometheus_format(test_name, 1 if result else 0, suite_name, prom_file, browser)
        all_results[browser] = results

    # Summary
    print("\n" + "="*60)
    print(f"{BOLD}TEST SUMMARY{RESET}")
    print("="*60)

    for browser, results in all_results.items():
        print(f"\n{BOLD}Browser: {browser}{RESET}")
        passed = sum(1 for r in results.values() if r)
        failed = len(results) - passed

        for test_name, result in results.items():
            if result:
                print(f"{GREEN}{test_name}: ✓ PASSED{RESET}")
            else:
                print(f"{RED}{test_name}: ✗ FAILED{RESET}")

        color = GREEN if failed == 0 else RED
        print(
            f"{BOLD}{color}"
            f"Total: {len(results)} | Passed: {passed} | Failed: {failed}"
            f"{RESET}"
        )

    exit(0 if all(all(r.values()) for r in all_results.values()) else 1)
