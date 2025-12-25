from playwright.sync_api import sync_playwright

BROWSER_MAP = {
    "Chromium": "chromium",
    "Firefox": "firefox",
    "Safari": "webkit",
}

def launch_browser(p, browser_label, mobile_device=None, record_video=False):
    browser_type = BROWSER_MAP[browser_label]

    launch_args = {}
    if browser_type == "chromium":
        launch_args["headless"] = False
        launch_args["args"] = [
            "--use-fake-ui-for-media-stream",
            "--use-fake-device-for-media-stream",
        ]
        browser = p.chromium.launch(**launch_args)
    elif browser_type == "firefox":
        browser = p.firefox.launch(headless=False)
    elif browser_type == "webkit":
        browser = p.webkit.launch(headless=False)
    else:
        raise ValueError(f"Unsupported browser {browser_label}")

    context_args = {
        "permissions": ["camera", "microphone"],  # alltid tillåt
    }

    if mobile_device:
        context_args.update(p.devices[mobile_device])
    if record_video:
        context_args["record_video_dir"] = "videos/"

    context = browser.new_context(**context_args)
    return browser, context
