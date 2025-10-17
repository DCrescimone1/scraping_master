#!/usr/bin/env python3
"""Test all imports after restructuring."""

import sys
from pathlib import Path

# Add current directory to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_imports():
    """Test all module imports."""
    errors = []
    
    print("Testing imports...\n")
    
    # Test config
    try:
        import config
        print("✓ config imported successfully")
    except Exception as e:
        errors.append(f"✗ config: {e}")
        print(f"✗ config: {e}")
    
    # Test core modules
    try:
        from core.input_handler import InputHandler
        print("✓ core.input_handler imported successfully")
    except Exception as e:
        errors.append(f"✗ core.input_handler: {e}")
        print(f"✗ core.input_handler: {e}")
    
    try:
        from core.xml_readers.original_supplier_id_extractor import OriginalSupplierIDExtractor
        print("✓ core.xml_readers.original_supplier_id_extractor imported successfully")
    except Exception as e:
        errors.append(f"✗ core.xml_readers.original_supplier_id_extractor: {e}")
        print(f"✗ core.xml_readers.original_supplier_id_extractor: {e}")
    
    try:
        from core.master_json_manager import MasterJSONManager
        print("✓ core.master_json_manager imported successfully")
    except Exception as e:
        errors.append(f"✗ core.master_json_manager: {e}")
        print(f"✗ core.master_json_manager: {e}")
    
    # Test scraper modules
    try:
        from scrapers.table_extractor import TableExtractor
        print("✓ scrapers.table_extractor imported successfully")
    except Exception as e:
        errors.append(f"✗ scrapers.table_extractor: {e}")
        print(f"✗ scrapers.table_extractor: {e}")
    
    try:
        from scrapers.dabag_scraper import DABAGScraper
        print("✓ scrapers.dabag_scraper imported successfully")
    except Exception as e:
        errors.append(f"✗ scrapers.dabag_scraper: {e}")
        print(f"✗ scrapers.dabag_scraper: {e}")
    
    # Test processor modules
    try:
        from processors.feature_extractor import FeatureExtractor
        print("✓ processors.feature_extractor imported successfully")
    except Exception as e:
        errors.append(f"✗ processors.feature_extractor: {e}")
        print(f"✗ processors.feature_extractor: {e}")
    
    # Test output modules
    try:
        from output.output_formatter import OutputFormatter
        print("✓ output.output_formatter imported successfully")
    except Exception as e:
        errors.append(f"✗ output.output_formatter: {e}")
        print(f"✗ output.output_formatter: {e}")
    
    # Test UI modules
    try:
        from ui.user_prompt import UserPrompt
        print("✓ ui.user_prompt imported successfully")
    except Exception as e:
        errors.append(f"✗ ui.user_prompt: {e}")
        print(f"✗ ui.user_prompt: {e}")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"❌ FAILED: {len(errors)} import error(s)")
        for error in errors:
            print(f"  {error}")
        return False
    else:
        print("✅ SUCCESS: All imports working correctly!")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
