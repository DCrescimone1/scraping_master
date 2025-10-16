"""Standalone script to extract unique feature names from master JSON.

Usage:
    python3 extract_features.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.feature_extractor import FeatureExtractor


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
