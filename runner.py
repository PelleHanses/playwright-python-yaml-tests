from playwright.sync_api import sync_playwright
from browsers import launch_browser
from run_step import run_step

def run_single_test(test, browser_label):
    with sync_playwright() as p:
        browser, context = launch_browser(
            p,
            browser_label,
            mobile_device=test.get("mobile"),
            record_video=test.get("record_video", False)
        )

        page = context.new_page()
        page.goto(test["url"])

        for i, step in enumerate(test.get("steps", []), 1):
            run_step(page, context, step, i)

        page.close()
        context.close()
        browser.close()
        return True
