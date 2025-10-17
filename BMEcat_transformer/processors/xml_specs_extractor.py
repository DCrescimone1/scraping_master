"""XML Technical Specs Extractor for BMEcat_transformer.

Extracts unstructured technical specifications from UDX.EDXF.* XML fields.
Handles HTML entities and preserves formatting for AI processing.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Dict, Optional

from utils.logger import setup_logger


class XMLSpecsExtractor:
    """Extract technical specifications from UDX.EDXF XML fields."""

    def __init__(self, xml_path: str) -> None:
        """Initialize with XML file path.

        Args:
            xml_path: Path to the Original BMEcat XML file.
        """
        self.xml_path = xml_path
        self.logger = setup_logger(__name__)
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None

    def load_xml(self) -> bool:
        """Load and parse the XML file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()
            self.logger.info(f"Loaded XML: {self.xml_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load XML: {e}")
            return False

    def extract_udx_fields(self, supplier_pid: str, field_mapping: Dict[str, str]) -> Dict[str, str]:
        """Extract UDX.EDXF fields for a specific product.

        Args:
            supplier_pid: Product SUPPLIER_PID to extract.
            field_mapping: Dict mapping friendly names to XML tag names.

        Returns:
            Dict with friendly field names as keys and cleaned text as values.
        """
        if not self.root:
            self.logger.error("XML not loaded. Call load_xml() first.")
            return {}

        result = {}

        # Find the product
        for product in self.root.findall('.//PRODUCT'):
            pid_elem = product.find('.//SUPPLIER_PID')
            if pid_elem is not None and pid_elem.text == supplier_pid:
                # Extract each UDX field
                for friendly_name, xml_tag in field_mapping.items():
                    field_elem = product.find(f'.//{xml_tag}')
                    if field_elem is not None and field_elem.text:
                        cleaned_text = self._clean_html_entities(field_elem.text)
                        result[friendly_name] = cleaned_text
                    else:
                        result[friendly_name] = ""
                
                self.logger.debug(f"Extracted {len([v for v in result.values() if v])} non-empty fields for {supplier_pid}")
                return result

        self.logger.warning(f"Product {supplier_pid} not found in XML")
        return result

    def _clean_html_entities(self, text: str) -> str:
        """Clean HTML entities and formatting from text.

        Args:
            text: Raw text with HTML entities.

        Returns:
            Cleaned text with proper formatting.
        """
        # Replace common HTML entities
        text = text.replace("&lt;br&gt;", "\n")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&amp;", "&")
        text = text.replace("&quot;", '"')
        
        # Remove remaining HTML-like tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean excessive whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        text = text.strip()
        
        return text

    def extract_all_products(self, field_mapping: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Extract UDX fields for all products in XML.

        Args:
            field_mapping: Dict mapping friendly names to XML tag names.

        Returns:
            Dict with SUPPLIER_PID as keys and field data as values.
        """
        if not self.root:
            self.logger.error("XML not loaded. Call load_xml() first.")
            return {}

        results = {}

        for product in self.root.findall('.//PRODUCT'):
            pid_elem = product.find('.//SUPPLIER_PID')
            if pid_elem is not None and pid_elem.text:
                supplier_pid = pid_elem.text
                product_data = self.extract_udx_fields(supplier_pid, field_mapping)
                if any(product_data.values()):  # Only add if has data
                    results[supplier_pid] = product_data

        self.logger.info(f"Extracted UDX fields for {len(results)} products")
        return results
