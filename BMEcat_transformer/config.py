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

# Optional keys depending on method
FIRECRAWL_API_KEY: str | None = os.getenv("FIRECRAWL_API_KEY")

# Validation
if SCRAPING_METHOD not in {"firecrawl", "playwright"}:
    raise ValueError(
        "SCRAPING_METHOD must be either 'firecrawl' or 'playwright'"
    )

if SCRAPING_METHOD == "firecrawl" and not FIRECRAWL_API_KEY:
    raise ValueError("FIRECRAWL_API_KEY not found in environment variables for firecrawl mode")

# Normalize OUTPUT_DIR to have trailing slash
if not OUTPUT_DIR.endswith("/"):
    OUTPUT_DIR = OUTPUT_DIR + "/"

