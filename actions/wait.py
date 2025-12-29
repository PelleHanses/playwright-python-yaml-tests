import time
from playwright.sync_api import TimeoutError

# --------------------------------------------------
# Vänta på ett element ska renderas
# --------------------------------------------------
def wait_for_element(page, params, logger=None, url_history=None):
    """
    Väntar på att ett element ska finnas i DOM:en.
    params: {"selector": "...", "timeout": 10000}
    """
    selector = params.get("selector")
    timeout = params.get("timeout", 10000)

    if not selector:
        raise ValueError("Parameter 'selector' saknas för wait_for_element")

    if logger:
        logger.info(f"Waiting for element: {selector} (timeout {timeout}ms)")

    try:
        page.wait_for_selector(selector, timeout=timeout)
    except TimeoutError:
        raise AssertionError(f"Element not found within {timeout}ms: {selector}")

# --------------------------------------------------
# Vänta en given tid
# --------------------------------------------------
def wait(page=None, params=None, logger=None, url_history=None):
    """
    Väntar i angiven millisekunder.
    params: {"ms": 1000}
    """
    ms = params.get("ms", 1000) if params else 1000
    if logger:
        logger.info(f"Waiting for {ms} ms")
    time.sleep(ms / 1000.0)

# --------------------------------------------------
# Vänta tills URL matchar expected
# --------------------------------------------------
def wait_for_url(page, params, logger=None, url_history=None):
    """
    Väntar tills aktuell URL matchar expected_url enligt match-typ.
    params: {"expected_url": "...", "match": "startswith|contains|regex", "timeout": 15000}
    """
    expected = params.get("expected_url")
    match_type = params.get("match", "startswith")
    timeout = params.get("timeout", 15000)

    if not expected:
        raise ValueError("Parameter 'expected_url' saknas för wait_for_url")

    if logger:
        logger.info(f"Waiting for URL ({match_type}): expected='{expected}'")

    try:
        if match_type == "regex":
            page.wait_for_url(re.compile(expected), timeout=timeout)
        else:
            page.wait_for_url(
                lambda url: (
                    url.startswith(expected) if match_type == "startswith" else
                    expected in url if match_type == "contains" else False
                ),
                timeout=timeout
            )
    except Exception:
        current = page.url
        history_str = " -> ".join(url_history) if url_history else "N/A"
        raise AssertionError(
            f"\nTimeout waiting for URL\n"
            f"  match    : {match_type}\n"
            f"  expected : {expected}\n"
            f"  current  : {current}\n"
            f"  history  : {history_str}"
        )
