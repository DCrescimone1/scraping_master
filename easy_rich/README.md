# Enhanced Generic Web Scraper

Search for content on the web or scrape any direct URL, then interactively explore and scrape same‑domain subpages. Results are organized into session folders with clean Markdown and structured JSON.

## Features

- **Dual Mode Operation**: Choose between web search or direct URL input
- **Subpage Exploration**: Automatically extract and explore links from scraped pages
- **Session Management**: Organize multiple scraped pages in per‑session folders
- **Domain Filtering**: Only show subpages from the same domain
- **Smart File Organization**: Automatic file naming and folder structure
- **SerpAPI Integration**: Reliable search results when using Search Mode
- **Advanced Web Scraping (Firecrawl)**: Handles JS‑heavy pages and anti‑bot protections
- **Clean Markdown + JSON**: Human‑readable Markdown and structured JSON outputs

## Usage

1. Run the application:
   ```bash
   python easy_rich/main.py
   ```

2. Choose your mode:
   - Search Mode: Enter search text (required) and optionally a website (e.g., `imdb.com`). The app finds a relevant URL and scrapes it.
   - Direct URL Mode: Enter any URL to scrape directly (e.g., `https://example.com/page`).

3. After scraping the initial page, you’ll see a numbered list of same‑domain subpages found on the page:
   - Enter a number to scrape that subpage
   - Enter `n` to start a new search or URL
   - Enter `q` to quit

## Requirements

- Python 3.8+
- SerpAPI account and API key
- Firecrawl account and API key
- Required packages: `requests`, `python-dotenv`, `firecrawl-py`

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a root‑level `.env` file with:
   ```env
   SERP_API_KEY=your-serpapi-key-here
   FIRECRAWL_API_KEY=your-firecrawl-key-here
   ```

3. Run the scraper:
   ```bash
   python easy_rich/main.py
   ```

## Output

Each run creates a session folder named like `domain_YYYYMMDD_HHMMSS/` containing all scraped content:

- Markdown Files: Clean, readable content with metadata
- JSON Files: Structured data extracted from pages

Example session structure:

```
imdb_com_20250926_143022/
├── toy_story_2_results.md
├── toy_story_2_results_data.json
├── subpage_cast_crew.md
├── subpage_cast_crew_data.json
└── subpage_reviews.md
```
