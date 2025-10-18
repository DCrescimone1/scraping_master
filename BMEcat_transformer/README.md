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
- **XML UDX specs extraction** from Original XML (`UDX.EDXF.*` fields)
- **AI-powered feature matching** (optional, via Grok) maps unstructured XML text to structured features

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
SCRAPED_TEXT_DIR=outputs/scraped_text/  # NEW: Directory for intermediate text extraction

# Optional: Enable AI-powered XML specs extraction/matching
GROK_API_KEY=xa-your-key
GROK_MODEL=grok-4-fast-reasoning
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

## Product ID Extraction

The system extracts product identifiers from BMEcat XML files with the following priority:

1. **SUPPLIER_AID** (checked first)
2. **SUPPLIER_PID** (fallback if AID not found)

Both tags are treated as equivalent product identifiers. The extractor:
- Uses regex for robustness with malformed XML
- Deduplicates automatically
- Preserves order of first appearance
- Works with or without XML namespaces

**Example XML tags recognized:**
```xml
<SUPPLIER_AID>207603216S</SUPPLIER_AID>
<SUPPLIER_PID>DCG405NT-XJ</SUPPLIER_PID>
```

Note: Variable names in code still use `SUPPLIER_PID` for backward compatibility.

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
├── outputs/
│   ├── scraped_text/ # Intermediate UDX XML text extraction
│   │   ├── DCG405NT-XJ.txt # Human-readable text per product
│   │   └── [product_id].txt # Organized by section headers
│   ├── comparison_tables/
│   │   ├── DCG405NT-XJ_de.json
│   │   └── master_comparison_catalog.json
│   ├── ai_generated_features.json # AI-discovered features (not in CSV)
│   ├── unique_features.csv # Feature taxonomy (German/French/Italian)
│   └── master_bmecat_dabag.json # Master product database
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
- `pyyaml>=6.0.1` (AI prompt configuration)

## Logging

The project uses a centralized logging system via `utils/logger.py`.

**Usage:**
```python
from utils.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Information message")
logger.debug("Debug message")
logger.warning("Warning message")
logger.error("Error message")
```

**Log Levels:**
- DEBUG: Detailed diagnostic information
- INFO: General informational messages (default)
- WARNING: Warning messages
- ERROR: Error messages

**Configuration:**
- Logs are written to stdout by default.
- To enable file logging:
```python
logger = setup_logger(__name__, log_file="logs/app.log")
```

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

## Comparison Table Generation

Generate comparison tables merging Original XML (DEWALT), DABAG XML (multi-language), web-scraped data (from master JSON), and AI mappings (placeholder).

### Usage

```bash
python3 scripts/create_comparison_tables.py \
  --original data/DEWALT_BMEcat_Original.xml \
  --dabag data/DEWALT_Version_DABAG.xml

# With auto-scraping
python3 scripts/create_comparison_tables.py \
  --original data/DEWALT_BMEcat_Original.xml \
  --dabag data/DEWALT_Version_DABAG.xml \
  --auto-scrape
```

### Input Requirements

- `original_xml`: BMEcat XML (original source). Features read from `FDESCR`, `FVALUE`, `FUNIT` per `<FEATURE>` within `<PRODUCT>` by `SUPPLIER_PID`.
- `dabag_xml`: BMEcat XML (DABAG enriched). Features read per language via `FNAME lang=deu|fra|ita`, `FVALUE lang=...`, and `FUNIT`.
- Optional `--auto-scrape`: If enabled, missing `SUPPLIER_PID`s in the master JSON will be scraped using `scrapers/dabag_scraper.py` and appended/updated.

### Output

- Individual tables:
  - Directory: `outputs/comparison_tables/`
  - File: `comparison_{supplier_id}_{lang}.json`
  - Columns: `original_fname, original_fvalue, dabag_fname, dabag_fvalue, web_fname, web_fvalue, ai_fname, ai_fvalue`
  - Units are saved separately per row (`original_funit`, `dabag_funit`).
- Master catalog:
  - File: `outputs/comparison_tables/master_comparison_catalog.json`
  - Structure:

```json
{
  "products": {
    "SUPPLIER_PID": {
      "languages": {
        "de": { "columns": [...], "rows": [...], "units": [...] },
        "fr": { "columns": [...], "rows": [...], "units": [...] },
        "it": { "columns": [...], "rows": [...], "units": [...] }
      }
    }
  }
}
```

### Example

After running the command, expect per-language files like:

```
outputs/comparison_tables/comparison_123456_de.json
outputs/comparison_tables/comparison_123456_fr.json
outputs/comparison_tables/comparison_123456_it.json

and a consolidated:

```
outputs/comparison_tables/master_comparison_catalog.json
```

## Scraped Text Files

**Directory:** `outputs/scraped_text/`

**Purpose:** Intermediate UDX XML text extraction for AI processing.

**Files:** One `.txt` file per product (German only)
- **Naming:** `{supplier_pid}.txt`
- **Format:** Human-readable text organized by section headers

**Sections:**
- `PRODUKTSTÄRKEN` (Product strengths)
- `LIEFERUMFANG` (Scope of delivery)
- `TECHNISCHE DATEN` (Technical data)
- `GARANTIE` (Warranty)
- `ANWENDUNGSBEISPIELE` (Application examples)

**Usage:** Automatically generated during XML specs extraction. Used as input for AI feature matching.

**Behavior:** Files are overwritten on each run to stay synchronized with XML changes.

**Example File Content:**
```
Product: DCG405NT-XJ
Extracted from: Original XML (DEWALT BMEcat)

=== PRODUKTSTÄRKEN ===
Brushless motor for extended runtime and durability.
Variable speed for optimal performance.

=== TECHNISCHE DATEN ===
Max. disc diameter: 125 mm
No-load speed: 9000 min⁻¹
```

## XML Specs Extractor

**File:** `processors/xml_specs_extractor.py`

**Purpose:** Extracts unstructured technical specifications from `UDX.EDXF.*` XML fields for AI processing.

**Key Features:**
- **Multi-strategy parsing:** Uses fallback approach for maximum reliability
  1. lxml with recovery mode (handles malformed XML)
  2. Standard ElementTree parsing (fallback)
  3. Regex extraction (fallback for severe XML errors)
- **HTML entity decoding:** Converts `&lt;br&gt;` to readable format
- **Field mapping:** Configurable via `config.UDX_FIELD_MAPPING`

**Extracted Fields:**
- `UDX.EDXF.LANGTEXT` (Product strengths)
- `UDX.EDXF.TECHNISCHE_DATEN` (Technical data)
- `UDX.EDXF.LIEFERUMFANG` (Scope of delivery)
- `UDX.EDXF.GARANTIEBEDINGUNGEN` (Warranty conditions)
- `UDX.EDXF.ANWENDUNGSBEISPIELE` (Application examples)

**Usage:**
```python
from processors.xml_specs_extractor import XMLSpecsExtractor

extractor = XMLSpecsExtractor("path/to/original.xml")
if extractor.load_xml():
    udx_data = extractor.extract_all_products(config.UDX_FIELD_MAPPING)
    # Returns: {supplier_pid: {field_name: text, ...}, ...}
```

**Recent Changes:**
- **2025-10-17:** Enhanced with multi-strategy parsing (lxml → ET → regex fallback) to handle malformed XML
