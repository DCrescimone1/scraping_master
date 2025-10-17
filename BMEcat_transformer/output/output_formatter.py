"""Output formatter for BMEcat_transformer.

- Pretty-prints per-product, per-language specification tables to terminal.
- Displays stats for each product (specs per language)
- Saves complete results to JSON in configured output directory.
- Displays a processing summary.
"""

from __future__ import annotations

from typing import Dict, Any
import os
import time
import json
import sys
from pathlib import Path
from tabulate import tabulate  # type: ignore


# Import config from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
import config  # type: ignore


class OutputFormatter:
    """Format and output scraping results."""

    def __init__(self, output_dir: str | None = None) -> None:
        """Initialize with an output directory.

        Args:
            output_dir: Directory to save JSON outputs. Defaults to config.OUTPUT_DIR
        """
        self.output_dir = output_dir or config.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def print_results(self, results: Dict[str, Dict[str, Any]]) -> None:
        """Print tables for each product with per-language statistics.

        Args:
            results: Mapping of SUPPLIER_PID -> {"product_url": str|None, "languages": {de|fr|it: specs dict}}
        """
        for SUPPLIER_PID, data in results.items():
            print("\n" + "=" * 80)
            print(f"Product: {SUPPLIER_PID}")
            url = data.get("product_url")
            if url:
                print(f"URL: {url}")
            print("-" * 80)

            # Build row keys from union of all labels across languages
            langs = data.get("languages", {})
            labels = set()
            for lang_dict in langs.values():
                labels.update(lang_dict.keys())
            ordered_labels = sorted(labels)

            table_rows = []
            for label in ordered_labels:
                row = [label]
                row.append(langs.get("de", {}).get(label, ""))
                row.append(langs.get("fr", {}).get(label, ""))
                row.append(langs.get("it", {}).get(label, ""))
                table_rows.append(row)

            print(tabulate(table_rows, headers=["Spec Label", "DE", "FR", "IT"], tablefmt="grid"))
            
            # Add per-product statistics
            de_specs = len([v for v in langs.get("de", {}).values() if v and v.strip()])
            fr_specs = len([v for v in langs.get("fr", {}).values() if v and v.strip()])
            it_specs = len([v for v in langs.get("it", {}).values() if v and v.strip()])
            
            print(f"\n📊 Stats: DE: {de_specs} specs | FR: {fr_specs} specs | IT: {it_specs} specs")

    def save_to_json(self, results: Dict[str, Dict[str, Any]], filename: str | None = None) -> str:
        """Save results to a timestamped JSON file in the output directory.

        Args:
            results: The complete results dict.
            filename: Optional base filename without extension.

        Returns:
            The full path of the saved JSON file.
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"bmecat_dabag_results_{timestamp}.json"

        if not filename.endswith(".json"):
            filename += ".json"

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Saved JSON: {filepath}")
        return filepath

    def display_summary(self, results: Dict[str, Dict[str, Any]]) -> None:
        """Display a summary of the scraping session.

        Args:
            results: The complete results dict.
        """
        total_products = len(results)
        
        # Count total unique specs per language across all products
        all_de_specs = set()
        all_fr_specs = set()
        all_it_specs = set()
        
        for data in results.values():
            langs = data.get("languages", {})
            all_de_specs.update(langs.get("de", {}).keys())
            all_fr_specs.update(langs.get("fr", {}).keys())
            all_it_specs.update(langs.get("it", {}).keys())

        print("\n" + "=" * 80)
        print("Summary")
        print("-" * 80)
        print(f"Total products processed: {total_products}")
        print(f"Total unique spec fields - DE: {len(all_de_specs)}, FR: {len(all_fr_specs)}, IT: {len(all_it_specs)}")
        print("-" * 80)