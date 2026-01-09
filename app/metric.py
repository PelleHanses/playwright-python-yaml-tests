from pathlib import Path
import time
 
METRIC_DIR = Path("metrics")
METRIC_FILE = METRIC_DIR / "playwright.prom"
 
METRIC_DIR.mkdir(exist_ok=True)
 
def write_test_metric(test_name: str, success: bool):
    """
    Skriver Prometheus-metrics för ETT test.
    Filen trunkeras varje gång funktionen anropas.
    """
 
    # Prometheus-konvention:
    # 0 = OK, 1 = ERROR (enligt din definition)
    status_value = 0 if success else 1
    timestamp_ms = int(time.time() * 1000)
 
    content = f"""# HELP playwright_test_success Status för Playwright-test (0=OK, 1=ERROR)
# TYPE playwright_test_success gauge
playwright_test_success{{test="{test_name}"}} {status_value}
 
# HELP playwright_test_success_timestamp Tidpunkt när testet kördes (epoch ms)
# TYPE playwright_test_success_timestamp gauge
playwright_test_success_timestamp{{test="{test_name}"}} {timestamp_ms}
"""
 
    METRIC_FILE.write_text(content)
