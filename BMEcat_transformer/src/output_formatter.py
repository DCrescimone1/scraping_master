"""Output formatter for BMEcat_transformer.

- Pretty-prints per-product, per-language specification tables to terminal.
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

# Import config from the module root (BMEcat_transformer)
MODULE_ROOT = Path(__file__).resolve().parent.parent
if str(MODULE_ROOT) not in sys.path:
    sys.path.append(str(MODULE_ROOT))
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
        """Print tables for each product.

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

    def save_to_json(self, results: Dict[str, Dict[str, Any]], filename: str | None = None) -> str:
        """Save results to a timestamped JSON file in the output directory.

        Args:
            results: The complete results dict.
            filename: Optional base filename without extension.

        Returns:
            The full path of the saved JSON file.
        """
        ts = time.strftime("%Y%m%d_%H%M%S")
        base = filename or f"bmecat_dabag_results_{ts}"
        path = os.path.join(self.output_dir, f"{base}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON: {path}")
        return path

    def display_summary(self, results: Dict[str, Dict[str, Any]]) -> None:
        """Print a summary of processed products and specs per language."""
        total_products = len(results)
        lang_counts = {"de": 0, "fr": 0, "it": 0}

        for data in results.values():
            langs = data.get("languages", {})
            for lang in lang_counts.keys():
                lang_counts[lang] += len(langs.get(lang, {}))

        print("\n" + "=" * 80)
        print("Summary")
        print("-" * 80)
        print(f"Total products processed: {total_products}")
        print(f"Total specs extracted - DE: {lang_counts['de']}, FR: {lang_counts['fr']}, IT: {lang_counts['it']}")

