# wait.py
ACTIONS = {}

def wait_for_element(page, context, payload):
    """Wait for an element to appear, med optional timeout"""
    page.wait_for_selector(
        payload["selector"],
        timeout=payload.get("timeout", 5000)  # default 5 sekunder
    )

def wait_for_timeout(page, context, payload):
    """Wait a fixed amount of tid i millisekunder"""
    ms = payload if isinstance(payload, int) else payload.get("ms", 1000)
    page.wait_for_timeout(ms)

def wait_for(page, context, payload):
    """
    Generic wait: kan vänta på element, funktion eller annat
    payload kan vara dict med valfri Playwright wait_for metod
    """
    if isinstance(payload, dict):
        # timeout default 5s
        timeout = payload.get("timeout", 5000)
        selector = payload.get("selector")
        if selector:
            page.wait_for_selector(selector, timeout=timeout)
        else:
            raise ValueError("wait_for dict måste ha 'selector'")
    else:
        raise ValueError("wait_for payload måste vara dict med 'selector'")

ACTIONS["wait_for_element"] = wait_for_element
ACTIONS["wait_for_timeout"] = wait_for_timeout
ACTIONS["wait_for"] = wait_for
