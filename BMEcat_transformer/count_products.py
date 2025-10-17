from lxml import etree as LXML_ET

original_xml = "/Users/dannycrescimone/Documents/data_scraping/DEWALT_BMEcat_Original.xml"
dabag_xml = "/Users/dannycrescimone/Documents/data_scraping/DEWALT_Version_DABAG.xml"

print("="*70)
print("ORIGINAL XML:")
with open(original_xml, 'rb') as f:
    root = LXML_ET.fromstring(f.read(), LXML_ET.XMLParser(recover=True))
products = root.xpath('.//*[local-name()="PRODUCT"]')
print(f"Total PRODUCT nodes: {len(products)}")
for i, prod in enumerate(products[:10], 1):  # Show first 10
    pids = prod.xpath('.//*[local-name()="SUPPLIER_PID"]')
    pid = pids[0].text if pids and pids[0].text else "NO PID"
    print(f"  {i}. {pid}")

print("\n" + "="*70)
print("DABAG XML:")
with open(dabag_xml, 'rb') as f:
    root = LXML_ET.fromstring(f.read(), LXML_ET.XMLParser(recover=True))
products = root.xpath('.//*[local-name()="PRODUCT"]')
print(f"Total PRODUCT nodes: {len(products)}")
for i, prod in enumerate(products[:10], 1):
    pids = prod.xpath('.//*[local-name()="SUPPLIER_PID"]')
    pid = pids[0].text if pids and pids[0].text else "NO PID"
    print(f"  {i}. {pid}")

print("="*70)
