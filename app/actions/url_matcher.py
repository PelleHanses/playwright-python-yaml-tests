import re

def match_url(current_url, expected, match_type):
    if match_type == "startswith":
        return current_url.startswith(expected)

    if match_type == "contains":
        return expected in current_url

    if match_type == "regex":
        return re.search(expected, current_url) is not None

    raise ValueError(f"Unknown match type: {match_type}")
