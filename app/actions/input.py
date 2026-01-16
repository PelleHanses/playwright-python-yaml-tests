from playwright.sync_api import TimeoutError

def fill_input(page, params, logger=None, url_history=None):
    selector = params.get("selector")
    value = params.get("value")
    timeout = params.get("timeout", 10000)

    if not selector or value is None:
        raise ValueError("Parametrar 'selector' och 'value' krävs för fill_input")

    if logger:
        logger.info(f"Fill input: {selector} = '{value}'")

    try:
        locator = page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        locator.fill(value)
    except TimeoutError:
        raise AssertionError(f"Input field not found or not visible: {selector}")

def select_radio(page, params, logger=None, url_history=None):
    selector = params.get("selector")
    timeout = params.get("timeout", 10000)

    if not selector:
        raise ValueError("Parameter 'selector' saknas för select_radio")

    if logger:
        logger.info(f"Selecting radio: {selector}")

    try:
        radio = page.locator(selector)
        radio.wait_for(state="attached", timeout=timeout)
        if not radio.is_checked():
            radio.check(force=True)
        if not radio.is_checked():
            raise AssertionError(f"Radio button not selected: {selector}")
    except TimeoutError:
        raise AssertionError(f"Radio button not found: {selector}")
