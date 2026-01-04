# Playwright YAML Test Runner

A simple, modular test runner for browser automation built with Playwright
 and YAML configuration files. Designed to run automated steps in the browser without hardcoding logic, allowing new tests and actions to be added easily.

## Features

- Dynamically loads actions from the actions/ folder Supports Chromium, Firefox, and Safari
- Can run in headless or headed mode
- Color-coded logging in the terminal (INFO, ERROR, WARNING)
- URL assertions with match types: startswith, contains, regex
- Waits for elements, fills input fields, clicks buttons, selects radio buttons, etc.
- Supports fake camera, microphone, and speaker in Chromium for automated media testing
- Generates Prometheus-style metrics in metrics/test_metrics.prom

## Flow Diagram
┌───────────────┐
│  runner.py    │
│  (main loop)  │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│  Load YAML    │
│  (tests/*.yaml)│
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Iterate over  │
│  steps        │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Dynamically   │
│ load actions  │
│ from actions/ │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Execute action│
│ (fill_input,  │
│ click_element,│
│ wait_for_url, │
│ select_radio, │
│ etc.)         │
└───────────────┘

## Installation

Clone the repository:
```
git clone <repo-url>
cd <repo-folder>
```

Install required Python packages:
```
python3 -m pip install -r requirements.txt
```
Install Playwright browsers:
```
python3 -m playwright install
```
## Usage
```
./runner.py --file tests/meet_login_guest.yaml --test "Jitsi-guest-full-login-flow" --browser Chromium --headless false
```

## Command-line Parameters
Parameter	Description
'-f, --file	         YAML file containing test cases (required)
'-t, --test	         Specific test name to run (optional)
'--browser	         Chromium, Firefox, Safari, or all (default: Chromium)
'--headless	         true or false (default: false)
'--clear-metrics	   Clears the metrics file before running

## Creating a New Action

1. Create a new Python file in the actions/ folder, e.g., actions/my_action.py.

2. Define the function with the following signature:
```
def my_action(page, params, logger, url_history=None):
    selector = params["selector"]
    logger.info(f"Doing something with {selector}")
    # Your code here, e.g., page.fill(selector, "text")
```

3. Add the action in your YAML test:
```
- my_action:
    selector: "#input-field"
  info: "Fills the input field with my_action"
```

4. The runner automatically loads all .py files in the actions/ folder.

## Example YAML Test File
```
- name: Jitsi-guest-full-login-flow
  steps:
    - goto:
        url: "https://jitsi-preprod.sgit.se/test_auto01"
      info: "Navigate to Jitsi"

    - wait: 
        ms: 4000
      info: "Wait for 4 seconds"

    - wait_for_url:
        expected_url: "https://pre.safos.se/video/login/login.php?/test_auto01?state="
        match: contains
      info: "Verify redirect to login page"

    - search_text:
        text: "How do you want"
      info: "Search for text 'How do you want'"

    - wait_for_element:
        selector: 'div.login-options form#loginForm'
      info: "Wait for login form"

    - select_radio:
        selector: "input[name='userType'][value='guest']"
      info: "Select 'Guest' radio button"

    - fill_input:
        selector: "#name"
        value: "SAFOS Guest"
      info: "Fill in name"

    - click_element:
        selector: "#submitBtn"
      info: "Click the submit button"

    - assert_url:
        expected_url: "https://auth-video-pp.safos.se"
        match: startswith
      info: "Check authentication page"

    - wait_for_element:
        selector: "#continue"
      info: "Wait for Continue button"

    - click_element:
        selector: "#continue"
      info: "Click Continue"
```
## Logging and ANSI Colors

This runner uses Python’s logging module with a custom console formatter to improve readability during test execution.

### Console Output (ANSI Colors)

Log messages are colorized using ANSI escape codes:

Log  Level	      Color
INFO              White
WARNING	          Yellow
ERROR	            Red

This makes it easy to spot problems immediately when running tests interactively.

Example output:
```
[INFO] goto : Navigate to Jitsi
[INFO] wait_for_url : Verifying redirect to login page
[WARNING] Optional element not found, continuing
[ERROR] assert_url : URL mismatch
```
### File Logging
- All logs are also written without ANSI colors to a log file
- Log files are stored in the log/ directory
- Filename format:
```
log/test_YYYYMMDD_HHMMSS.log
```
This makes logs safe to parse, archive, or ship to log aggregation systems.

### Logger Injection into Actions

Each action can optionally receive a logger:
```
def fill_input(page, params, logger):
    logger.info("Filling input field")
```
The runner automatically injects the logger if the function signature includes a logger parameter.
This keeps actions clean and avoids global logging state.

## Metrics and Prometheus / Alloy Integration
The test runner generates Prometheus-compatible metrics after each run.
These metrics can be scraped by Grafana Alloy, Prometheus, or any compatible collector.

### Metrics File
Metrics are written to:
```
metrics/test_metrics.prom
```
Example content:
```
test_passed 1 1735503268
test_failed 0 1735503268
test_total  1 1735503268
```
### Exported Metrics
Metric Name	  Description
test_passed	  Number of passed  tests
test_failed	  Number of failed tests
test_total	  Total number of executed tests

Each metric includes a Unix timestamp, making it compatible with Prometheus textfile collectors.

### Clearing Metrics
You can clear the metrics file before a run:
```
./runner.py --file tests/test.yaml --clear-metrics
```
### Example Alloy Configuration
```
prometheus.scrape "playwright_tests" {
  targets = [{
    __address__ = "localhost"
  }]

  scrape_interval = "30s"

  metrics_path = "/metrics"
}

prometheus.exporter.textfile "playwright" {
  directory = "/path/to/metrics"
}
```
This allows:
- CI/CD test monitoring
- Dashboards showing test stability over time
- Alerting on failed test spikes



## License
MIT License © Pelle Hanses
```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
```


