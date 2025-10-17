from __future__ import annotations

"""Create comparison tables from Original XML, DABAG XML, and web master JSON.

Usage:
    python3 scripts/create_comparison_tables.py \
      --original path/to/DEWALT_BMEcat_Original.xml \
      --dabag path/to/DEWALT_Version_DABAG.xml \
      [--auto-scrape]
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Add project root for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Local imports
import config  # type: ignore
from core.comparison_table_builder import ComparisonTableBuilder  # type: ignore
from output.output_formatter import OutputFormatter  # type: ignore
from utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate comparison tables from Original and DABAG BMEcat XMLs",
    )
    parser.add_argument(
        "--original",
        required=True,
        help="Path to Original BMEcat XML file (e.g., DEWALT_BMEcat_Original.xml)",
    )
    parser.add_argument(
        "--dabag",
        required=True,
        help="Path to DABAG BMEcat XML file (e.g., DEWALT_Version_DABAG.xml)",
    )
    parser.add_argument(
        "--auto-scrape",
        action="store_true",
        help="Automatically scrape missing supplier IDs from web",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    
    # Initialize logging
    logger = setup_logger(__name__)

    original_xml_path = Path(args.original)
    dabag_xml_path = Path(args.dabag)

    if not original_xml_path.exists() or not original_xml_path.is_file():
        print(f"❌ Original XML not found or not a file: {original_xml_path}")
        sys.exit(1)
    if not dabag_xml_path.exists() or not dabag_xml_path.is_file():
        print(f"❌ DABAG XML not found or not a file: {dabag_xml_path}")
        sys.exit(1)

    print("=" * 80)
    print("BMEcat_transformer - Comparison Table Generation")
    print("=" * 80)

    builder = ComparisonTableBuilder(
        original_xml_path=str(original_xml_path),
        dabag_xml_path=str(dabag_xml_path),
    )

    merged = builder.build_comparison_tables(auto_scrape=bool(args.auto_scrape))

    formatter = OutputFormatter(output_dir=config.OUTPUT_DIR)

    # Format and save per-product per-language tables
    saved_files: List[str] = []
    formatted_tables: List[Dict[str, Any]] = []

    for supplier_id, data in merged.items():
        for lang in ["de", "fr", "it"]:
            table = formatter.format_comparison_table(data, supplier_id, lang)
            formatted_tables.append(table)
            path = formatter.save_comparison_table(table)
            saved_files.append(path)

    # Save master comparison catalog
    master_path = formatter.save_master_comparison_catalog(formatted_tables)

    # Display summary
    print("\n" + "=" * 80)
    print("Comparison Table Generation Summary")
    print("-" * 80)
    print(f"Products processed: {len(merged)}")
    print(f"Tables created: {len(saved_files)}")
    print(f"Master catalog: {master_path}")
    print("-" * 80)


if __name__ == "__main__":
    main()
