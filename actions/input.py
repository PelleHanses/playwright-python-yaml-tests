ACTIONS = {}

def fill(page, context, payload):
    page.locator(payload["selector"]).fill(payload["value"])

def checkbox(page, context, payload):
    el = page.locator(payload["selector"])
    if payload.get("check", True):
        el.check()
    else:
        el.uncheck()

ACTIONS.update({
    "fill": fill,
    "checkbox": checkbox,
})
