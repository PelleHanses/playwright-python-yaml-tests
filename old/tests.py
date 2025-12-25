#!/usr/bin/env python3

import argparse
import yaml
from playwright.sync_api import sync_playwright, Error
import logging
from datetime import datetime
import os

# Konfigurera loggning
logging.basicConfig(filename='test_results.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO)

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['tests']

def run_step(page, step, step_number=None):
    """Kör ett enskilt steg i testet"""
    step_prefix = f"  Step {step_number}: " if step_number else "  "
    
    # Sök efter sträng på sidan
    if 'search_string' in step:
        assert step['search_string'] in page.text_content('body'), \
            f"'{step['search_string']}' not found on the page."
        print(f"{step_prefix}✓ Found text: '{step['search_string']}'")
    
    # Fylla i ett textfält
    if 'input_text_field' in step:
        input_element = page.locator(step['input_text_field']['selector'])
        input_element.fill(step['input_text_field']['value'])
        print(f"{step_prefix}✓ Filled input field")
    
    # Markera en radioknapp
    if 'radio_button' in step:
        radio_element = page.locator(step['radio_button']['selector'])
        radio_element.click()
        print(f"{step_prefix}✓ Clicked radio button")
    
    # Välj i rullgardinsmeny
    if 'dropdown' in step:
        dropdown_element = page.locator(step['dropdown']['selector'])
        dropdown_element.select_option(value=step['dropdown']['value'])
        print(f"{step_prefix}✓ Selected dropdown option")
    
    # Klicka på en knapp
    if 'button_click' in step:
        button_element = page.locator(step['button_click']['selector'])
        button_element.click()
        print(f"{step_prefix}✓ Clicked button")
    
    # Vänta tills sidan har lästs in
    page.wait_for_load_state('networkidle')
    
    # Kontrollera URL efter omdirigeringar
    if 'expected_url' in step:
        current_url = page.url
        assert current_url.startswith(step['expected_url']), \
            f"Expected URL to start with {step['expected_url']}, but got {current_url}"
        print(f"{step_prefix}✓ URL verified: {current_url}")
    
    # Bakåtkompatibilitet med expected_redirect_url
    if 'expected_redirect_url' in step:
        current_url = page.url
        assert current_url.startswith(step['expected_redirect_url']), \
            f"Expected redirect to {step['expected_redirect_url']}, but got {current_url}"
        print(f"{step_prefix}✓ Redirect verified: {current_url}")

#    if 'expected_fragment' in step:
#        fragment = step['expected_fragment'].lstrip('#')
#        page.wait_for_function(f"() => window.location.hash.includes('{fragment}')")
#        current_hash = page.evaluate("() => window.location.hash")
#        if current_hash.startswith('#'):
#            current_hash = current_hash[1:]
#        assert fragment in current_hash, f"Expected fragment '{fragment}' in hash, got '{current_hash}'"
#        print(f"{step_prefix}✓ Fragment verified: {current_hash}")
    if 'expected_fragment' in step:
        fragment = step['expected_fragment']

        # Läs hash direkt via JS (snabbare än page.url)
        hash_value = page.evaluate("() => window.location.hash")

        assert fragment in hash_value, \
            f"Expected fragment '{fragment}' but got '{hash_value}'"

        print(f"{step_prefix}✓ Fragment verified: {hash_value}")


def run_single_test(test):
    """Kör ett enskilt test"""
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
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()

            page.goto(test['url'])
            print(f"  ✓ Navigated to: {test['url']}")

            # Kolla om testet har steps (nytt format)
            if 'steps' in test:
                for i, step in enumerate(test['steps'], 1):
                    run_step(page, step, i)
            else:
                # Kör gamla formatet (bakåtkompatibilitet)
                run_step(page, test)
            
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
            # Stäng resurser om de har skapats
            if page:
                page.close()
            if context:
                context.close()
            if browser:
                browser.close()
    
    return test_passed

def run_tests(tests, test_names):
    """Kör en eller flera tester"""
    results = {}
    
    for test in tests:
        if test['name'] in test_names:
            result = run_single_test(test)
            results[test['name']] = result
    
    return results

def get_prom_filename(yaml_file):
    """
    Generera Prometheus-filnamn baserat på YAML-filens namn
    
    Args:
        yaml_file: Sökväg till YAML-filen (t.ex. 'config.yaml' eller 'tests/smoke-tests.yaml')
    
    Returns:
        Prometheus-filnamn (t.ex. 'test_results-config.prom' eller 'test_results-smoke-tests.prom')
    """
    # Ta bort sökväg och filtyp
    base_name = os.path.basename(yaml_file)
    base_name = base_name.replace('.yaml', '').replace('.yml', '')
    
    return f'test_results-{base_name}.prom'

def get_suite_name(yaml_file):
    """
    Extrahera suite-namn från YAML-filens namn
    
    Args:
        yaml_file: Sökväg till YAML-filen
    
    Returns:
        Suite-namn för Prometheus label
    """
    base_name = os.path.basename(yaml_file)
    suite_name = base_name.replace('.yaml', '').replace('.yml', '')
    
    # Om filnamnet är 'config', använd 'default'
    if suite_name == 'config':
        suite_name = 'default'
    
    return suite_name

def save_to_prometheus_format(test_name, result, suite_name, prom_file, mode='a'):
    """
    Spara testresultat i Prometheus-format
    
    Args:
        test_name: Namnet på testet
        result: 1 för success, 0 för failure
        suite_name: Suite-namn som Prometheus label
        prom_file: Filnamn för Prometheus-metrics
        mode: 'w' för att skriva över, 'a' för att lägga till
    """
    with open(prom_file, mode) as f:
        timestamp = int(datetime.now().timestamp())
        # Testresultat med suite-label
        f.write(f'test_result{{name="{test_name}",suite="{suite_name}"}} {result}\n')
        # När testet senast kördes (för att kunna larma på "inte kört på länge")
        f.write(f'test_last_run_timestamp{{name="{test_name}",suite="{suite_name}"}} {timestamp}\n')

def print_summary(results):
    """Skriv ut sammanfattning av testresultat"""
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Playwright tests from a YAML configuration file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file config.yaml --test all
  %(prog)s --file smoke-tests.yaml --test Meet-login
  %(prog)s --file config.yaml --test "Meet-login,Test-2"
  %(prog)s -f tests.yaml -t all
  %(prog)s --file api-tests.yaml --test all --clear-metrics
        """)
    
    parser.add_argument('-f', '--file', 
                        type=str, 
                        default='config.yaml',
                        help='Path to YAML configuration file (default: config.yaml)')
    
    parser.add_argument('-t', '--test', 
                        type=str, 
                        required=True,
                        help='Test(s) to run: "all" for all tests, or comma-separated test names')
    
    parser.add_argument('--clear-metrics', 
                        action='store_true',
                        help='Clear the Prometheus metrics file before running tests')
    
    args = parser.parse_args()
    
    # Generera filnamn för Prometheus-metrics baserat på YAML-filen
    prom_file = get_prom_filename(args.file)
    suite_name = get_suite_name(args.file)
    
    # Rensa metrics-fil om flaggan är satt
    if args.clear_metrics:
        open(prom_file, 'w').close()
        logging.info(f"Cleared {prom_file}")
        print(f"Cleared metrics file: {prom_file}")
    
    # Ladda tester från fil
    try:
        tests = load_config(args.file)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found!")
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML in '{args.file}': {e}")
        exit(1)
    
    # Bestäm vilka tester som ska köras
    if args.test.lower() == 'all':
        test_names = [test['name'] for test in tests]
        print(f"Running all {len(test_names)} tests from {args.file}")
    else:
        # Dela upp kommaseparerade testnamn
        test_names = [name.strip() for name in args.test.split(',')]
        print(f"Running {len(test_names)} test(s) from {args.file}")
        
        # Kontrollera att alla tester finns
        available_tests = [test['name'] for test in tests]
        missing_tests = [name for name in test_names if name not in available_tests]
        if missing_tests:
            print(f"\nWarning: The following tests were not found in {args.file}:")
            for name in missing_tests:
                print(f"  - {name}")
            print(f"\nAvailable tests: {', '.join(available_tests)}")
            exit(1)
    
    print(f"Metrics will be saved to: {prom_file}")
    
    # Kör tester
    results = run_tests(tests, test_names)
    
    # Spara resultat i Prometheus-format
    # Första testet skriver över filen (w), resten lägger till (a)
    first_test = True
    for test_name, result in results.items():
        mode = 'w' if first_test and not args.clear_metrics else 'a'
        save_to_prometheus_format(test_name, 1 if result else 0, suite_name, prom_file, mode)
        first_test = False
    
    print(f"\nMetrics saved to: {prom_file}")
    
    # Skriv ut sammanfattning
    if len(results) > 1:
        print_summary(results)
    
    # Exit med felkod om något test misslyckades
    exit(0 if all(results.values()) else 1)