"""DABAG scraper for BMEcat_transformer.

Selects scraping backend based on config (firecrawl or playwright) to locate
product pages, then fetches product page HTML and extracts specification tables
for multiple languages.
"""

from __future__ import annotations

from typing import Dict, Optional
import sys
from pathlib import Path
from urllib.parse import urljoin
import requests

# Import config from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
import config  # type: ignore

# Import appropriate scraper based on config
PARENT_PROJECT = PROJECT_ROOT.parent
sys.path.append(str(PARENT_PROJECT))

if config.SCRAPING_METHOD == "firecrawl":
    from easy_rich.src.web_scraper import WebScraper  # type: ignore
elif config.SCRAPING_METHOD == "playwright":
    from manual_scrape.src.web_scraper import WebScraper  # type: ignore
else:  # Defensive
    from easy_rich.src.web_scraper import WebScraper  # type: ignore

# Local imports
from scrapers.table_extractor import TableExtractor


class DABAGScraper:
    """Search and scrape DABAG product pages in multiple languages."""

    def __init__(self) -> None:
        """Initialize scraper backend and table extractor."""
        try:
            self.scraper = WebScraper()
        except Exception as e:
            print(f"⚠️ Warning: Failed to initialize scraper backend: {e}")
            self.scraper = None
        self.table_extractor = TableExtractor()

    def search_product(self, SUPPLIER_PID: str) -> Optional[str]:
        """Search DABAG for a product and return the product detail URL.

        Args:
            SUPPLIER_PID: The product identifier to search.

        Returns:
            Full URL to the product detail page, or None if not found.
        """
        try:
            search_url = f"{config.DABAG_BASE_URL}/?q={SUPPLIER_PID}&srv=search"
            if not self.scraper:
                print("⚠️ Warning: Scraper not initialized; cannot perform search.")
                return None

            result = self.scraper.scrape_page(search_url)
            if not result:
                print(f"⚠️ Warning: Search failed for SUPPLIER_PID={SUPPLIER_PID}")
                return None

            markdown = result.get("markdown_content", "")
            # Reuse link extractor from the backend if available
            try:
                links = self.scraper.extract_links_from_markdown(markdown, search_url)  # type: ignore[attr-defined]
            except Exception:
                links = []

            # Find product detail link with expected pattern
            target: Optional[str] = None
            for _title, href in links:
                if "srv=search&pg=det&q=" in href:
                    target = href
                    break

            if not target:
                print(f"⚠️ Warning: Product detail link not found for SUPPLIER_PID={SUPPLIER_PID}")
                return None

            # Ensure full URL
            full_url = target if target.startswith("http") else urljoin(config.DABAG_BASE_URL, target)
            return full_url

        except Exception as e:
            print(f"⚠️ Warning: Error during product search for {SUPPLIER_PID}: {e}")
            return None

    def scrape_product_languages(self, base_url: str, SUPPLIER_PID: str) -> Dict[str, Dict[str, str]]:
        """Scrape product specs for all configured languages.

        Args:
            base_url: The base product detail page URL (likely in default language).
            SUPPLIER_PID: The product identifier for logging only.

        Returns:
            Mapping of language code (de/fr/it) to specs dict.
        """
        results: Dict[str, Dict[str, str]] = {}
        headers = {"User-Agent": "Mozilla/5.0 (compatible; BMEcatTransformer/1.0)"}

        for lang_code, lang_id in config.LANGUAGES.items():
            try:
                url = f"{base_url}&&&lngId={lang_id}"
                resp = requests.get(url, headers=headers, timeout=30)
                if resp.status_code >= 400:
                    print(f"⚠️ Warning: {lang_code.upper()} page HTTP {resp.status_code} for {SUPPLIER_PID}")
                    results[lang_code] = {}
                    continue

                html = resp.text
                specs = self.table_extractor.extract_specs_table(html)
                results[lang_code] = specs
            except Exception as e:
                print(f"⚠️ Warning: Failed to scrape {lang_code.upper()} for {SUPPLIER_PID}: {e}")
                results[lang_code] = {}

        return results

    def process_product(self, SUPPLIER_PID: str) -> Dict[str, object]:
        """Search and scrape a single product across languages.

        Returns a dict with structure:
        {
            "SUPPLIER_PID": str,
            "product_url": str | None,
            "languages": {"de": {...}, "fr": {...}, "it": {...}}
        }
        """
        product_url = self.search_product(SUPPLIER_PID)
        lang_data: Dict[str, Dict[str, str]] = {}
        if product_url:
            lang_data = self.scrape_product_languages(product_url, SUPPLIER_PID)
        else:
            print(f"⚠️ Warning: Skipping language scrape; no product URL for {SUPPLIER_PID}")

        return {
            "SUPPLIER_PID": SUPPLIER_PID,
            "product_url": product_url,
            "languages": lang_data,
        }

