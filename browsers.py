from playwright.sync_api import sync_playwright

BROWSER_MAP = {
    "Chromium": "chromium",
    "Firefox": "firefox",
    "Safari": "webkit",
}

def launch_browser(p, browser_label, mobile_device=None, record_video=False):
    browser_type = BROWSER_MAP[browser_label]

    if browser_type == "chromium":
        browser = p.chromium.launch()
    elif browser_type == "firefox":
        browser = p.firefox.launch()
    elif browser_type == "webkit":
        browser = p.webkit.launch()
    else:
        raise ValueError(f"Unsupported browser {browser_label}")

    context_args = {}

    if mobile_device:
        context_args.update(p.devices[mobile_device])

    if record_video:
        context_args["record_video_dir"] = "videos/"

    context = browser.new_context(**context_args)
    return browser, context
