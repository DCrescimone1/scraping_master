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
MASTER_COMPARISON_FILENAME: str = os.getenv(
    "MASTER_COMPARISON_FILENAME",
    "master_comparison_catalog.json"
)

# Master JSON settings
MASTER_JSON_FILENAME: str = os.getenv("MASTER_JSON_FILENAME", "master_bmecat_dabag.json")
MASTER_JSON_BACKUP_COUNT: int = int(os.getenv("MASTER_JSON_BACKUP_COUNT", "2"))

# Optional keys depending on method
FIRECRAWL_API_KEY: str | None = os.getenv("FIRECRAWL_API_KEY")

# Validation
if SCRAPING_METHOD not in {"firecrawl", "playwright"}:
    raise ValueError(
        "SCRAPING_METHOD must be either 'firecrawl' or 'playwright'"
    )

if SCRAPING_METHOD == "firecrawl" and not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables for firecrawl mode")

# Normalize directories to have trailing slash
if not OUTPUT_DIR.endswith("/"):
    OUTPUT_DIR = OUTPUT_DIR + "/"
if not COMPARISON_TABLES_DIR.endswith("/"):
    COMPARISON_TABLES_DIR = COMPARISON_TABLES_DIR + "/"

