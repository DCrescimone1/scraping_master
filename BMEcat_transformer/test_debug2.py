from lxml import etree as LXML_ET

xml_path = "/Users/dannycrescimone/Documents/data_scraping/DEWALT_BMEcat_Original.xml"

with open(xml_path, 'rb') as f:
    raw = f.read()

parser = LXML_ET.XMLParser(recover=True, encoding='utf-8')
root = LXML_ET.fromstring(raw, parser)

product_nodes = root.xpath('.//*[local-name()="PRODUCT"]')
print(f"Found {len(product_nodes)} PRODUCT nodes")

for i, prod in enumerate(product_nodes):
    print(f"\n--- Product {i+1} ---")
    
    # Test the EXACT xpath from your code
    pid_nodes = prod.xpath('.//SUPPLIER_PID | .//*[local-name()="SUPPLIER_PID"]')
    print(f"pid_nodes length: {len(pid_nodes)}")
    print(f"pid_nodes: {pid_nodes}")
    
    if pid_nodes:
        print(f"pid_nodes[0]: {pid_nodes[0]}")
        print(f"pid_nodes[0].text: {pid_nodes[0].text}")
        if pid_nodes[0].text:
            supplier_id = pid_nodes[0].text.strip()
            print(f"supplier_id after strip: '{supplier_id}'")
            print(f"bool(supplier_id): {bool(supplier_id)}")
        else:
            print("pid_nodes[0].text is None or empty!")
