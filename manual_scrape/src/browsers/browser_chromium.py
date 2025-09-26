"""Chromium browser implementation."""

from typing import List

class ChromiumBrowser:
    """Chromium browser configuration and launch handler."""

    name = "chromium"

    def get_launch_args(self) -> List[str]:
        """Get Chromium-specific launch arguments optimized for stealth."""
        return [
            '--no-sandbox',
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--no-first-run',
            '--force-device-scale-factor=1',
            '--disable-default-apps'
        ]

    def launch(self, playwright_instance, headless: bool = True):
        """Launch Chromium browser with stealth configuration."""
        print(f"🚀 Launching Chromium browser (headless: {headless})")
        print(f"🔧 Chromium launch args: {self.get_launch_args()}")
        
        try:
            browser = playwright_instance.chromium.launch(
                headless=headless,
                args=self.get_launch_args()
            )
            print(f"✅ Chromium browser launched successfully")
            return browser
        except Exception as e:
            print(f"❌ Failed to launch Chromium browser: {e}")
            raise

    def get_user_agents(self) -> List[str]:
        """Get Chromium-compatible user agents."""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
