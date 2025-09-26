# Enhanced Generic Web Scraper
## Features
- **Dual Mode Operation**: Choose between web search or direct URL input
- **Subpage Exploration**: Automatically extract and explore links from scraped pages
- **Session Management**: Organize multiple scraped pages in per-session folders
- **Domain Filtering**: Only show subpages from the same domain
- **Smart File Organization**: Automatic file naming and folder structure
- **SerpAPI Integration**: Reliable search results when using Search Mode
- **Advanced Web Scraping (Playwright)**: Handles JS-heavy pages and anti-bot protections
- **Clean Markdown + JSON**: Human-readable Markdown and structured JSON outputs

## New Features

### Stealth Proxy Support
The scraper now includes automatic bot detection and stealth proxy fallback:

- **Auto Detection**: Monitors for bot blocking (status codes 401, 403, 500)
- **Manual Approval**: Prompts user before using stealth mode (costs 5 credits)
- **Per-scrape Decision**: Each blocked request gets individual stealth confirmation
- **Session Override**: Option to enable stealth mode for entire session

### Configuration
Modify `config.py` to customize:
- `DEFAULT_PROXY_MODE` : Set default proxy behavior ("auto", "basic", "stealth")
- `STEALTH_COST_WARNING` : Enable/disable cost warnings
- `BOT_DETECTION_CODES` : Customize detection status codes

### Usage
1. Run normally - stealth prompts appear when bot detection occurs
2. Choose option 3 at startup to enable session-wide stealth mode
3. Costs are clearly displayed before stealth attempts

## Usage

1. Run the application:
    ```bash
    python easy_rich/main.py
    ```
2. Choose your mode:
    - Search Mode: Enter search text (required) and optionally a website (e.g., `imdb.com`). The app finds a relevant URL and scrapes it.
    - Direct URL Mode: Enter any URL to scrape directly (e.g., `https://example.com/page`).

3. After scraping the initial page, you’ll see a numbered list of same-domain subpages found on the page:
    - Enter a number to scrape that subpage
    - Enter `n` to start a new search or URL
    - Enter `q` to quit

## Requirements

- Python 3.8+
- SerpAPI account and API key
- Required packages: `requests`, `python-dotenv`, plus Playwright dependencies listed in `manual_scrape/requirements.txt`

## Setup

1. Install dependencies:
   ```bash
   pip install -r manual_scrape/requirements.txt
   ```

2. Create a root‑level `.env` file with:
   ```env
   SERP_API_KEY=your-serpapi-key-here
   ```

3. Install Playwright browsers (first time only):
   ```bash
   ./manual_scrape/install_browsers.sh
   ```

4. Run the scraper:
   ```bash
   python manual_scrape/main.py
   ```

## Output

Each run creates a session folder named like `domain_YYYYMMDD_HHMMSS/` containing all scraped content:

- Markdown Files: Clean, readable content with metadata
- JSON Files: Structured data extracted from pages

Example session structure:
```

## Manual Scraping with Playwright

This version uses Playwright for robust web scraping with anti-bot capabilities.

### Browser Configuration
Configure browser in `config.py`:
```python
BROWSER = {
    'default': 'firefox',  # or 'chromium'
}
```

### Additional Features
- Anti-bot detection: Stealth-friendly launch args, popup handling, human-like behavior
- Multiple browsers: Firefox (default) and Chromium support
- Session management: Organized file storage by search session
- Content extraction: Advanced content parsing and validation

**✅ All requirements fulfilled, ready for testing!**
