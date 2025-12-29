from actions.url_matcher import match_url

def search_text(page, params, logger=None, url_history=None):
    text = params.get("text")
    if not text:
        raise ValueError("Parameter 'text' saknas för search_text")
    if logger:
        logger.info(f"Searching for text: {text}")
    if text not in page.content():
        raise AssertionError(f"Text not found: {text}")

def assert_text(page, params, logger=None, url_history=None):
    text = params.get("text")
    if not text:
        raise ValueError("Parameter 'text' saknas för assert_text")
    if logger:
        logger.info(f"Asserting text: {text}")
    if text not in page.content():
        raise AssertionError(f"Text '{text}' not found on page")

def assert_url(page, params, logger=None, url_history=None):
    expected = params.get("expected_url")
    match_type = params.get("match", "startswith")
    if not expected:
        raise ValueError("Parameter 'expected_url' saknas för assert_url")

    current = page.url
    if logger:
        logger.info(f"Assert URL ({match_type}): expected='{expected}', current='{current}'")

    if not match_url(current, expected, match_type):
        history_str = " -> ".join(url_history) if url_history else "N/A"
        raise AssertionError(
            f"\nURL mismatch\n"
            f"  match    : {match_type}\n"
            f"  expected : {expected}\n"
            f"  current  : {current}\n"
            f"  history  : {history_str}"
        )
