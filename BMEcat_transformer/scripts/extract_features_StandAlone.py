"""Standalone script to extract unique feature names from master JSON.
OVERVIEW:
This script analyzes the master product database (master_bmecat_dabag.json) 
and extracts all unique feature/specification field names across three languages 
(German, French, Italian). It creates a reference CSV that maps how the same 
feature is named in each language.

PURPOSE:
When scraping product specifications from DABAG, the same technical feature 
may have different names in different languages. For example:
  - German: "Leistung" 
  - French: "Puissance"
  - Italian: "Potenza"
  
This tool helps identify these cross-language mappings by analyzing position 
indices in the specification tables, assuming features appear in the same order 
across all language versions.

WORKFLOW:
1. Loads master_bmecat_dabag.json containing all scraped products
2. Iterates through all products and their multi-language specifications
3. Matches features by their position index (1st feature in DE = 1st in FR = 1st in IT)
4. Stores unique feature name combinations with example values
5. Exports to CSV for manual review and mapping

INPUT:
- File: master_bmecat_dabag.json (from outputs/ directory)
- Structure: JSON with products containing nested language-specific specs
- Example product structure:
  {
    "products": {
      "PROD123": {
        "languages": {
          "de": {"Leistung": "1200W", "Gewicht": "2.5kg"},
          "fr": {"Puissance": "1200W", "Poids": "2.5kg"},
          "it": {"Potenza": "1200W", "Peso": "2.5kg"}
        }
      }
    }
  }

OUTPUT:
- File: unique_features.csv (saved to outputs/ directory)
- Format: 6 columns showing feature names and example values:
  | fname_de | fvalue_de | fname_fr | fvalue_fr | fname_it | fvalue_it |
  |----------|-----------|----------|-----------|----------|-----------|
  | Leistung | 1200W     | Puissance| 1200W     | Potenza  | 1200W     |
  | Gewicht  | 2.5kg     | Poids    | 2.5kg     | Peso     | 2.5kg     |

USAGE:
    python3 extract_features.py

DEPENDENCIES:
- config.py: Contains OUTPUT_DIR and MASTER_JSON_FILENAME settings
- src/feature_extractor.py: Core extraction logic

NOTES:
- Features are matched by position, not by value matching
- Only the first occurrence of each unique feature combination is stored
- Empty/missing features in any language are preserved as empty strings
- The script requires master_bmecat_dabag.json to exist (run main scraper first)

"""

from __future__ import annotations

import sys
from pathlib import Path

# Add parent directory to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from processors.feature_extractor import FeatureExtractor


def main() -> None:
    """Run feature extraction."""
    # Construct master JSON path
    master_json_path = Path(config.OUTPUT_DIR) / config.MASTER_JSON_FILENAME
    
    if not master_json_path.exists():
        print(f"❌ Error: Master JSON not found at {master_json_path}")
        print(f"Please run the main scraper first to generate {config.MASTER_JSON_FILENAME}")
        sys.exit(1)
    
    # Run extractor
    extractor = FeatureExtractor(
        master_json_path=str(master_json_path),
        output_dir=config.OUTPUT_DIR
    )
    
    success = extractor.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
