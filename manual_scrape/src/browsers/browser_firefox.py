"""Firefox browser implementation."""

from typing import List

class FirefoxBrowser:
    """Firefox browser configuration and launch handler."""

    name = "firefox"

    def get_launch_args(self) -> List[str]:
        """Get Firefox-specific launch arguments optimized for stealth."""
        return [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--no-first-run',
            '--disable-default-browser-check',
            '--disable-infobars'
        ]

    def launch(self, playwright_instance, headless: bool = False):
        """Launch Firefox browser with stealth configuration."""
        print(f"🚀 Launching Firefox browser (headless: {headless})")
        print(f"🔧 Firefox launch args: {self.get_launch_args()}")
        
        try:
            browser = playwright_instance.firefox.launch(
                headless=headless,
                args=self.get_launch_args()
            )
            print(f"✅ Firefox browser launched successfully")
            return browser
        except Exception as e:
            print(f"❌ Failed to launch Firefox browser: {e}")
            raise

    def get_user_agents(self) -> List[str]:
        """Get Firefox-compatible user agents."""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
        ]

    def add_human_behavior(self, page):
        """Add realistic human behavior including mouse movement."""
        import random
        # Random mouse movement
        page.mouse.move(
            random.randint(100, 800),
            random.randint(100, 600)
        )
        page.wait_for_timeout(random.randint(800, 2000))
