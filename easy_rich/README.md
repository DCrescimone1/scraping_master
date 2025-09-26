# Generic Web Scraper

A Python-based web scraping tool that allows users to search for content on specific websites or the entire web using SerpAPI and scrape the resulting pages.

## Features

- **Flexible Search**: Search for any text on any website or the entire web
- **User Input**: Interactive terminal prompts for search parameters
- **SerpAPI Integration**: Uses SerpAPI for reliable search results
- **Web Scraping**: Extracts and saves full page content
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
- Save the content as an HTML file

## Requirements

- Python 3.x
- SerpAPI key (set in `.env` file as `SERP_API_KEY`)
- Required packages: `requests`, `beautifulsoup4`, `python-dotenv`

## Configuration

Set your SerpAPI key in a root-level `.env` file:

```env
SERP_API_KEY=your_api_key_here
```

## Output

Scraped content is saved as `{search_text}_results.html` in the project directory.
