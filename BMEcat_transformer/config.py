from __future__ import annotations

"""
Configuration settings for BMEcat_transformer.
Follows the style of existing configs in `doc_processor/` and `easy_rich/`.
"""

import os
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv()

# Scraping method selection: "firecrawl" or "playwright"
SCRAPING_METHOD: str = os.getenv("SCRAPING_METHOD", "firecrawl").strip().lower()

# DABAG settings
DABAG_BASE_URL: str = os.getenv("DABAG_BASE_URL", "https://www.dabag.ch")

# Language mapping for DABAG (de=1, fr=2, it=3)
LANGUAGES: dict[str, int] = {
    "de": 1,
    "fr": 2,
    "it": 3,
}

# Output directory for saved JSON
OUTPUT_DIR: str = os.getenv("BME_OUTPUT_DIR", "outputs/")

# Comparison tables output directory and master filename
# Default COMPARISON_TABLES_DIR nests under OUTPUT_DIR
COMPARISON_TABLES_DIR: str = os.getenv(
    "COMPARISON_TABLES_DIR",
    os.path.join(OUTPUT_DIR, "comparison_tables/")
)
# Scraped text output directory for intermediate UDX XML text extraction
SCRAPED_TEXT_DIR: str = os.getenv(
    "SCRAPED_TEXT_DIR",
    os.path.join(OUTPUT_DIR, "scraped_text/")
)
MASTER_COMPARISON_FILENAME: str = os.getenv(
    "MASTER_COMPARISON_FILENAME",
    "master_comparison_catalog.json"
)

# Master JSON settings
MASTER_JSON_FILENAME: str = os.getenv("MASTER_JSON_FILENAME", "master_bmecat_dabag.json")
MASTER_JSON_BACKUP_COUNT: int = int(os.getenv("MASTER_JSON_BACKUP_COUNT", "2"))

# Grok AI Configuration for XML Specs Extraction
GROK_API_KEY: str | None = os.getenv("GROK_API_KEY")
GROK_MODEL: str = os.getenv("GROK_MODEL", "grok-4-fast-reasoning")
GROK_BASE_URL: str = "https://api.x.ai/v1"
GROK_CONFIDENCE_THRESHOLD: float = 0.70

# AI Generated Features Management
AI_FEATURES_FILENAME: str = "ai_generated_features.json"
AI_FEATURES_PATH: str = os.path.join(OUTPUT_DIR, AI_FEATURES_FILENAME)

# UDX XML Fields Mapping
UDX_FIELD_MAPPING: dict[str, str] = {
    "produktstaerken": "UDX.EDXF.LANGTEXT",
    "lieferumfang": "UDX.EDXF.LIEFERUMFANG",
    "technische_daten": "UDX.EDXF.TECHNISCHE_DATEN",
    "garantie": "UDX.EDXF.GARANTIEBEDINGUNGEN",
    "anwendungsbeispiele": "UDX.EDXF.ANWENDUNGSBEISPIELE"
}

# Optional keys depending on method
FIRECRAWL_API_KEY: str | None = os.getenv("FIRECRAWL_API_KEY")

# Validation
if SCRAPING_METHOD not in {"firecrawl", "playwright"}:
    raise ValueError(
        "SCRAPING_METHOD must be either 'firecrawl' or 'playwright'"
    )

if SCRAPING_METHOD == "firecrawl" and not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables for firecrawl mode")

# Grok validation
if GROK_API_KEY:
    print(f"✅ Grok API configured: {GROK_MODEL}")

# Normalize directories to have trailing slash
if not OUTPUT_DIR.endswith("/"):
    OUTPUT_DIR = OUTPUT_DIR + "/"
if not COMPARISON_TABLES_DIR.endswith("/"):
    COMPARISON_TABLES_DIR = COMPARISON_TABLES_DIR + "/"
if not SCRAPED_TEXT_DIR.endswith("/"):
    SCRAPED_TEXT_DIR = SCRAPED_TEXT_DIR + "/"
