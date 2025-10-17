#!/usr/bin/env python3
"""
Visualize BMEcat comparison tables in terminal or export to Excel/CSV.

Usage:
    python3 visualize_comparison_tables.py --product DCG405NT-XJ --lang de
    python3 visualize_comparison_tables.py --master  # Show all products
    python3 visualize_comparison_tables.py --product DT1953-QZ --lang fr --export excel
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
from tabulate import tabulate
import sys

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas not available. Excel export disabled.")


def load_comparison_table(product_id: str, lang: str, base_dir: str = "outputs/comparison_tables") -> Dict[str, Any]:
    """Load a single comparison table JSON file."""
    filepath = Path(base_dir) / f"comparison_{product_id}_{lang}.json"
    
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_master_catalog(base_dir: str = "outputs/comparison_tables") -> Dict[str, Any]:
    """Load the master comparison catalog."""
    filepath = Path(base_dir) / "master_comparison_catalog.json"
    
    if not filepath.exists():
        print(f"❌ Master catalog not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def visualize_table(data: Dict[str, Any], show_units: bool = True) -> None:
    """Pretty-print a comparison table to terminal."""
    supplier_id = data.get("supplier_id", "Unknown")
    lang = data.get("lang", "xx")
    url = data.get("product_url")
    
    print("\n" + "=" * 120)
    print(f"Product: {supplier_id} | Language: {lang.upper()}")
    if url:
        print(f"URL: {url}")
    print("=" * 120)
    
    rows = data.get("rows", [])
    units = data.get("units", [])
    
    if not rows:
        print("⚠️  No data rows found.")
        return
    
    # Build table data
    table_data = []
    headers = [
        "Feature",
        "Original Name", "Original Value",
        "DABAG Name", "DABAG Value",
        "Web Name", "Web Value",
        "AI Name", "AI Value"
    ]
    
    for i, row in enumerate(rows):
        # Get the primary feature name (first non-empty)
        fname = (row.get("original_fname") or 
                row.get("dabag_fname") or 
                row.get("web_fname") or 
                row.get("ai_fname", ""))
        
        table_row = [
            fname,
            row.get("original_fname", ""),
            row.get("original_fvalue", ""),
            row.get("dabag_fname", ""),
            row.get("dabag_fvalue", ""),
            row.get("web_fname", ""),
            row.get("web_fvalue", ""),
            row.get("ai_fname", ""),
            row.get("ai_fvalue", "")
        ]
        table_data.append(table_row)
    
    # Print main table
    print(tabulate(table_data, headers=headers, tablefmt="grid", maxcolwidths=[20, 15, 20, 15, 20, 15, 20, 15, 20]))
    
    # Print units if requested
    if show_units and units:
        print("\n" + "-" * 120)
        print("UNITS:")
        print("-" * 120)
        unit_data = []
        for u in units:
            if u.get("original_funit") or u.get("dabag_funit"):
                unit_data.append([
                    u.get("name", ""),
                    u.get("original_funit", ""),
                    u.get("dabag_funit", "")
                ])
        
        if unit_data:
            print(tabulate(unit_data, headers=["Feature", "Original Unit", "DABAG Unit"], tablefmt="simple"))
    
    # Print statistics
    print("\n" + "-" * 120)
    print("STATISTICS:")
    print("-" * 120)
    
    orig_count = sum(1 for r in rows if r.get("original_fvalue"))
    dabag_count = sum(1 for r in rows if r.get("dabag_fvalue"))
    web_count = sum(1 for r in rows if r.get("web_fvalue"))
    ai_count = sum(1 for r in rows if r.get("ai_fvalue"))
    
    print(f"Original features: {orig_count}")
    print(f"DABAG features: {dabag_count}")
    print(f"Web scraped features: {web_count}")
    print(f"AI mapped features: {ai_count}")
    print(f"Total unique features: {len(rows)}")


def export_to_excel(data: Dict[str, Any], output_path: str = None) -> None:
    """Export comparison table to Excel."""
    if not PANDAS_AVAILABLE:
        print("❌ pandas not installed. Run: pip install pandas openpyxl")
        return
    
    supplier_id = data.get("supplier_id", "unknown")
    lang = data.get("lang", "xx")
    
    if not output_path:
        output_path = f"comparison_{supplier_id}_{lang}.xlsx"
    
    rows = data.get("rows", [])
    units = data.get("units", [])
    
    # Create main dataframe
    df_main = pd.DataFrame(rows)
    
    # Reorder columns for readability
    col_order = [
        "original_fname", "original_fvalue",
        "dabag_fname", "dabag_fvalue",
        "web_fname", "web_fvalue",
        "ai_fname", "ai_fvalue"
    ]
    df_main = df_main[[c for c in col_order if c in df_main.columns]]
    
    # Create units dataframe
    df_units = pd.DataFrame(units)
    
    # Write to Excel with multiple sheets
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_main.to_excel(writer, sheet_name='Comparison', index=False)
        if not df_units.empty:
            df_units.to_excel(writer, sheet_name='Units', index=False)
        
        # Add metadata sheet
        metadata = pd.DataFrame({
            'Property': ['Supplier ID', 'Language', 'Product URL'],
            'Value': [supplier_id, lang, data.get("product_url", "N/A")]
        })
        metadata.to_excel(writer, sheet_name='Metadata', index=False)
    
    print(f"✅ Exported to Excel: {output_path}")


def export_to_csv(data: Dict[str, Any], output_path: str = None) -> None:
    """Export comparison table to CSV."""
    supplier_id = data.get("supplier_id", "unknown")
    lang = data.get("lang", "xx")
    
    if not output_path:
        output_path = f"comparison_{supplier_id}_{lang}.csv"
    
    rows = data.get("rows", [])
    
    if PANDAS_AVAILABLE:
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, encoding='utf-8')
    else:
        import csv
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
    
    print(f"✅ Exported to CSV: {output_path}")


def show_master_overview(catalog: Dict[str, Any]) -> None:
    """Display overview of all products in master catalog."""
    products = catalog.get("products", {})
    
    print("\n" + "=" * 80)
    print(f"MASTER COMPARISON CATALOG - {len(products)} Products")
    print("=" * 80)
    
    overview_data = []
    for supplier_id, product_data in products.items():
        languages = product_data.get("languages", {})
        
        de_features = len(languages.get("de", {}).get("rows", []))
        fr_features = len(languages.get("fr", {}).get("rows", []))
        it_features = len(languages.get("it", {}).get("rows", []))
        
        overview_data.append([
            supplier_id,
            de_features,
            fr_features,
            it_features,
            max(de_features, fr_features, it_features)
        ])
    
    print(tabulate(
        overview_data,
        headers=["Supplier ID", "DE Features", "FR Features", "IT Features", "Max"],
        tablefmt="grid"
    ))
    
    print("\n💡 To view a specific product:")
    print("   python3 visualize_comparison_tables.py --product <SUPPLIER_ID> --lang <de|fr|it>")


def main():
    parser = argparse.ArgumentParser(
        description="Visualize BMEcat comparison tables"
    )
    
    parser.add_argument(
        "--product",
        help="Supplier ID / product code (e.g., DCG405NT-XJ)"
    )
    
    parser.add_argument(
        "--lang",
        choices=["de", "fr", "it"],
        help="Language code"
    )
    
    parser.add_argument(
        "--master",
        action="store_true",
        help="Show master catalog overview"
    )
    
    parser.add_argument(
        "--export",
        choices=["excel", "csv"],
        help="Export to file format"
    )
    
    parser.add_argument(
        "--no-units",
        action="store_true",
        help="Hide units table"
    )
    
    parser.add_argument(
        "--output",
        help="Custom output filename for export"
    )
    
    parser.add_argument(
        "--dir",
        default="outputs/comparison_tables",
        help="Base directory for comparison tables"
    )
    
    args = parser.parse_args()
    
    # Show master overview
    if args.master:
        catalog = load_master_catalog(args.dir)
        show_master_overview(catalog)
        return
    
    # Validate product and lang
    if not args.product or not args.lang:
        print("❌ Error: --product and --lang are required (or use --master)")
        parser.print_help()
        sys.exit(1)
    
    # Load and visualize
    data = load_comparison_table(args.product, args.lang, args.dir)
    
    # Export if requested
    if args.export == "excel":
        export_to_excel(data, args.output)
    elif args.export == "csv":
        export_to_csv(data, args.output)
    else:
        # Default: terminal visualization
        visualize_table(data, show_units=not args.no_units)


if __name__ == "__main__":
    main()