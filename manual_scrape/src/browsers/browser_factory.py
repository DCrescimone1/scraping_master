"""Factory class for creating browser instances."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import BROWSER

from .browser_chromium import ChromiumBrowser
from .browser_firefox import FirefoxBrowser

class BrowserFactory:
    """Factory class for creating browser instances."""

    _browsers = {
        'chromium': ChromiumBrowser,
        'firefox': FirefoxBrowser
    }

    @classmethod
    def create(cls, browser_name=None):
        """Create a browser instance based on configuration or specified name."""
        if browser_name is None:
            browser_name = BROWSER.get('default', 'firefox')
            print(f"🌐 Browser auto-selected from config: {browser_name}")
        else:
            print(f"🌐 Browser explicitly requested: {browser_name}")

        browser_class = cls._browsers.get(browser_name)
        if not browser_class:
            raise ValueError(f"Unsupported browser: {browser_name}. Available: {list(cls._browsers.keys())}")

        browser_instance = browser_class()
        print(f"✅ Browser instance created: {browser_instance.name}")
        return browser_instance

    @classmethod
    def get_available_browsers(cls):
        """Get list of available browser names."""
        return list(cls._browsers.keys())
    
    @classmethod
    def verify_browser_config(cls):
        """Verify current browser configuration and return details."""
        try:
            config_browser = BROWSER.get('default', 'firefox')
            print(f"📋 Config browser setting: {config_browser}")
            
            browser_instance = cls.create()
            print(f"📋 Actual browser created: {browser_instance.name}")
            
            return {
                'config_browser': config_browser,
                'actual_browser': browser_instance.name,
                'available_browsers': cls.get_available_browsers()
            }
        except Exception as e:
            print(f"❌ Browser config verification failed: {e}")
            return None
