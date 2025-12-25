ACTIONS = {}

def take_screenshot(page, context, payload):
    page.screenshot(
        path=payload["path"],
        full_page=payload.get("full_page", True)
    )

ACTIONS["take_screenshot"] = take_screenshot
