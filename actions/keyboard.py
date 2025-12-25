ACTIONS = {}

def keyboard(page, context, payload):
    if "press" in payload:
        page.keyboard.press(payload["press"])
    if "type" in payload:
        page.keyboard.type(payload["type"])

ACTIONS["keyboard"] = keyboard
