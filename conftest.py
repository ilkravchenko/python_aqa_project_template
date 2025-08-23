"""
conftest.py

Pytest configuration file that sets up Playwright testing, database connections, and test metadata.
Most report-related logic has been moved to html_reporter/report_handler.py.
"""

import os
import time
from pathlib import Path

import pytest
from playwright.sync_api import Playwright, sync_playwright, Browser, BrowserContext, Page

from db.db_connector import DBConnector
from pages.common.header import HeaderComponent
from utils.soft_assert import SoftAssertContextManager

# Constants
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


# Pytest Configuration
def pytest_addoption(parser):
    """Add custom command-line options"""
    parser.addoption("--headless", action="store", default="false", help="Run tests in headless mode (true/false)")
    parser.addoption("--html-report", action="store", default="reports/test_report.html",
                     help="Path to HTML report file")
    parser.addoption("--report-title", action="store", default="RPZM Test Automation Report",
                     help="Title for the HTML report")


@pytest.hookimpl
def pytest_configure(config):
    """
    Configure pytest before test collection and execution.

    This function ensures that required environment variables are set before the tests are run.
    Raises an error if any of the necessary environment variables for KEP or Keycloak (KC) are missing.

    Environment Variables:
        - SECRET_FILE: Path to the KEP (Key Encryption Key) file.
        - SECRET_PASS: Password for the KEP file.
        - KC_CLIENT_ID: Keycloak client ID for authentication.
        - KC_COOKIE: Keycloak session cookie for API authentication.

    Raises:
        ValueError: If any required environment variables are missing.
    """
    config.screenshots_amount = 0  # Limit the number of screenshots attached to reports.

    # Ensure required environment variables are set.

    # Check environment variables
    if not os.getenv('SECRET_FILE'):
        raise ValueError('Path to the KEP file is not provided using SECRET_FILE environment variable!')
    if not os.getenv('SECRET_PASS'):
        raise ValueError('Password for the KEP file is not provided using SECRET_PASS environment variable!')

    os.environ["HEADLESS"] = config.getoption("headless")
    # Turn off timeouts for local testing
    if os.getenv('GITLAB_CI') != 'true':
        config.option.timeout = 0


# Playwright Fixtures
@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    """
    Set up the Playwright instance for the test session.
    This fixture initializes Playwright and yields the instance.

    Returns:
        Playwright: A configured Playwright instance with browser engines.
    """
    with sync_playwright() as playwright:
        # The sync_playwright context manager handles initialization and cleanup
        yield playwright
        # Playwright is automatically closed after all tests complete


@pytest.fixture(scope="session")
def browser(playwright_instance) -> Browser:
    """
    Launch a Chromium browser instance.
    The browser stays active for the entire session and closes after tests complete.

    Args:
        playwright_instance: The Playwright instance from the playwright_instance fixture

    Returns:
        Browser: A configured Chromium browser instance

    Environment Variables:
        HEADLESS: When 'true', runs the browser without a visible UI
    """
    if os.getenv('HEADLESS', 'false') == 'true':
        # Launch in headless mode (no visible browser window)
        browser = playwright_instance.chromium.launch(headless=True)
    else:
        # Launch with visible browser window and maximize it
        browser = playwright_instance.chromium.launch(headless=os.getenv('HEADLESS', 'false') == 'true',
                                                      args=["--start-maximized"])
    yield browser
    # Ensure browser is closed after all tests complete
    browser.close()


@pytest.fixture(scope="session")
def browser_context(browser) -> BrowserContext:
    """
    Create a new browser context for the test module.
    Each context has isolated sessions, cookies, and storage to avoid test interference.

    Args:
        browser: The Browser instance from the browser fixture

    Returns:
        BrowserContext: An isolated browser context with its own cookies/storage

    Environment Variables:
        HEADLESS: When 'true', configures viewport dimensions for headless mode
    """
    if os.getenv('HEADLESS', 'false') == 'true':
        # Fixed viewport size for consistent testing in headless mode
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, screen={"width": 1920, "height": 1080})
    else:
        # Use system's native viewport size (maximized browser)
        context = browser.new_context(no_viewport=True)
    yield context
    # Clean up the context after module tests complete
    context.close()


@pytest.fixture(scope="session")
def page(request, browser_context) -> Page:
    """
    Create a new page within the browser context for testing.

    Args:
        request: The pytest request object for test metadata access
        browser_context: The BrowserContext instance from the browser_context fixture

    Returns:
        Page: A new browser page for test automation

    Notes:
        - Attaches the page to the request node for access in other fixtures/hooks
        - Automatically handles logout before closing the page
    """
    # Create a new page in the current browser context
    page = browser_context.new_page()
    # Attach page to pytest request for access in other fixtures/hooks
    request.node.page = page
    yield page
    # Attempt to log out if still logged in before closing the page
    header = HeaderComponent(page)
    if header.user_info.is_visible:
        try:
            header.user_info.logout()
        except Exception:
            # Silently continue if logout fails
            pass
    # Close the page to clean up resources
    page.close()


@pytest.hookimpl
def pytest_sessionfinish(session):
    """
    Generate final HTML report and clean up resources after all tests finish.

    This hook runs after all tests have completed execution to:
    1. Clean up orphaned Playwright browser processes
    2. Generate a consolidated HTML report from individual test results
    3. Remove temporary JSON files after report generation

    Args:
        session: The pytest session object containing test information
    """
    # Force cleanup of any remaining browser processes to prevent resource leaks
    import psutil
    current_pid = os.getpid()

    # Only clean processes related to current worker to avoid affecting other test runs
    for proc in psutil.process_iter():
        try:
            # Check if process is child of current process and is a Playwright browser
            if proc.ppid() == current_pid and 'playwright' in proc.name().lower():
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Skip processes we can't access or that no longer exist
            pass

    # Skip report generation on worker nodes in distributed testing
    if hasattr(session.config, "workerinput"):
        return  # Skip on worker nodes - only master node generates the report


# Test logging helper
@pytest.fixture
def test_logger(request):
    """
    Fixture to add logs to test results that will be included in the final report.

    Args:
        request: The pytest request object

    Returns:
        callable: A function that adds messages to the test logs
    """

    def _log_message(message: str):
        if not hasattr(request.node, "test_logs"):
            request.node.test_logs = []
        request.node.test_logs.append(message)

    return _log_message


@pytest.fixture(scope="session")
def db_conn() -> DBConnector:
    """
    Creates a PostgreSQL connection to the registry database for the entire test session.

    Retrieves database credentials from OpenShift secrets and establishes a connection
    to the operational PostgreSQL instance.

    Yields:
        psycopg2.connection: Active database connection to the registry database
    """
    pod_name = "POD_NAME"
    namespace = "NAMESPACE"
    dbname = "DB_NAME"
    pg_info = dict()
    pod_port = int(pg_info['port'])
    user = pg_info['user']
    password = pg_info['password']

    # Connection is automatically closed when the context manager exits
    with DBConnector(pod_name, namespace, pod_port, dbname, user, password) as connection:
        yield connection


@pytest.fixture
def soft_assert(request) -> SoftAssertContextManager:
    """
    Provides a soft assertion mechanism that collects failures without stopping test execution.

    Creates a SoftAssertContextManager and attaches it to the test item for later
    access during test result processing. This allows multiple assertions to be checked
    within a single test while collecting all failures.

    Args:
        request: The pytest request object

    Returns:
        SoftAssertContextManager: Soft assertion context for collecting multiple failures
    """
    context = SoftAssertContextManager()
    request.node._soft_assert = context  # Attach to the pytest item for later access
    return context


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """
    Hook to track the currently running test item throughout the test framework.

    Sets a global reference to the current test item that can be accessed
    by utilities that don't receive the test item directly.

    Args:
        item: The current test item being executed
        nextitem: The next test item to be executed
    """
    pytest.current_item = item
    yield
    pytest.current_item = None


@pytest.hookimpl(tryfirst=True)
def pytest_configure_node(node):
    """
    Logs when a worker node is configured in distributed testing mode.

    This provides visibility into test distribution and parallel execution status.

    Args:
        node: The worker node being configured
    """
    node.log.info(f"Worker {node.gateway.id} is configured and starting")


@pytest.hookimpl(tryfirst=True)
def pytest_testnodedown(node, error):
    """
    Logs the status of a worker node when it completes testing.

    Provides error details if the node failed or a success message if it completed normally.

    Args:
        node: The worker node that has finished
        error: Error information if the node failed, None otherwise
    """
    if error:
        node.log.error(f"Worker {node.gateway.id} failed: {error}")
    else:
        node.log.info(f"Worker {node.gateway.id} finished successfully")


@pytest.fixture
def page_if_exists(request):
    """Helper fixture to check if the test uses the page fixture."""
    if "page" not in request.fixturenames:
        return None

    return request.getfixturevalue("page")


@pytest.fixture(autouse=True, scope="function")
def capture_console_logs(request, page_if_exists):
    """Capture browser console logs for UI tests only."""
    # Skip for non-UI tests
    if not page_if_exists:
        yield
        return

    console_logs = []

    def log_event(msg):
        console_logs.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location["url"] if msg.location and "url" in msg.location else "unknown",
            "timestamp": time.time()
        })

    # Add event listener
    page_if_exists.on("console", log_event)

    # Store on test item
    request.node.console_logs = console_logs

    yield


@pytest.fixture(autouse=True, scope="function")
def capture_network_failures(request, page_if_exists):
    """Capture failed network requests for UI tests only without adding overhead."""
    # Skip for non-UI tests
    if not page_if_exists:
        yield
        return

    failed_requests = []

    # Simple event handler - minimal processing, fire and forget
    def log_response(response):
        # Only track failed responses (4xx & 5xx status codes)
        if 400 <= response.status < 600 and response.request.resource_type in ["fetch", "xhr"]:
            # Try to get request post data if available
            request_body = ""
            try:
                post_data = response.request.post_data
                if post_data:
                    request_body = post_data
            except Exception:
                # Silently continue if we can't get request body
                pass

            # Minimal data collection - no processing that would block test execution
            failed_requests.append({
                "url": response.url,
                "status": response.status,
                "status_text": response.status_text,
                "method": response.request.method,
                "headers": dict(response.headers),  # Simple dict conversion is fast
                "timestamp": time.time(),
                "resource_type": response.request.resource_type,
                "request_body": request_body,  # Include request body if available
                "content": ""  # Don't collect content to avoid any delay
            })

    # Add event listener
    page_if_exists.on("response", log_response)

    # Store reference immediately
    request.node.failed_requests = failed_requests

    yield

