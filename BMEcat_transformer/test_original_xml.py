from __future__ import annotations
import logging
from core.xml_readers import OriginalXMLReader
from utils.logger import setup_logger

# Enable DEBUG level
logger = setup_logger(__name__, level=logging.DEBUG)

xml_path = "/Users/dannycrescimone/Documents/data_scraping/DEWALT_BMEcat_Original.xml"
reader = OriginalXMLReader(xml_path)

# This will show all debug messages
result = reader.extract_features()

print(f"\n{'='*60}")
print(f"FINAL RESULT: {len(result)} products found")
if result:
    print(f"First product ID: {list(result.keys())[0]}")
    print(f"First product features: {len(result[list(result.keys())[0]])} features")
print(f"{'='*60}")
