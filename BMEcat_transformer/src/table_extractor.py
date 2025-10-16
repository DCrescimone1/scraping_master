"""Table extractor for BMEcat_transformer.

Parses DABAG product pages' specification table into a dictionary mapping
label -> value. Designed to be resilient to minor HTML variations.
"""

from __future__ import annotations

from typing import Dict
from bs4 import BeautifulSoup  # type: ignore


class TableExtractor:
    """Extract specification tables from DABAG HTML content.

    Methods:
        extract_specs_table(html_content): Return dict of spec label -> value.
    """

    def __init__(self) -> None:
        """Initialize the extractor (no state required)."""
        pass

    def extract_specs_table(self, html_content: str) -> Dict[str, str]:
        """Extract specifications table from given HTML.

        The table is expected to have class
        "w-100 table table-striped m-0". Each row should contain two
        <td> cells: label and value.

        Args:
            html_content: Full HTML content of the product page.

        Returns:
            Dictionary mapping label -> value. Empty if table not found
            or on parse errors.
        """
        specs: Dict[str, str] = {}
        try:
            soup = BeautifulSoup(html_content or "", "html.parser")
            table = soup.find("table", class_="w-100 table table-striped m-0")
            if table is None:
                # Attempt a broader match if exact class chain changes order
                # or is partially applied by the site.
                candidate_tables = soup.find_all("table")
                for t in candidate_tables:
                    classes = set((t.get("class") or []))
                    needed = {"w-100", "table", "table-striped", "m-0"}
                    if needed.issubset(classes):
                        table = t
                        break

            if table is None:
                print("⚠️ Warning: Specification table not found in HTML.")
                return specs

            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue
                label = (tds[0].get_text(strip=True) or "").strip()
                value = (tds[1].get_text(strip=True) or "").strip()
                if label:
                    specs[label] = value

        except Exception as e:
            print(f"⚠️ Warning: Failed to parse specification table: {e}")
            return {}

        return specs

