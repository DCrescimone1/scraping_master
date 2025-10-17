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
        """Load and parse the XML file using multiple fallback strategies.

        Parsing priority:
        1. lxml with recovery mode (most reliable)
        2. Standard ET parsing (fallback)

        Returns:
            True if successful, False otherwise.
        """
        # Strategy 1: Try lxml with recovery mode
        try:
            from lxml import etree as LXML_ET
            self.logger.debug("Attempting lxml parsing with recovery mode")
            with open(self.xml_path, 'rb') as f:
                raw = f.read()
            parser = LXML_ET.XMLParser(recover=True, encoding='utf-8')
            self.root = LXML_ET.fromstring(raw, parser)
            self.tree = None  # Not needed for lxml approach
            self.logger.info("Successfully loaded XML with lxml recovery mode")
            return True
        except ImportError:
            self.logger.debug("lxml not available, trying standard ET parsing")
        except Exception as e:
            self.logger.warning(f"lxml parsing failed: {e}, trying standard ET")

        # Strategy 2: Try standard ET parsing
        try:
            self.logger.debug("Attempting standard ET parsing")
            self.tree = ET.parse(self.xml_path)
            self.root = self.tree.getroot()
            self.logger.info("Successfully loaded XML with standard ET parsing")
            return True
        except Exception as e:
            self.logger.error(f"All XML parsing strategies failed: {e}")
            return False

    def extract_udx_fields(self, supplier_pid: str, field_mapping: Dict[str, str]) -> Dict[str, str]:
        """Extract UDX.EDXF fields for a specific product.

        Args:
            supplier_pid: Product ID to extract fields for.
            field_mapping: Dict mapping friendly names to XML tag names.

        Returns:
            Dict with field names as keys and cleaned text as values.
        """
        if not self.root:
            self.logger.error("XML not loaded. Call load_xml() first.")
            return {}

        result: Dict[str, str] = {}

        # Try XML-based extraction first
        try:
            # Find the product by SUPPLIER_PID using XPath (lxml) or findall (ET)
            if hasattr(self.root, 'xpath'):
                products = self.root.xpath(f'.//PRODUCT[.//SUPPLIER_PID[text()="{supplier_pid}"]]')
            else:
                products = [p for p in self.root.findall('.//PRODUCT')
                           if p.find('.//SUPPLIER_PID') is not None
                           and p.find('.//SUPPLIER_PID').text == supplier_pid]

            if not products:
                self.logger.debug(f"Product {supplier_pid} not found in XML")
                return result

            product = products[0]

            # Find USER_DEFINED_EXTENSIONS section
            if hasattr(product, 'xpath'):
                udx_nodes = product.xpath('.//USER_DEFINED_EXTENSIONS')
                udx_section = udx_nodes[0] if udx_nodes else None
            else:
                udx_section = product.find('.//USER_DEFINED_EXTENSIONS')

            if udx_section is None:
                self.logger.debug(f"No USER_DEFINED_EXTENSIONS for {supplier_pid}")
                return result

            # Extract each requested field
            for field_name, xml_tag in field_mapping.items():
                if hasattr(udx_section, 'xpath'):
                    nodes = udx_section.xpath(f'.//{xml_tag}/text()')
                    raw_text = nodes[0] if nodes else None
                else:
                    field_elem = udx_section.find(f'.//{xml_tag}')
                    raw_text = field_elem.text if field_elem is not None else None

                if raw_text:
                    clean_text = self._clean_html_entities(raw_text)
                    result[field_name] = clean_text
                    self.logger.debug(f"Extracted {field_name}: {len(clean_text)} chars")

        except Exception as e:
            self.logger.warning(f"XML extraction failed for {supplier_pid}: {e}, trying regex fallback")
            result = self._extract_via_regex(supplier_pid, field_mapping)

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

    def _extract_via_regex(self, supplier_pid: str, field_mapping: Dict[str, str]) -> Dict[str, str]:
        """Extract UDX fields using regex patterns (fallback for malformed XML).

        Args:
            supplier_pid: Product ID to extract fields for.
            field_mapping: Dict mapping friendly names to XML tag names.

        Returns:
            Dict with field names as keys and extracted text as values.
        """
        result: Dict[str, str] = {}

        try:
            with open(self.xml_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Find the PRODUCT block for this supplier_pid
            product_pattern = f'<PRODUCT[^>]*>.*?<SUPPLIER_PID>\\s*{re.escape(supplier_pid)}\\s*</SUPPLIER_PID>.*?</PRODUCT>'
            product_match = re.search(product_pattern, content, re.DOTALL | re.IGNORECASE)

            if not product_match:
                self.logger.debug(f"Product {supplier_pid} not found via regex")
                return result

            product_xml = product_match.group(0)

            # Extract each UDX field
            for field_name, xml_tag in field_mapping.items():
                pattern = f'<{re.escape(xml_tag)}>\\s*(.*?)\\s*</{re.escape(xml_tag)}>'
                match = re.search(pattern, product_xml, re.DOTALL | re.IGNORECASE)

                if match:
                    raw_text = match.group(1).strip()
                    if raw_text:
                        clean_text = self._clean_html_entities(raw_text)
                        result[field_name] = clean_text
                        self.logger.debug(f"Extracted {field_name} via regex: {len(clean_text)} chars")

        except Exception as e:
            self.logger.error(f"Regex extraction failed for {supplier_pid}: {e}")

        return result

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
