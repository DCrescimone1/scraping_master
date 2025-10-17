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

From `BMEcat_transformer/` directory:

```bash
# Main scraper
python3 scripts/main.py /path/to/your_bmecat.xml

# Or JSON input with a simple array of SUPPLIER_PIDs
python3 scripts/main.py /path/to/manual_ids.json

# Feature extraction
python3 scripts/extract_features.py

# Testing imports
python3 test_imports.py
```

You can also run without args and enter the path when prompted.

### Input File Formats

- **XML Format**: Extracts `SUPPLIER_PID` values from BMEcat XML files (see `core/xml_reader.py` for details).
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

## Master JSON Tracking

The scraper maintains a persistent `master_bmecat_dabag.json` file in the `outputs/` directory that accumulates all scraped products across runs.

### How It Works

1. **First Run**: All products are scraped and added to the master JSON
2. **Subsequent Runs**:
   - If a product ID already exists, you'll see a comparison and be prompted to update or skip
   - New products are automatically added
   - Updates are tracked with timestamps

### Master JSON Structure

```json
{
  "metadata": {
    "created_at": "2025-10-16T10:00:00",
    "last_updated": "2025-10-16T14:30:00",
    "total_products": 150
  },
  "products": {
    "PRODUCT_ID": {
      "scraped_at": "2025-10-16T10:15:00",
      "updated_at": "2025-10-16T14:25:00",
      "product_url": "https://...",
      "languages": {
        "de": { },
        "fr": { },
        "it": { }
      }
    }
  }
}
```

### Backup System

- Automatically maintains 2 backup versions of the master JSON
- Backups are named: `master_bmecat_dabag.json.backup1` and `master_bmecat_dabag.json.backup2`
- Each save rotates backups automatically

### Per-Run Exports

In addition to the master JSON, each run still creates a timestamped export file (e.g., `bmecat_dabag_results_20251016_104334.json`) containing only the products processed in that specific run.

### Configuration

You can customize master JSON behavior in `.env`:

```bash
MASTER_JSON_FILENAME=master_bmecat_dabag.json
MASTER_JSON_BACKUP_COUNT=2
```

## Project Structure

```
BMEcat_transformer/
├── config.py
├── README.md
├── test_imports.py
│
├── scripts/
│   ├── main.py
│   └── extract_features.py
│
├── inputs/
│   └── example_supplier_ids.json
│
├── core/
│   ├── __init__.py
│   ├── input_handler.py
│   ├── xml_reader.py
│   └── master_json_manager.py
│
├── scrapers/
│   ├── __init__.py
│   ├── dabag_scraper.py
│   └── table_extractor.py
│
├── processors/
│   ├── __init__.py
│   └── feature_extractor.py
│
├── output/
│   ├── __init__.py
│   └── output_formatter.py
│
└── ui/
    ├── __init__.py
    └── user_prompt.py
```

## Dependencies

Managed at project root in `requirements.txt`:

- `beautifulsoup4`, `tabulate`, `requests`, `python-dotenv`
- `firecrawl-py` (for Firecrawl mode)
- `playwright` (for Playwright mode)

## 🔧 Feature Name Extractor

Extract a database of unique feature names (fname) across all languages from the master JSON.

### Purpose
Creates a reference CSV file showing how each product feature is named in German (de), French (fr), and Italian (it).

### Usage

```bash
cd BMEcat_transformer
python3 scripts/extract_features.py
```

### Output
- **File**: `outputs/unique_features.csv`
- **Format**: 6 columns (fname_de, fvalue_de, fname_fr, fvalue_fr, fname_it, fvalue_it)
- **Content**: Unique feature mappings with example values

### Example Output
```csv
fname_de,fvalue_de,fname_fr,fvalue_fr,fname_it,fvalue_it
Spannung,18 V,tension,18 V,tensione,18 V
Akku-Typ,--,type d'accu,--,tipo di batteria,--
```

### Notes
- Features are matched by position (assumes same order across languages)
- Only first occurrence is stored as example value
- Requires `master_bmecat_dabag.json` to exist (run main scraper first)

## Notes

- On Firecrawl mode, `FIRECRAWL_API_KEY` is required; otherwise startup will fail with a clear message.
- The tool continues processing other products/languages even when some steps fail, logging warnings.

