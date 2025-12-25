from playwright.sync_api import sync_playwright
from browsers import launch_browser
from run_step import run_step

# ANSI-färger
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def run_single_test(test, browser_label):
    with sync_playwright() as p:
        # Launch browser & context
        browser, context = launch_browser(
            p,
            browser_label,
            mobile_device=test.get("mobile"),
            record_video=test.get("record_video", False)
        )

        page = context.new_page()
        page.goto(test["url"])

        test_passed = True
        try:
            for i, step in enumerate(test.get("steps", []), 1):
                run_step(page, step, i)
        except Exception as e:
            test_passed = False
            print(f"\n{RED}✗ {test['name']} FAILED: {e}{RESET}")

        if test_passed:
            print(f"\n{GREEN}✓ {test['name']} PASSED{RESET}")

        page.close()
        context.close()
        browser.close()
        return test_passed


def print_summary(all_results):
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for browser, results in all_results.items():
        print(f"\nBrowser: {browser}")
        passed = sum(1 for r in results.values() if r)
        failed = len(results) - passed
        for test_name, result in results.items():
            status = f"{GREEN}✓ PASSED{RESET}" if result else f"{RED}✗ FAILED{RESET}"
            print(f"{test_name}: {status}")
        print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
