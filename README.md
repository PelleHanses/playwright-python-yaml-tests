# Playwright Python YAML Enterprise Tests
A YAML-configured enterprise-ready Playwright test runner for Python with multi-browser support, Prometheus metrics export, screenshots, and advanced step actions. Run browser automation tests defined in YAML files and export results in Prometheus format for monitoring and alerting.

[TOC]

## Features
- 🎯 YAML Configuration - Define tests in simple, readable YAML files
- 🔄 Multi-step Tests - Support complex test flows with multiple steps
- 🌐 Multi-Browser - Run tests on Chromium, Firefox, Safari, or all simultaneously
- 📸 Screenshots & Video - Capture screenshots per step
- ⏳ Wait for Elements - Reduce flaky tests with explicit waits
- ⌨️ Keyboard & Hover Actions - Simulate advanced user interactions
- 📂 File Upload & Drag-and-Drop - Support complex UI tests
- 🍪 Cookies & Local Storage - Manage session data in tests
- 🏷️ Prometheus Metrics with Browser Label - Monitor tests in Grafana with detailed labels
- ✅ Backward Compatible - Supports both simple and advanced test formats
- 🚀 Easy to Run - CLI with --file, --test, --browser, --clear-metrics
- 📝 Comprehensive Logging - All test results logged to test_results.log


## Installation
### Prerequisites
Python 3.8+
pip

### Setup
git clone https://github.com/PelleHanses/playwright-python-yaml-tests
cd playwright-python-yaml-tests

python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium firefox webkit

## Usage
R## un Tests
```
# Default Chromium
./main.py --file test_files/preprod-meet.yml --test Meet-login-guest

# Specify browser
./main.py --file test_files/preprod-meet.yml --test Meet-login-guest --browser Firefox

# Run all browsers
./main.py --file test_files/preprod-meet.yml --test Meet-login-guest --browser all

# Clear metrics before running
./main.py --file test_files/preprod-meet.yml --test all --clear-metrics
```

## Command-Line Arguments
Argument	Short	Required	Default	Description
--file	-f	No	config.yaml	Path to YAML configuration file
--test	-t	Yes	-	Test(s) to run: "all" or comma-separated names
--browser	-	No	Chromium	Browser to run: Chromium, Firefox, Safari, or all
--clear-metrics	-	No	false	Clear Prometheus metrics before running
## YAML Configuration
### Simple Test Format
```
tests:
  - name: Meet-login
    url: "https://meet.sgit.se/test_auto01"
    search_string: "Moderator och identifierade deltagare"
    expected_redirect_url: "https://files.sgit.se/video/login/login.php?/test_auto01"
```

### Advanced Test Format with Steps
```
tests:
  - name: Meet-login-guest
    url: "https://jitsi-preprod.sgit.se/test_auto01"
    steps:
      - wait_for_element: 'body'
      - search_string: "Hur vill du"
        expected_url: "https://pre.safos.se/video/login/login.php?state=..."
      - take_screenshot: "step1_page_loaded.png"

      - radio_button:
          selector: 'input[name="userType"][value="guest"]'
      - input_text_field:
          selector: "#name"
          value: "SAFOS Guest"
      - wait_for_element: "#submitBtn"
      - button_click:
          selector: "#submitBtn"
      - take_screenshot: "step2_guest_filled.png"

      - wait_for_element: "#continue"
      - button_click:
          selector: "#continue"
        expected_url: "https://auth-video-pp.safos.se"
      - take_screenshot: "step3_redirect_auth.png"

      - wait_for_element: "#jitsi-container"
      - expected_url: "https://jitsi-preprod.sgit.se/test_auto01"
      - take_screenshot: "step4_final_jitsi.png"

      - assert_element:
          selector: "h1"
          text: "Välkommen"
```

### Supported Actions
Action	YAML Key	Description
Navigate	url	Go to URL
Search Text	search_string	Assert text exists
Fill Input	input_text_field	Fill text input
Click Button	button_click	Click element
Select Radio	radio_button	Select radio button
Select Dropdown	dropdown	Select dropdown option
Wait for Element	wait_for_element	Wait until selector exists
Take Screenshot	take_screenshot	Capture screenshot
Assert Element	assert_element	Check element text/content
Verify URL	expected_url	Assert URL starts with value
Verify Redirect	expected_redirect_url	Assert redirect URL
Verify Fragment	expected_fragment	Assert URL fragment

## Enterprise examples
### Drag and Drop
steps:
  - wait_for_element: "#drag-source"
  - wait_for_element: "#drop-target"
  - drag_and_drop:
      source: "#drag-source"
      target: "#drop-target"
  - take_screenshot: "step_drag_drop.png"
### File Upload
steps:
  - wait_for_element: "#file-input"
  - upload_file:
      selector: "#file-input"
      path: "/path/to/file.pdf"
  - take_screenshot: "step_file_upload.png"
### Hover and Click
steps:
  - wait_for_element: "#menu"
  - hover:
      selector: "#menu"
  - button_click:
      selector: "#submenu-item"
  - take_screenshot: "step_hover_click.png"
### Keyboard Input
steps:
  - wait_for_element: "#input-field"
  - keyboard_input:
      selector: "#input-field"
      text: "Hello World"
      press_enter: true
  - take_screenshot: "step_keyboard.png"
### Mobile Emulation Example
steps:
  - emulate_device: "iPhone 13"
  - wait_for_element: "#mobile-menu"
  - button_click:
      selector: "#mobile-menu"
  - take_screenshot: "step_mobile.png"
### Network and Cookies Example
steps:
  - set_cookie:
      name: "session_id"
      value: "123456"
      domain: "example.com"
  - block_request:
      url_pattern: "*/ads/*"
  - go_to: "https://example.com/dashboard"
  - take_screenshot: "step_network_cookies.png"
### Assertions on Elements
steps:
  - wait_for_element: "h1"
  - assert_element:
      selector: "h1"
      text: "Welcome"

💡 Tip: All advanced actions integrate seamlessly with existing steps like wait_for_element, search_string, and take_screenshot. This approach keeps your YAML modular, readable, and enterprise-ready without expanding main.py unnecessarily.

## Example file - test_files/example.yml
What the file shows:
1. Page load & search text – search_string, wait_for_element
2. Input & keyboard actions – input_text_field, keyboard_input
3. Hover & menu clicks – hover, button_click
4. Dropdown & radio buttons – dropdown, radio_button
5. File upload – upload_file
6. Drag-and-drop – drag_and_drop
7. Mobile emulation – emulate_device
8. Network & cookies – set_cookie, block_request, go_to
9. Multiple tabs/windows – new_tab, close_tab
10. Assertions & URL/fragment verification – assert_element, expected_url, expected_fragment
11. Screenshots per step – take_screenshot

💡 Usage tips:
The file works as a master template – you can comment/remove steps that are not needed.
Steps with wait_for_element before search_string or click make tests more stable against dynamically loaded pages.
emulate_device changes the viewport/resolution and user agent for mobile testing.
The browser parameter (--browser Chromium|Firefox|Safari|all) is automatically logged in Prometheus metrics.

## Output and Results
### Console Output
```
Running test: Meet-login-guest
============================================================
  ✓ Navigated to: https://jitsi-preprod.sgit.se/test_auto01
  ✓ Found text: 'Hur vill du'
  ✓ Clicked radio button
  ✓ Filled input field
  ✓ Clicked button
  ✓ Redirect verified: https://auth-video-pp.safos.se
  ✓ Fragment verified: #connect_as=guest,connect_name=SAFOS Guest

✓ Test 'Meet-login-guest' PASSED!
```
## Prometheus Metrics

Metrics now include browser:
```
test_result{name="Meet-login-guest",suite="preprod-meet",browser="Chromium"} 1
test_last_run_timestamp{name="Meet-login-guest",suite="preprod-meet",browser="Chromium"} 1734876543
```
- browser label shows which browser executed the test
- 1 = passed, 0 = failed

## Running Multiple Test Suites & Browsers
```
#!/bin/bash
# run_all_tests.sh
./main.py -f smoke-tests.yaml -t all --browser all --clear-metrics
./main.py -f api-tests.yaml -t all --browser all --clear-metrics
./main.py -f ui-tests.yaml -t all --browser all --clear-metrics
```
## Project Structure
playwright-python-yaml-tests/
├── main.py                # Main test runner
├── config.yaml            # Default test config
├── test_files/            # YAML test files
├── test_results.log       # Logs
├── test_results-*.prom    # Prometheus metrics
├── requirements.txt       # Dependencies
├── README.md              # This file
└── LICENSE                # MIT License

## Development
Add new actions in run_step() in main.py
Enterprise-ready: easily extendable for hover, drag-and-drop, file upload, network, cookies, mobile emulation, etc.

## Authors

- Pelle Hanses - Initial work

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Metrics format compatible with [Prometheus](https://prometheus.io/)
- YAML parsing with [PyYAML](https://pyyaml.org/)

## License
MIT License
