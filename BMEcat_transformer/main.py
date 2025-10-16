"""Main entry point for BMEcat_transformer.

Pipeline:
- Parse XML path from args/user input
- Extract SUPPLIER_PIDs
- For each SUPPLIER_PID, search and scrape DABAG in DE/FR/IT
- Print tables, save JSON, display summary
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Dict, Any

import config
from src.xml_reader import XMLReader
from src.dabag_scraper import DABAGScraper
from src.output_formatter import OutputFormatter


def get_xml_path() -> str:
    """Get XML file path from command-line args or prompt user.

    Returns:
        Validated path string.
    """
    path: str | None = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("Enter path to BMEcat XML file: ").strip()

    if not path:
        print("⚠️ No XML path provided.")
        sys.exit(1)

    p = Path(path)
    if not p.exists() or not p.is_file():
        print(f"⚠️ XML path does not exist or is not a file: {path}")
        sys.exit(1)
    return str(p)


def main() -> None:
    start = time.time()
    print("=" * 80)
    print("BMEcat_transformer - DABAG Spec Scraper")
    print(f"Scraping method: {config.SCRAPING_METHOD}")
    print("=" * 80)

    xml_path = get_xml_path()

    # Extract product IDs
    reader = XMLReader(xml_path)
    SUPPLIER_PIDs = reader.extract_SUPPLIER_PIDs()
    print(f"Found {len(SUPPLIER_PIDs)} SUPPLIER_PID(s) to process.")
    if not SUPPLIER_PIDs:
        print("Nothing to do. Exiting.")
        return

    scraper = DABAGScraper()
    results: Dict[str, Dict[str, Any]] = {}

    for idx, pid in enumerate(SUPPLIER_PIDs, 1):
        print("-" * 80)
        print(f"[{idx}/{len(SUPPLIER_PIDs)}] Processing SUPPLIER_PID: {pid}")
        try:
            data = scraper.process_product(pid)
            results[pid] = data
        except Exception as e:
            print(f"⚠️ Warning: Error processing {pid}: {e}")
            results[pid] = {"SUPPLIER_PID": pid, "product_url": None, "languages": {}}

    formatter = OutputFormatter(output_dir=config.OUTPUT_DIR)
    formatter.print_results(results)
    formatter.save_to_json(results)
    formatter.display_summary(results)

    elapsed = time.time() - start
    print("-" * 80)
    print(f"Elapsed time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
