ACTIONS = {}

def assert_element(page, context, payload):
    el = page.locator(payload["selector"])
    text = el.inner_text()
    assert text == payload["text"], f"Expected '{payload['text']}', got '{text}'"

ACTIONS["assert_element"] = assert_element
