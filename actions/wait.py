ACTIONS = {}

def wait_for_element(page, context, payload):
    page.wait_for_selector(
        payload["selector"],
        timeout=payload.get("timeout", 5000)
    )

ACTIONS["wait_for_element"] = wait_for_element
