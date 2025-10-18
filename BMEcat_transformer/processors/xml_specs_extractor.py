from __future__ import annotations

"""XML Technical Specs Extractor for BMEcat_transformer.

Extracts unstructured technical specifications from UDX.EDXF.* XML fields.
Handles HTML entities and preserves formatting for AI processing.
"""

import os
import re
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
        self.root: Optional[any] = None

    def load_xml(self) -> bool:
        """Load and parse the XML file using multiple fallback strategies.

        Parsing priority:
        1. lxml with recovery mode (most reliable)
        2. Regex-based extraction (ultimate fallback)

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
            self.logger.info("Successfully loaded XML with lxml recovery mode")
            return True
        except ImportError:
            self.logger.debug("lxml not available, using regex-based extraction")
            self.root = None  # Will use regex
            return True
        except Exception as e:
            self.logger.warning(f"lxml parsing failed: {e}, falling back to regex")
            self.root = None
            return True

    def _clean_html_entities(self, text: str) -> str:
        """Clean HTML entities from text.

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

    def _extract_udx_block_regex(self, product_xml: str, field_mapping: Dict[str, str]) -> Dict[str, str]:
        """Extract all UDX.EDXF fields from a product's USER_DEFINED_EXTENSIONS block.

        Uses regex to extract the entire UDX section and then parse each field.
        Handles both empty and populated fields.

        Args:
            product_xml: XML content of a single PRODUCT block.
            field_mapping: Dict mapping friendly names to XML tag names.

        Returns:
            Dict with field names as keys and extracted text as values.
        """
        result: Dict[str, str] = {}

        # Extract the USER_DEFINED_EXTENSIONS block
        udx_pattern = r'<USER_DEFINED_EXTENSIONS>(.*?)</USER_DEFINED_EXTENSIONS>'
        udx_match = re.search(udx_pattern, product_xml, re.DOTALL | re.IGNORECASE)

        if not udx_match:
            self.logger.debug("No USER_DEFINED_EXTENSIONS block found")
            return result

        udx_content = udx_match.group(1)

        # Extract each UDX field from the field_mapping
        for field_name, xml_tag in field_mapping.items():
            # Pattern handles both self-closing tags (<TAG/>) and tags with content
            pattern = f'<{re.escape(xml_tag)}(?:\\s[^>]*)?>\\s*(.*?)\\s*</{re.escape(xml_tag)}>'
            match = re.search(pattern, udx_content, re.DOTALL | re.IGNORECASE)

            if match:
                raw_text = match.group(1).strip()
                if raw_text:  # Only add non-empty content
                    clean_text = self._clean_html_entities(raw_text)
                    result[field_name] = clean_text
                    self.logger.debug(f"Extracted {field_name}: {len(clean_text)} chars")
                else:
                    self.logger.debug(f"{field_name} is empty")
            else:
                # Check if it's a self-closing tag
                self_closing_pattern = f'<{re.escape(xml_tag)}\\s*/>'
                if re.search(self_closing_pattern, udx_content, re.IGNORECASE):
                    self.logger.debug(f"{field_name} is self-closing (empty)")
                else:
                    self.logger.debug(f"{field_name} not found in UDX block")

        return result

    def extract_udx_fields(self, supplier_pid: str, field_mapping: Dict[str, str]) -> Dict[str, str]:
        """Extract UDX.EDXF fields for a specific product.

        Args:
            supplier_pid: Product ID to extract fields for.
            field_mapping: Dict mapping friendly names to XML tag names.

        Returns:
            Dict with field names as keys and cleaned text as values.
        """
        try:
            with open(self.xml_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Find the PRODUCT block for this supplier_pid
            product_pattern = f'<PRODUCT[^>]*>.*?<SUPPLIER_PID>\\s*{re.escape(supplier_pid)}\\s*</SUPPLIER_PID>.*?</PRODUCT>'
            product_match = re.search(product_pattern, content, re.DOTALL | re.IGNORECASE)

            if not product_match:
                self.logger.debug(f"Product {supplier_pid} not found")
                return {}

            product_xml = product_match.group(0)
            return self._extract_udx_block_regex(product_xml, field_mapping)

        except Exception as e:
            self.logger.error(f"Extraction failed for {supplier_pid}: {e}")
            return {}

    def extract_all_products(self, field_mapping: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Extract UDX fields for all products in XML.

        CRITICAL: This method now loads ALL products with valid PIDs,
        even if their UDX fields are empty. Products without any UDX data
        will have empty dictionaries, but they will still be in the results.

        Args:
            field_mapping: Dict mapping friendly names to XML tag names.

        Returns:
            Dict with SUPPLIER_PID as keys and field data as values.
        """
        results = {}

        try:
            with open(self.xml_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Find all PRODUCT blocks
            product_pattern = r'<PRODUCT[^>]*>(.*?)</PRODUCT>'
            products = re.findall(product_pattern, content, re.DOTALL)

            self.logger.debug(f"Found {len(products)} PRODUCT blocks")

            for product_xml in products:
                # Extract SUPPLIER_PID
                pid_match = re.search(r'<SUPPLIER_PID>\s*([^<]+?)\s*</SUPPLIER_PID>', product_xml)
                
                if not pid_match:
                    self.logger.debug("Skipping product without SUPPLIER_PID")
                    continue

                supplier_pid = pid_match.group(1).strip()
                
                # Extract UDX fields for this product
                product_data = self._extract_udx_block_regex(product_xml, field_mapping)
                
                # NEW: Save to text file
                if product_data:
                    self.save_to_text_file(supplier_pid, product_data)
                
                # This ensures consistency with product counts across all XML readers
                results[supplier_pid] = product_data
                
                if product_data:
                    self.logger.debug(f"Product {supplier_pid}: extracted {len(product_data)} UDX fields")
                else:
                    self.logger.debug(f"Product {supplier_pid}: no UDX data (empty fields)")

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")

        self.logger.info(f"Extracted UDX fields for {len(results)} products")
        return results

    def save_to_text_file(self, supplier_pid: str, udx_fields: Dict[str, str]) -> str:
        """Save extracted UDX fields to a text file for AI processing.
        
        Creates human-readable text file with section headers.
        Overwrites existing file on each run.
        
        Args:
            supplier_pid: Product identifier for filename.
            udx_fields: Dict with field names and extracted text.
            
        Returns:
            Full path to saved text file.
        """
        import sys
        from pathlib import Path
        
        # Import config
        PROJECT_ROOT = Path(__file__).resolve().parent.parent
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.append(str(PROJECT_ROOT))
        import config
        
        # Create directory if not exists
        output_dir = config.SCRAPED_TEXT_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        # Build file path
        filename = f"{supplier_pid}.txt"
        filepath = os.path.join(output_dir, filename)
        
        # Build content with section headers
        content_parts = [
            f"Product: {supplier_pid}",
            f"Extracted from: Original XML (DEWALT BMEcat)\n"
        ]
        
        for field_name, text in udx_fields.items():
            if text:  # Only add non-empty sections
                section_header = field_name.upper().replace("_", " ")
                content_parts.append(f"=== {section_header} ===")
                content_parts.append(text)
                content_parts.append("")  # Empty line between sections
        
        # Write to file (overwrite mode)
        full_content = "\n".join(content_parts)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        self.logger.info(f"Saved scraped text: {filepath}")
        return filepath