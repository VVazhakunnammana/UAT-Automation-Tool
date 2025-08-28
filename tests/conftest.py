import pytest
import sys
import os
from playwright.sync_api import Page, Browser, BrowserContext

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.uat_parallel_page import UATParallelPage
from pages.grading_page import GradingPage
from utils.config import Config


@pytest.fixture(scope="session", autouse=True)
def setup_directories():
    """Create necessary directories before running tests."""
    Config.create_directories()


@pytest.fixture
def uat_parallel_page(page: Page):
    """Fixture to provide a UATParallelPage instance."""
    return UATParallelPage(page)

@pytest.fixture
def grading_page(page: Page):
    """Fixture to provide a GradingPage instance."""
    return GradingPage(page)


# Commented out missing page fixtures
# @pytest.fixture
# def google_page(page: Page):
#     """Fixture to provide a GooglePage instance."""
#     from pages.google_page import GooglePage
#     return GooglePage(page)

# @pytest.fixture
# def sample_uat_page(page: Page):
#     """Fixture to provide a SampleUATPage instance."""
#     from pages.sample_uat_page import SampleUATPage
#     return SampleUATPage(page)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context arguments."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
        "permissions": ["geolocation", "clipboard-read", "clipboard-write"]
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments."""
    browser_options = Config.get_browser_options("chromium")
    
    return {
        **browser_type_launch_args,
        **browser_options
    }


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture screenshots on test failure."""
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call" and rep.failed:
        # Get the page fixture if available
        if hasattr(item, "funcargs") and "page" in item.funcargs:
            page = item.funcargs["page"]
            screenshot_path = Config.get_screenshot_path(f"{item.name}_failure")
            
            try:
                page.screenshot(path=screenshot_path)
                print(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                print(f"Failed to capture screenshot: {e}")


@pytest.fixture(autouse=True)
def test_setup_teardown(page: Page, request):
    """Setup and teardown for each test."""
    # Setup
    test_name = request.node.name
    print(f"\n🧪 Starting test: {test_name}")
    
    yield
    
    # Teardown
    print(f"✅ Completed test: {test_name}")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "smoke: mark test as a smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
