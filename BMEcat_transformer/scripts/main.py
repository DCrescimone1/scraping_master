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

# Add parent directory to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from scrapers.dabag_scraper import DABAGScraper
from output.output_formatter import OutputFormatter
from core.input_handler import InputHandler
from core.master_json_manager import MasterJSONManager
from ui.user_prompt import UserPrompt


def get_input_path() -> str:
    """Get input file path from command-line args or prompt user.

    Returns:
        Validated path string to input file.
    """
    path: str | None = None
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("Enter path to BMEcat XML file: ").strip()

    if not path:
        print("⚠️ No input file path provided.")
        sys.exit(1)

    p = Path(path)
    if not p.exists() or not p.is_file():
        print(f"⚠️ Input file path does not exist or is not a file: {path}")
        sys.exit(1)
    return str(p)


def main() -> None:
    start = time.time()
    print("=" * 80)
    print("BMEcat_transformer - DABAG Spec Scraper")
    print(f"Scraping method: {config.SCRAPING_METHOD}")
    print("=" * 80)

    input_path = get_input_path()

    # Extract product IDs
    SUPPLIER_PIDs = InputHandler.load_supplier_ids(input_path)
    print(f"Found {len(SUPPLIER_PIDs)} SUPPLIER_PID(s) to process.")
    if not SUPPLIER_PIDs:
        print("Nothing to do. Exiting.")
        return

    # Initialize master JSON manager
    master_manager = MasterJSONManager(
        master_filename=config.MASTER_JSON_FILENAME,
        output_dir=config.OUTPUT_DIR,
        backup_count=config.MASTER_JSON_BACKUP_COUNT
    )
    master_manager.load()

    # Show master JSON statistics
    stats = master_manager.get_statistics()
    print(f"\n📊 Master JSON Status:")
    print(f"  Total products: {stats['total_products']}")
    print(f"  Last updated: {stats['last_updated']}")
    print()

    scraper = DABAGScraper()
    results: Dict[str, Dict[str, Any]] = {}
    
    # Counters for summary
    new_count = 0
    updated_count = 0
    skipped_count = 0

    for idx, pid in enumerate(SUPPLIER_PIDs, 1):
        print("-" * 80)
        print(f"[{idx}/{len(SUPPLIER_PIDs)}] Processing SUPPLIER_PID: {pid}")

        # Check if ID exists in master JSON
        exists, existing_data = master_manager.check_id_exists(pid)

        if exists:
            # Show existing data WITHOUT scraping
            UserPrompt.show_existing_data(pid, existing_data)

            # Ask user for decision BEFORE scraping
            decision = UserPrompt.prompt_update_decision(pid)

            if decision == "update":
                # Only scrape if user wants to update
                try:
                    new_data = scraper.process_product(pid)
                    master_manager.update_product(pid, new_data)
                    results[pid] = new_data
                    updated_count += 1
                except Exception as e:
                    print(f"⚠️  Warning: Error processing {pid}: {e}")
                    results[pid] = existing_data  # Keep existing on error
            else:
                print(f"⏭️  Skipping {pid} (keeping existing data)")
                results[pid] = existing_data
                skipped_count += 1

        else:
            # New ID - scrape and append
            try:
                data = scraper.process_product(pid)
                master_manager.append_product(pid, data)
                results[pid] = data
                new_count += 1
            except Exception as e:
                print(f"⚠️  Warning: Error processing {pid}: {e}")
                results[pid] = {"SUPPLIER_PID": pid, "product_url": None, "languages": {}}

    # Save master JSON
    master_manager.save()

    # Display results and save timestamped export
    formatter = OutputFormatter(output_dir=config.OUTPUT_DIR)
    formatter.print_results(results)
    formatter.save_to_json(results)  # Keeps timestamped export functionality
    formatter.display_summary(results)

    # Display master JSON update summary
    print("\n" + "=" * 80)
    print("Master JSON Update Summary")
    print("-" * 80)
    print(f"New products added: {new_count}")
    print(f"Products updated: {updated_count}")
    print(f"Products skipped: {skipped_count}")
    print(f"Total in master: {master_manager.get_statistics()['total_products']}")
    print("-" * 80)

    elapsed = time.time() - start
    print(f"Elapsed time: {elapsed:.2f}s")


if __name__ == "__main__":
    main()
