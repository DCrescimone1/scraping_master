from __future__ import annotations
import logging
import sys

# Set DEBUG level for ALL loggers
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)

from core.xml_readers import OriginalXMLReader

xml_path = "/Users/dannycrescimone/Documents/data_scraping/DEWALT_BMEcat_Original.xml"

reader = OriginalXMLReader(xml_path)
reader.logger.setLevel(logging.DEBUG)

result = reader.extract_features()

print("\n" + "="*70)
print(f"RESULT: {len(result)} products found")
if result:
    first_id = list(result.keys())[0]
    print(f"First product ID: {first_id}")
    print(f"First product has {len(result[first_id])} features")
    print(f"First feature: {result[first_id][0]}")
else:
    print("NO PRODUCTS FOUND")
    
    # Manual check with lxml
    print("\nMANUAL LXML CHECK:")
    from lxml import etree as LXML_ET
    
    with open(xml_path, 'rb') as f:
        raw = f.read()
    
    parser = LXML_ET.XMLParser(recover=True, encoding='utf-8')
    root = LXML_ET.fromstring(raw, parser)
    
    print(f"Root tag: {root.tag}")
    print(f"Root has {len(root)} direct children")
    
    # Try different xpath queries
    products_1 = root.xpath('.//PRODUCT')
    products_2 = root.xpath('.//*[local-name()="PRODUCT"]')
    products_3 = root.xpath('//PRODUCT')
    
    print(f"\nXPath './/PRODUCT': {len(products_1)} nodes")
    print(f"XPath './/*[local-name()=\"PRODUCT\"]': {len(products_2)} nodes")
    print(f"XPath '//PRODUCT': {len(products_3)} nodes")
    
    if products_2:
        prod = products_2[0]
        print(f"\nFirst PRODUCT tag: {prod.tag}")
        print(f"First PRODUCT attributes: {prod.attrib}")
        
        # Check for SUPPLIER_PID
        pids_1 = prod.xpath('.//SUPPLIER_PID')
        pids_2 = prod.xpath('.//*[local-name()="SUPPLIER_PID"]')
        
        print(f"SUPPLIER_PID with './/': {len(pids_1)}")
        print(f"SUPPLIER_PID with local-name: {len(pids_2)}")
        
        if pids_1:
            print(f"SUPPLIER_PID value: {pids_1[0].text}")
        if pids_2:
            print(f"SUPPLIER_PID value (local-name): {pids_2[0].text}")

print("="*70)
