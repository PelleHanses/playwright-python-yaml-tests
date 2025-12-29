from actions import navigation, wait, assertions, input, mouse
from console import step_ok, step_fail

ACTION_MAP = {
    "goto": navigation.goto,
    "wait_for_element": wait.wait_for_element,
    "wait_for_url": wait.wait_for_url,
    "wait": wait.wait,

    "search_text": assertions.search_text,
    "assert_url": assertions.assert_url,

    "fill": input.fill,
    "click": mouse.click,
}

def execute_steps(page, steps, logger, url_history):
    for step in steps:
        action_name, payload = next(iter(step.items()))

        if action_name not in ACTION_MAP:
            raise ValueError(f"Unknown action: {action_name}")

        try:
            ACTION_MAP[action_name](page, payload, logger, url_history)
            step_ok(f"{action_name} {payload}")
        except Exception:
            step_fail(f"{action_name} {payload}")
            raise

