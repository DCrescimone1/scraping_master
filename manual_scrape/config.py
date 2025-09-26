"""
Configuration settings for the Generic Web Scraper.
"""

# Proxy Settings
DEFAULT_PROXY_MODE = "auto"  # "auto", "basic", "stealth"
MANUAL_STEALTH_OVERRIDE = False  # Force stealth from start if True

# Cost Management  
STEALTH_COST_WARNING = True
STEALTH_CREDITS_COST = 5

# Bot Detection
BOT_DETECTION_CODES = [401, 403, 500]

# Terminal Messages
STEALTH_WARNING_MSG = "💰 Stealth mode costs {} credits per request"
BOT_DETECTED_MSG = "❌ Bot detected (Status: {})"
STEALTH_PROMPT_MSG = "🤔 Try stealth mode? [y/N]: "
STEALTH_TRYING_MSG = "🥷 Trying stealth mode..."

# Browser Configuration
BROWSER = {
    'default': 'firefox',  # Options: 'chromium', 'firefox'
    'engines': {
        'chromium': {
            'timeout': 30000,
            'stealth_mode': True
        },
        'firefox': {
            'timeout': 30000,
            'stealth_mode': True
        }
    }
}
