# Playwright Python YAML Tests

A YAML-configured Playwright test runner for Python with Prometheus metrics export. Run browser automation tests defined in simple YAML configuration files and export results in Prometheus format for monitoring and alerting.

[TOC]

## Features

- 🎯 **YAML Configuration** - Define tests in simple, readable YAML files
- 🔄 **Multi-step Tests** - Support for complex test flows with multiple steps
- 📊 **Prometheus Metrics** - Automatic export of test results and timestamps
- 🏷️ **Suite Labels** - Organize tests by suite with Prometheus labels
- ✅ **Backward Compatible** - Supports both simple and advanced test formats
- 🚀 **Easy to Run** - Simple command-line interface
- 📝 **Comprehensive Logging** - All test results logged to file

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/PelleHanses/playwright-python-yaml-tests
cd playwright-python-yaml-tests
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install playwright pyyaml
playwright install chromium
```

## Usage

### Basic Usage

```bash
# Run all tests from config.yaml
./tests.py --test all

# Run a specific test
./tests.py --test Meet-login

# Run multiple specific tests
./tests.py --test "Meet-login,Test-2,More"
```

### With Custom YAML File

```bash
# Run all tests from a specific file
./tests.py --file smoke-tests.yaml --test all

# Run specific tests from a custom file
./tests.py --file api-tests.yaml --test "login,logout"
```

### Clear Metrics Before Running

```bash
# Clear the Prometheus metrics file before running tests
./tests.py --file smoke-tests.yaml --test all --clear-metrics
```

## Command-Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--file` | `-f` | No | `config.yaml` | Path to YAML configuration file |
| `--test` | `-t` | Yes | - | Test(s) to run: `"all"` for all tests, or comma-separated test names |
| `--clear-metrics` | - | No | `false` | Clear the Prometheus metrics file before running tests |

### Examples

```bash
# Use default config.yaml, run all tests
./tests.py -t all

# Use custom file with short notation
./tests.py -f tests/smoke.yaml -t all

# Run specific tests and clear metrics
./tests.py --file api-tests.yaml --test "health_check" --clear-metrics

# Show help
./tests.py --help
```

## YAML Configuration

### Simple Test Format

```yaml
tests:
  - name: Meet-login
    url: "https://meet.sgit.se/test_auto01"
    search_string: "Moderator och identifierade deltagare"
    expected_redirect_url: "https://files.sgit.se/video/login/login.php?/test_auto01"
```

### Advanced Test Format with Steps

```yaml
tests:
  - name: Multi-step-login
    url: "https://example.com/login"
    steps:
      - search_string: "Welcome"
        expected_url: "https://example.com/login"
      
      - input_text_field:
          selector: "#username"
          value: "testuser"
        button_click:
          selector: "#login-btn"
        expected_url: "https://example.com/verify"
      
      - input_text_field:
          selector: "#code"
          value: "123456"
        button_click:
          selector: "#verify-btn"
        expected_url: "https://example.com/dashboard"
```

### Supported Actions

| Action | YAML Key | Description | Example |
|--------|----------|-------------|---------|
| Navigate | `url` | Navigate to URL | `url: "https://example.com"` |
| Search Text | `search_string` | Assert text exists on page | `search_string: "Welcome"` |
| Fill Input | `input_text_field` | Fill text input field | `input_text_field:`<br>&nbsp;&nbsp;`selector: "#username"`<br>&nbsp;&nbsp;`value: "test"` |
| Click Button | `button_click` | Click a button or element | `button_click:`<br>&nbsp;&nbsp;`selector: "#submit"` |
| Select Radio | `radio_button` | Select a radio button | `radio_button:`<br>&nbsp;&nbsp;`selector: "input[value='option']"` |
| Select Dropdown | `dropdown` | Select dropdown option | `dropdown:`<br>&nbsp;&nbsp;`selector: "#select"`<br>&nbsp;&nbsp;`value: "Option 2"` |
| Verify URL | `expected_url` | Assert URL starts with value | `expected_url: "https://example.com/page"` |
| Verify Redirect | `expected_redirect_url` | Assert redirect URL | `expected_redirect_url: "https://example.com"` |

## Output and Results

### Console Output

```
Running 3 test(s) from smoke-tests.yaml
Metrics will be saved to: test_results-smoke-tests.prom

Running test: Meet-login
============================================================
  ✓ Navigated to: https://meet.sgit.se/test_auto01
  ✓ Found text: 'Moderator och identifierade deltagare'
  ✓ Redirect verified: https://files.sgit.se/video/login/login.php

✓ Test 'Meet-login' PASSED!

...

Metrics saved to: test_results-smoke-tests.prom

============================================================
TEST SUMMARY
============================================================
Meet-login: ✓ PASSED
Meet-login-2: ✓ PASSED
Test-2: ✗ FAILED
------------------------------------------------------------
Total: 3 | Passed: 2 | Failed: 1
============================================================
```

### Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed, or error occurred

### Log Files

Test results are logged to `test_results.log`:
```
2024-12-22 10:30:15 - INFO - Starting test: Meet-login
2024-12-22 10:30:18 - INFO - Test 'Meet-login' passed!
```

### Prometheus Metrics

Each YAML file generates its own metrics file: `test_results-<filename>.prom`

**Example: `test_results-smoke-tests.prom`**
```
test_result{name="Meet-login",suite="smoke-tests"} 1
test_last_run_timestamp{name="Meet-login",suite="smoke-tests"} 1734876543
test_result{name="Meet-login-2",suite="smoke-tests"} 1
test_last_run_timestamp{name="Meet-login-2",suite="smoke-tests"} 1734876543
```

**Metrics:**
- `test_result` - Test result (1 = passed, 0 = failed)
- `test_last_run_timestamp` - Unix timestamp of last test run

**Labels:**
- `name` - Test name
- `suite` - Suite name (derived from YAML filename)

## Monitoring with Prometheus/Grafana

### Alloy/Prometheus Configuration

Configure your Alloy agent to scrape the metrics files:

```hcl
prometheus.exporter.textfile "test_metrics" {
  directory = "/path/to/playwright-python-yaml-tests"
  
  forward_to = [prometheus.remote_write.default.receiver]
}
```

### Grafana Queries

```promql
# Show all test results
test_result

# Alert on failed tests
test_result == 0

# Alert on tests not run in 5 hours
(time() - test_last_run_timestamp) > 18000

# Show time since last run (in hours)
(time() - test_last_run_timestamp) / 3600

# Failed tests in specific suite
test_result{suite="smoke-tests"} == 0
```

### Example Alert Rules

```yaml
groups:
  - name: playwright_tests
    interval: 1m
    rules:
      - alert: PlaywrightTestFailed
        expr: test_result == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Playwright test {{ $labels.name }} failed"
          description: "Test {{ $labels.name }} in suite {{ $labels.suite }} has failed"
      
      - alert: PlaywrightTestNotRun
        expr: (time() - test_last_run_timestamp) > 21600
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Playwright test {{ $labels.name }} not run recently"
          description: "Test {{ $labels.name }} has not run in over 6 hours"
```

## Running Multiple Test Suites

Create a wrapper script to run multiple test suites:

```bash
#!/bin/bash
# run_all_tests.sh

echo "Running all test suites..."

./tests.py --file smoke-tests.yaml --test all --clear-metrics
./tests.py --file api-tests.yaml --test all --clear-metrics
./tests.py --file ui-tests.yaml --test all --clear-metrics

echo "All test suites completed!"
echo "Check metrics: ls -l test_results-*.prom"
```

## Project Structure

```
playwright-python-yaml-tests/
├── tests.py              # Main test runner script
├── config.yaml           # Default test configuration
├── test_results.log      # Test execution log
├── test_results-*.prom   # Prometheus metrics files
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── LICENSE              # MIT License
```

## Development

### Adding New Actions

To add new test actions, modify the `run_step()` function in `tests.py`:

```python
def run_step(page, step, step_number=None):
    # ... existing code ...
    
    # Add your new action
    if 'your_new_action' in step:
        # Implement action logic
        pass
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Troubleshooting

### Common Issues

**"Playwright error: Event loop is closed"**
- Solution: This is handled automatically in the current version

**"Test not found in config.yaml"**
- Check test name spelling in YAML file
- Ensure test name matches exactly (case-sensitive)

**"File 'config.yaml' not found"**
- Ensure YAML file exists in the specified path
- Use `--file` to specify correct path

**Tests fail with selector errors**
- Verify selectors using browser DevTools
- Wait for page load: actions automatically wait for `networkidle`

## License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Authors

- Pelle Hanses - Initial work

## Acknowledgments

- Built with [Playwright](https://playwright.dev/)
- Metrics format compatible with [Prometheus](https://prometheus.io/)
- YAML parsing with [PyYAML](https://pyyaml.org/)
