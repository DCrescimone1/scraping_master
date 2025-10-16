"""Feature extractor for BMEcat_transformer.

Extracts unique feature names (fname) and example values (fvalue) from 
master_bmecat_dabag.json across all languages (de, fr, it).
Creates a 6-column matrix for feature name mapping reference.
"""

from __future__ import annotations

import json
import csv
import os
from typing import Dict, List, Tuple, Any
from pathlib import Path


class FeatureExtractor:
    """Extract and export unique feature names from master JSON."""

    def __init__(self, master_json_path: str, output_dir: str) -> None:
        """Initialize with paths.

        Args:
            master_json_path: Path to master_bmecat_dabag.json
            output_dir: Directory to save output CSV
        """
        self.master_json_path = master_json_path
        self.output_dir = output_dir
        self.data: Dict[str, Any] = {}
        
        # Store unique features as: {(fname_de, fname_fr, fname_it): (fvalue_de, fvalue_fr, fvalue_it)}
        self.unique_features: Dict[Tuple[str, str, str], Tuple[str, str, str]] = {}

    def load_master_json(self) -> bool:
        """Load the master JSON file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(self.master_json_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"✅ Loaded master JSON: {len(self.data.get('products', {}))} products")
            return True
        except FileNotFoundError:
            print(f"❌ Error: Master JSON not found at {self.master_json_path}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON: {e}")
            return False

    def extract_features(self) -> None:
        """Extract unique features from all products.
        
        Matches features by position index across languages.
        """
        products = self.data.get('products', {})
        
        for pid, product_data in products.items():
            languages = product_data.get('languages', {})
            
            de_features = languages.get('de', {})
            fr_features = languages.get('fr', {})
            it_features = languages.get('it', {})
            
            # Convert to lists to maintain order
            de_items = list(de_features.items())
            fr_items = list(fr_features.items())
            it_items = list(it_features.items())
            
            # Match by position index
            max_len = max(len(de_items), len(fr_items), len(it_items))
            
            for i in range(max_len):
                fname_de = de_items[i][0] if i < len(de_items) else ""
                fvalue_de = de_items[i][1] if i < len(de_items) else ""
                
                fname_fr = fr_items[i][0] if i < len(fr_items) else ""
                fvalue_fr = fr_items[i][1] if i < len(fr_items) else ""
                
                fname_it = it_items[i][0] if i < len(it_items) else ""
                fvalue_it = it_items[i][1] if i < len(it_items) else ""
                
                # Create unique key and store
                feature_key = (fname_de, fname_fr, fname_it)
                
                # Skip if all empty
                if not any([fname_de, fname_fr, fname_it]):
                    continue
                
                # Store first occurrence as example
                if feature_key not in self.unique_features:
                    self.unique_features[feature_key] = (fvalue_de, fvalue_fr, fvalue_it)
        
        print(f"✅ Extracted {len(self.unique_features)} unique feature mappings")

    def export_to_csv(self, filename: str = "unique_features.csv") -> str:
        """Export unique features to CSV file.

        Args:
            filename: Output CSV filename.

        Returns:
            Full path to the saved CSV file.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, filename)
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'fname_de', 'fvalue_de',
                'fname_fr', 'fvalue_fr',
                'fname_it', 'fvalue_it'
            ])
            
            # Write data rows
            for feature_key, feature_values in sorted(self.unique_features.items()):
                row = [
                    feature_key[0], feature_values[0],  # de
                    feature_key[1], feature_values[1],  # fr
                    feature_key[2], feature_values[2]   # it
                ]
                writer.writerow(row)
        
        print(f"✅ Saved CSV: {output_path}")
        return output_path

    def run(self) -> bool:
        """Run the complete feature extraction pipeline.

        Returns:
            True if successful, False otherwise.
        """
        print("="*80)
        print("Feature Extractor - Unique Feature Name Database")
        print("="*80)
        
        if not self.load_master_json():
            return False
        
        self.extract_features()
        self.export_to_csv()
        
        print("="*80)
        print("✅ Feature extraction complete!")
        print("="*80)
        
        return True
