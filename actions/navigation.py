ACTIONS = {}

def goto(page, context, payload):
    page.goto(payload["url"])

ACTIONS["goto"] = goto
