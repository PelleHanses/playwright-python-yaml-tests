import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-f", "--file", required=True)
    parser.add_argument("-t", "--test")
    parser.add_argument(
        "--browser",
        choices=["Chromium", "Firefox", "Safari", "all"],
        default="Chromium",
    )
    parser.add_argument("--clear-metrics", action="store_true")

    return parser.parse_args()
