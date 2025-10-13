"""
BMEcat XML Parser - Specialized parser for BMEcat catalog format.
Captures all attributes, relationships, and multi-language content.
"""

import xml.etree.ElementTree as ET
import codecs
from typing import Dict, List, Optional, Any


class BMEcatParser:
    """Enhanced parser specifically designed for BMEcat format."""
    
    def __init__(self):
        """Initialize the BMEcat parser."""
        self.namespaces = {
            'bme': 'http://www.bmecat.org/bmecat/2005fd'
        }
    
    def parse_bmecat_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse BMEcat XML file and extract all structured data.
        
        Args:
            file_path: Path to BMEcat XML file
            
        Returns:
            Dictionary with complete structured data or None if failed
        """
        try:
            # Read and sanitize XML to handle BOM and leading whitespace before declaration
            with open(file_path, 'rb') as f:
                raw = f.read()

            # Remove UTF-8 BOM if present
            if raw.startswith(codecs.BOM_UTF8):
                raw = raw[len(codecs.BOM_UTF8):]

            # Decode and strip leading whitespace/newlines before the first '<'
            text = raw.decode('utf-8', errors='replace')
            text = text.lstrip()  # remove leading spaces/newlines/tabs

            # Parse from string (handles cases where declaration isn't at pos 0 originally)
            root = ET.fromstring(text)
            
            # Handle namespace
            if root.tag.startswith('{'):
                ns = root.tag.split('}')[0] + '}'
            else:
                ns = ''
            
            result = {
                'header': self._parse_header(root, ns),
                'catalog_groups': self._parse_catalog_groups(root, ns),
                'metadata': {
                    'total_catalog_structures': 0,
                    'root_categories': 0,
                    'node_categories': 0,
                    'leaf_categories': 0
                }
            }
            
            # Count structures
            for group in result['catalog_groups']:
                for struct in group['structures']:
                    result['metadata']['total_catalog_structures'] += 1
                    struct_type = struct.get('type', '')
                    if struct_type == 'root':
                        result['metadata']['root_categories'] += 1
                    elif struct_type == 'node':
                        result['metadata']['node_categories'] += 1
                    elif struct_type == 'leaf':
                        result['metadata']['leaf_categories'] += 1
            
            return result
            
        except Exception as e:
            print(f"❌ Error parsing BMEcat file: {e}")
            return None
    
    def _parse_header(self, root: ET.Element, ns: str) -> Dict[str, Any]:
        """Extract header information."""
        header = {}
        header_elem = root.find(f'.//{ns}HEADER')
        
        if header_elem is not None:
            # Catalog info
            catalog_elem = header_elem.find(f'{ns}CATALOG')
            if catalog_elem is not None:
                header['catalog'] = {
                    'languages': [lang.text for lang in catalog_elem.findall(f'{ns}LANGUAGE')],
                    'catalog_id': self._get_text(catalog_elem, f'{ns}CATALOG_ID'),
                    'catalog_version': self._get_text(catalog_elem, f'{ns}CATALOG_VERSION')
                }
            
            # Supplier info
            supplier_elem = header_elem.find(f'{ns}SUPPLIER')
            if supplier_elem is not None:
                header['supplier'] = {
                    'name': self._get_text(supplier_elem, f'{ns}SUPPLIER_NAME')
                }
            
            # Parties info
            parties = []
            for party in header_elem.findall(f'.//{ns}PARTY'):
                party_id = party.find(f'{ns}PARTY_ID')
                if party_id is not None:
                    parties.append({
                        'id': party_id.text,
                        'type': party_id.get('type')
                    })
            header['parties'] = parties
        
        return header
    
    def _parse_catalog_groups(self, root: ET.Element, ns: str) -> List[Dict[str, Any]]:
        """Extract all catalog group systems."""
        groups = []
        
        for group_system in root.findall(f'.//{ns}CATALOG_GROUP_SYSTEM'):
            group_data = {
                'group_system_id': self._get_text(group_system, f'{ns}GROUP_SYSTEM_ID'),
                'group_system_name': self._get_text(group_system, f'{ns}GROUP_SYSTEM_NAME'),
                'structures': []
            }
            
            # Parse all catalog structures
            for struct in group_system.findall(f'{ns}CATALOG_STRUCTURE'):
                structure_data = self._parse_catalog_structure(struct, ns)
                group_data['structures'].append(structure_data)
            
            groups.append(group_data)
        
        return groups
    
    def _parse_catalog_structure(self, struct: ET.Element, ns: str) -> Dict[str, Any]:
        """Parse a single CATALOG_STRUCTURE element with all details."""
        data = {
            'type': struct.get('type'),
            'group_id': self._get_text(struct, f'{ns}GROUP_ID'),
            'parent_id': self._get_text(struct, f'{ns}PARENT_ID'),
            'group_order': self._get_text(struct, f'{ns}GROUP_ORDER'),
            'names': {},
            'descriptions': {}
        }
        
        # Get all GROUP_NAME elements (multi-language)
        for name_elem in struct.findall(f'{ns}GROUP_NAME'):
            lang = name_elem.get('lang', 'default')
            data['names'][lang] = name_elem.text
        
        # Get all GROUP_DESCRIPTION elements (multi-language)
        for desc_elem in struct.findall(f'{ns}GROUP_DESCRIPTION'):
            lang = desc_elem.get('lang', 'default')
            # Preserve full description text including line breaks
            desc_text = desc_elem.text or ''
            data['descriptions'][lang] = desc_text.strip()
        
        return data
    
    def _get_text(self, element: ET.Element, path: str) -> Optional[str]:
        """Safely extract text from element."""
        elem = element.find(path)
        return elem.text if elem is not None else None
    
    def to_markdown(self, parsed_data: Dict[str, Any]) -> str:
        """
        Convert parsed BMEcat data to well-structured markdown for AI processing.
        
        Args:
            parsed_data: Output from parse_bmecat_file()
            
        Returns:
            Formatted markdown string
        """
        md_lines = []
        
        # Header section
        md_lines.append("# BMEcat Catalog Document\n")
        
        if parsed_data.get('header'):
            md_lines.append("## Catalog Information\n")
            header = parsed_data['header']
            
            if 'catalog' in header:
                cat = header['catalog']
                md_lines.append(f"**Catalog ID:** {cat.get('catalog_id', 'N/A')}")
                md_lines.append(f"**Version:** {cat.get('catalog_version', 'N/A')}")
                md_lines.append(f"**Languages:** {', '.join(cat.get('languages', []))}\n")
            
            if 'supplier' in header:
                md_lines.append(f"**Supplier:** {header['supplier'].get('name', 'N/A')}\n")
        
        # Metadata
        if parsed_data.get('metadata'):
            meta = parsed_data['metadata']
            md_lines.append("## Catalog Statistics\n")
            md_lines.append(f"- Total catalog structures: {meta['total_catalog_structures']}")
            md_lines.append(f"- Root categories: {meta['root_categories']}")
            md_lines.append(f"- Node categories: {meta['node_categories']}")
            md_lines.append(f"- Leaf categories: {meta['leaf_categories']}\n")
        
        # Catalog structures
        md_lines.append("## Catalog Structure Details\n")
        
        for group in parsed_data.get('catalog_groups', []):
            md_lines.append(f"### Group System: {group.get('group_system_name', 'N/A')}\n")
            md_lines.append(f"**System ID:** {group.get('group_system_id', 'N/A')}\n")
            
            for idx, struct in enumerate(group.get('structures', []), 1):
                md_lines.append(f"#### Structure {idx}: {struct.get('type', 'unknown').upper()}\n")
                md_lines.append(f"**Group ID:** `{struct.get('group_id', 'N/A')}` ")
                md_lines.append(f"**Parent ID:** `{struct.get('parent_id', 'N/A')}` ")
                md_lines.append(f"**Order:** {struct.get('group_order', 'N/A')}\n")
                
                # Names (all languages)
                if struct.get('names'):
                    md_lines.append("**Names:**")
                    for lang, name in struct['names'].items():
                        md_lines.append(f"- [{lang}] {name}")
                    md_lines.append("")
                
                # Descriptions (all languages)
                if struct.get('descriptions'):
                    md_lines.append("**Descriptions:**")
                    for lang, desc in struct['descriptions'].items():
                        if desc:  # Only show if description exists
                            md_lines.append(f"\n*[{lang}]*")
                            md_lines.append(desc)
                    md_lines.append("\n---\n")
        
        return "\n".join(md_lines)
