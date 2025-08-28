import os
from typing import Dict, Any


class Config:
    """Configuration settings for the test framework."""
    
    # Base URLs
    GOOGLE_URL = "https://www.google.com"
    
    # Timeouts (in milliseconds)
    DEFAULT_TIMEOUT = 30000
    ELEMENT_TIMEOUT = 10000
    PAGE_LOAD_TIMEOUT = 30000
    
    # Browser settings
    BROWSER_OPTIONS = {
        "headless": True,
        "args": [
            "--start-maximized",
            "--disable-blink-features=AutomationControlled",
            "--disable-extensions",
        ]
    }
    
    # Test data
    SEARCH_TERMS = {
        "MCP": "MCP",
        "PLAYWRIGHT": "Playwright",
        "PYTHON": "Python programming"
    }
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORTS_DIR = os.path.join(BASE_DIR, "reports")
    SCREENSHOTS_DIR = os.path.join(REPORTS_DIR, "screenshots")
    
    @classmethod
    def create_directories(cls) -> None:
        """Create necessary directories if they don't exist."""
        os.makedirs(cls.REPORTS_DIR, exist_ok=True)
        os.makedirs(cls.SCREENSHOTS_DIR, exist_ok=True)
    
    @classmethod
    def get_screenshot_path(cls, test_name: str) -> str:
        """Get screenshot path for a test."""
        cls.create_directories()
        return os.path.join(cls.SCREENSHOTS_DIR, f"{test_name}.png")
    
    @classmethod
    def get_browser_options(cls, browser_name: str = "chromium") -> Dict[str, Any]:
        """Get browser-specific options."""
        options = cls.BROWSER_OPTIONS.copy()
        
        if browser_name == "firefox":
            # Firefox-specific options
            options["args"].extend([
                "--width=1920",
                "--height=1080"
            ])
        elif browser_name == "webkit":
            # WebKit-specific options
            pass
        
        return options
