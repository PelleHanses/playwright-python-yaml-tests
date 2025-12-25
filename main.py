#!/usr/bin/env python3

import argparse
import yaml
from playwright.sync_api import sync_playwright, Error, BrowserType
import logging
from datetime import datetime
import os

# ---------------------------
# Konfigurera loggning
# ---------------------------
logging.basicConfig(filename='test_results.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)

# ---------------------------
# Ladda YAML-konfiguration
# ---------------------------
def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['tests']

# ---------------------------
# Teststeg: modulära funktioner
# ---------------------------
def step_search_string(page, step):
    assert step['search_string'] in page.text_content('body'), \
        f"'{step['search_string']}' not found on the page"
    print(f"  ✓ Found text: '{step['search_string']}'")

def step_input_text(page, step):
    input_element = page.locator(step['input_text_field']['selector'])
    input_element.fill(step['input_text_field']['value'])
    print("  ✓ Filled input field")

def step_radio(page, step):
    radio_element = page.locator(step['radio_button']['selector'])
    radio_element.click()
    print("  ✓ Clicked radio button")

def step_dropdown(page, step):
    dropdown_element = page.locator(step['dropdown']['selector'])
    dropdown_element.select_option(value=step['dropdown']['value'])
    print("  ✓ Selected dropdown option")

def step_button_click(page, step):
    button_element = page.locator(step['button_click']['selector'])
    button_element.click()
    print("  ✓ Clicked button")

def step_wait_for_element(page, step):
    page.wait_for_selector(step['wait_for_element'])
    print(f"  ✓ Element visible: {step['wait_for_element']}")

def step_hover(page, step):
    page.locator(step['hover']).hover()
    print(f"  ✓ Hovered over {step['hover']}")

def step_keyboard_input(page, step):
    page.keyboard.type(step['keyboard_input'])
    print(f"  ✓ Typed: {step['keyboard_input']}")

def step_checkbox_toggle(page, step):
    checkbox = page.locator(step['checkbox_toggle']['selector'])
    checked = step['checkbox_toggle']['check']
    if checked:
        checkbox.check()
    else:
        checkbox.uncheck()
    print(f"  ✓ Checkbox set to {checked}")

def step_take_screenshot(page, step):
    filename = step.get('take_screenshot', 'screenshot.png')
    page.screenshot(path=filename)
    print(f"  ✓ Screenshot saved: {filename}")

def step_drag_and_drop(page, step):
    source = page.locator(step['drag_and_drop']['source'])
    target = page.locator(step['drag_and_drop']['target'])
    source.drag_to(target)
    print(f"  ✓ Dragged {source} -> {target}")

def step_file_upload(page, step):
    page.locator(step['file_upload']['selector']).set_input_files(step['file_upload']['path'])
    print(f"  ✓ Uploaded file: {step['file_upload']['path']}")

def step_assert_element(page, step):
    locator = page.locator(step['assert_element']['selector'])
    expected_text = step['assert_element']['text']
    actual_text = locator.text_content()
    assert expected_text == actual_text, f"Expected '{expected_text}', got '{actual_text}'"
    print(f"  ✓ Element '{step['assert_element']['selector']}' contains '{expected_text}'")

# ---------------------------
# Kör ett steg dynamiskt
# ---------------------------
STEP_MAP = {
    'search_string': step_search_string,
    'input_text_field': step_input_text,
    'radio_button': step_radio,
    'dropdown': step_dropdown,
    'button_click': step_button_click,
    'wait_for_element': step_wait_for_element,
    'hover': step_hover,
    'keyboard_input': step_keyboard_input,
    'checkbox_toggle': step_checkbox_toggle,
    'take_screenshot': step_take_screenshot,
    'drag_and_drop': step_drag_and_drop,
    'file_upload': step_file_upload,
    'assert_element': step_assert_element,
}

def run_step(page, step, step_number=None):
    prefix = f"Step {step_number}:" if step_number else ""
    for key in STEP_MAP:
        if key in step:
            STEP_MAP[key](page, step)
    # Vänta på att sidan laddas klart (för säkerhet)
    page.wait_for_load_state('networkidle')

# ---------------------------
# Kör ett enskilt test
# ---------------------------
def run_single_test(test, browser_type):
    test_name = test['name']
    test_passed = False
    
    logging.info(f"Starting test: {test_name}")
    print(f"\nRunning test: {test_name}")
    print("=" * 60)
    
    with sync_playwright() as p:
        browser = None
        context = None
        page = None
        try:
            browser_launcher = getattr(p, browser_type.lower())
            browser = browser_launcher.launch()
            context = browser.new_context()
            page = context.new_page()

            page.goto(test['url'])
            print(f"  ✓ Navigated to: {test['url']}")

            if 'steps' in test:
                for i, step in enumerate(test['steps'], 1):
                    run_step(page, step, i)
            
            logging.info(f"Test '{test_name}' passed!")
            print(f"\n✓ Test '{test_name}' PASSED!")
            test_passed = True

        except AssertionError as ae:
            logging.error(f"Test '{test_name}' failed: {ae}")
            print(f"\n✗ Test '{test_name}' FAILED: {ae}")
            test_passed = False
        except Exception as e:
            logging.error(f"Test '{test_name}' error: {e}")
            print(f"\n✗ Test '{test_name}' ERROR: {e}")
            test_passed = False
        finally:
            if page: page.close()
            if context: context.close()
            if browser: browser.close()
    
    return test_passed

# ---------------------------
# Kör tester
# ---------------------------
def run_tests(tests, test_names, browsers):
    results = {}
    for browser_type in browsers:
        for test in tests:
            if test['name'] in test_names:
                key = f"{test['name']} [{browser_type}]"
                result = run_single_test(test, browser_type)
                results[key] = result
    return results

# ---------------------------
# Prometheus-format
# ---------------------------
def get_prom_filename(yaml_file):
    base_name = os.path.basename(yaml_file).replace('.yaml', '').replace('.yml', '')
    return f'test_results-{base_name}.prom'

def get_suite_name(yaml_file):
    base_name = os.path.basename(yaml_file).replace('.yaml', '').replace('.yml', '')
    return base_name if base_name != 'config' else 'default'

def save_to_prometheus_format(test_name, result, suite_name, browser_type, prom_file, mode='a'):
    with open(prom_file, mode) as f:
        timestamp = int(datetime.now().timestamp())
        f.write(f'test_result{{name="{test_name}",suite="{suite_name}",browser="{browser_type}"}} {result}\n')
        f.write(f'test_last_run_timestamp{{name="{test_name}",suite="{suite_name}",browser="{browser_type}"}} {timestamp}\n')

# ---------------------------
# Summary
# ---------------------------
def print_summary(results):
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for result in results.values() if result)
    failed = len(results) - passed
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    print("-" * 60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("=" * 60)

# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Playwright tests from YAML config")
    parser.add_argument('-f', '--file', type=str, default='config.yaml')
    parser.add_argument('-t', '--test', type=str, required=True)
    parser.add_argument('--browser', type=str, default='Chromium', 
                        help='Browser to use: Chromium, Firefox, Safari, or all')
    parser.add_argument('--clear-metrics', action='store_true')
    args = parser.parse_args()

    # Browser lista
    if args.browser.lower() == 'all':
        browsers = ['Chromium', 'Firefox', 'WebKit']
    else:
        browsers = [args.browser]

    # Prometheus-fil
    prom_file = get_prom_filename(args.file)
    suite_name = get_suite_name(args.file)
    if args.clear_metrics:
        open(prom_file, 'w').close()
        print(f"Cleared metrics file: {prom_file}")

    # Ladda tester
    try:
        tests = load_config(args.file)
    except Exception as e:
        print(f"Error loading {args.file}: {e}")
        exit(1)

    # Testnamn
    if args.test.lower() == 'all':
        test_names = [t['name'] for t in tests]
    else:
        test_names = [n.strip() for n in args.test.split(',')]

    results = run_tests(tests, test_names, browsers)

    # Spara till Prometheus
    first_test = True
    for key, result in results.items():
        test_name, browser_type = key.rsplit(' [', 1)
        browser_type = browser_type[:-1]
        mode = 'w' if first_test and not args.clear_metrics else 'a'
        save_to_prometheus_format(test_name, 1 if result else 0, suite_name, browser_type, prom_file, mode)
        first_test = False

    print_summary(results)
    exit(0 if all(results.values()) else 1)
