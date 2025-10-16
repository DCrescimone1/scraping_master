# BMEcat_transformer – DABAG Spec Scraper

## Overview

Extracts product IDs (SUPPLIER_PID) from BMEcat XML files, searches DABAG.ch, scrapes product pages in DE/FR/IT, extracts specification tables, prints formatted tables in the terminal, and saves results to JSON for future XML transformation.

## Features

- **BMEcat SUPPLIER_PID extraction** from local XML files
- **Configurable scraping backend**: Firecrawl or Playwright
- **Multi-language scraping**: de, fr, it
- **Specification table parsing** via BeautifulSoup
- **Readable terminal tables** using `tabulate`
- **JSON output** saved to `outputs/`
- **Graceful error handling** with warnings

## Requirements

- Python 3.9+
- See project-level `requirements.txt` for dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set values in root `.env` and/or environment variables. See `BMEcat_transformer/config.py`.

Environment:

```bash
# Required for Firecrawl mode
FIRECRAWL_API_KEY=fc-your-key

# Optional overrides
SCRAPING_METHOD=firecrawl   # or: playwright
DABAG_BASE_URL=https://www.dabag.ch
BME_OUTPUT_DIR=outputs/
```

Selection logic:
- `SCRAPING_METHOD=firecrawl` → uses `easy_rich/src/web_scraper.py`
- `SCRAPING_METHOD=playwright` → uses `manual_scrape/src/web_scraper.py`

## Usage

From repo root or `BMEcat_transformer/`:

```bash
python3 BMEcat_transformer/main.py /path/to/your_bmecat.xml
```

JSON input is also supported with a simple array of SUPPLIER_PIDs:

```bash
python3 BMEcat_transformer/main.py /path/to/manual_ids.json
```

You can also run without args and enter the path when prompted.

### Input File Formats

- **XML Format**: Extracts `SUPPLIER_PID` values from BMEcat XML files (see `src/xml_reader.py` for details).
- **JSON Format**: Simple array of strings. Example:

```json
[
  "ID1",
  "ID2",
  "ID3"
]
```

## Output

- Terminal shows a per-product table with columns `[Spec Label, DE, FR, IT]`.
- A timestamped JSON file is saved to `outputs/`.

Example JSON structure:

```json
{
  "PROD123": {
    "SUPPLIER_PID": "PROD123",
    "product_url": "https://www.dabag.ch/?srv=search&pg=det&q=...",
    "languages": {
      "de": {"Leistung": "1200 W"},
      "fr": {"Puissance": "1200 W"},
      "it": {"Potenza": "1200 W"}
    }
  }
}
```

## Project Structure

```
BMEcat_transformer/
├── config.py                 # Settings & validation
├── main.py                   # Orchestrator
├── README.md                 # This file
└── src/
    ├── __init__.py
    ├── xml_reader.py         # Extracts SUPPLIER_PID from BMEcat XML
    ├── dabag_scraper.py      # Searches & scrapes DABAG in DE/FR/IT
    ├── table_extractor.py    # BeautifulSoup table parsing
    └── output_formatter.py   # Printing tables & JSON saving
```

## Dependencies

Managed at project root in `requirements.txt`:

- `beautifulsoup4`, `tabulate`, `requests`, `python-dotenv`
- `firecrawl-py` (for Firecrawl mode)
- `playwright` (for Playwright mode)

## Notes

- On Firecrawl mode, `FIRECRAWL_API_KEY` is required; otherwise startup will fail with a clear message.
- The tool continues processing other products/languages even when some steps fail, logging warnings.

