from actions import (
    navigation,
    input,
    mouse,
    keyboard,
    assertions,
    wait,
    files,
    media,
    network,
    storage,
)

ACTION_HANDLERS = {
    **navigation.ACTIONS,
    **input.ACTIONS,
    **mouse.ACTIONS,
    **keyboard.ACTIONS,
    **assertions.ACTIONS,
    **wait.ACTIONS,
    **files.ACTIONS,
    **media.ACTIONS,
    **network.ACTIONS,
    **storage.ACTIONS,
}

def run_step(page, context, step, step_number=None):
    prefix = f"  Step {step_number}: " if step_number else "  "

    for action, payload in step.items():
        if action not in ACTION_HANDLERS:
            raise ValueError(f"Unknown action '{action}'")

        ACTION_HANDLERS[action](page, context, payload)
        print(f"{prefix}✓ {action}")
