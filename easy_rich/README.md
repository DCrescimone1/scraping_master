# Generic Web Scraper

A Python-based web scraping tool that allows users to search for content on specific websites or the entire web using SerpAPI and scrape the resulting pages.

## Features

- **Flexible Search**: Search for any text on any website or the entire web
- **User Input**: Interactive terminal prompts for search parameters
- **SerpAPI Integration**: Uses SerpAPI for reliable search results
- **Advanced Web Scraping (Firecrawl)**: Handles JavaScript-heavy pages and anti-bot protection
- **Clean Markdown Extraction**: Saves readable content as Markdown (.md)
- **Structured Data Extraction**: Saves key information as JSON (.json)
- **Error Handling**: Robust error handling and validation

## Usage

1. Run the application:
   ```bash
   python easy_rich/main.py
   ```

2. Enter your search parameters when prompted:
   - Search text (required): What you want to search for
   - Website (optional): Specific website to search on (e.g., "imdb.com", "wikipedia.org")

The scraper will:
- Search using SerpAPI
- Find the first relevant result
- Scrape the page content
- Save the content as Markdown and JSON files

## Requirements

- Python 3.x
- SerpAPI key (set in `.env` file as `SERP_API_KEY`)
- Firecrawl API key (set in `.env` file as `FIRECRAWL_API_KEY`)
- Required packages: `requests`, `python-dotenv`, `firecrawl-py`

## Configuration

Create a root-level `.env` file with the following variables:

```env
SERP_API_KEY=your_serpapi_key_here
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
```

## Output

Scraped content is saved in the project directory as:

- `{search_text}_results.md` — Clean Markdown content
- `{search_text}_results_data.json` — Structured data (title, status code, extracted fields)
