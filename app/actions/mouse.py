# actions/mouse.py

from playwright.sync_api import TimeoutError

def click(page, params, logger=None, url_history=None):
    selector = params.get("selector")
    timeout = params.get("timeout", 10000)

    if not selector:
        raise ValueError("Parameter 'selector' saknas för click_element")

    if logger:
        logger.info(f"Click element: {selector}")

    try:
        locator = page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.click()
    except TimeoutError:
        raise AssertionError(f"Element not clickable: {selector}")
