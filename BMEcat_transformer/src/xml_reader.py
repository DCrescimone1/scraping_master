"""XML Reader for BMEcat_transformer.

Provides `XMLReader` that extracts unique `SUPPLIER_PID`s from a BMEcat XML file.
Uses multiple fallback strategies to handle malformed XML.
"""

from __future__ import annotations

from typing import List, Set
import sys
import re
from pathlib import Path
import xml.etree.ElementTree as ET


# Ensure we can import the BMEcatParser from the sibling module `doc_processor`
DOC_PROCESSOR_PATH = Path(__file__).parent.parent.parent / "doc_processor"
sys.path.append(str(DOC_PROCESSOR_PATH))
try:
    from src.bmecat_parser import BMEcatParser  # type: ignore
except Exception as e:  # pragma: no cover - import guard
    BMEcatParser = None  # Fallback if import fails; we'll handle at runtime


class XMLReader:
    """Read BMEcat XML and extract product IDs.

    Attributes:
        xml_path: Path to the BMEcat XML file.
    """

    def __init__(self, xml_path: str) -> None:
        """Initialize with the XML file path.

        Args:
            xml_path: Path to the BMEcat XML file.
        """
        self.xml_path = xml_path

    def extract_SUPPLIER_PIDs(self) -> List[str]:
        """Extract a list of unique SUPPLIER_PID strings from the XML file.

        Uses multiple strategies in order:
        1. Try XML parsing with ET
        2. Try with lxml (if available)
        3. Fall back to regex extraction (always works)

        Returns:
            List of unique product IDs (order preserved by first appearance).
        """
        SUPPLIER_PIDs: List[str] = []
        seen: Set[str] = set()

        # Strategy 1: Try standard XML parsing
        try:
            print("🔍 Attempting standard XML parsing...")
            SUPPLIER_PIDs = self._extract_via_xml_parsing()
            if SUPPLIER_PIDs:
                print(f"✅ Successfully extracted {len(SUPPLIER_PIDs)} SUPPLIER_PIDs via XML parsing")
                return SUPPLIER_PIDs
        except Exception as e:
            print(f"⚠️  XML parsing failed: {e}")

        # Strategy 2: Try lxml with recovery mode (more lenient)
        try:
            print("🔍 Attempting lxml parsing with recovery mode...")
            from lxml import etree as LXML_ET
            SUPPLIER_PIDs = self._extract_via_lxml()
            if SUPPLIER_PIDs:
                print(f"✅ Successfully extracted {len(SUPPLIER_PIDs)} SUPPLIER_PIDs via lxml recovery")
                return SUPPLIER_PIDs
        except ImportError:
            print("⚠️  lxml not available, skipping...")
        except Exception as e:
            print(f"⚠️  lxml parsing failed: {e}")

        # Strategy 3: Regex-based extraction (always works, even with malformed XML)
        try:
            print("🔍 Falling back to regex-based extraction...")
            SUPPLIER_PIDs = self._extract_via_regex()
            if SUPPLIER_PIDs:
                print(f"✅ Successfully extracted {len(SUPPLIER_PIDs)} SUPPLIER_PIDs via regex")
                return SUPPLIER_PIDs
        except Exception as e:
            print(f"❌ Regex extraction failed: {e}")

        if not SUPPLIER_PIDs:
            print("⚠️  Warning: No SUPPLIER_PID elements found in the provided XML.")

        return SUPPLIER_PIDs

    def _extract_via_xml_parsing(self) -> List[str]:
        """Extract SUPPLIER_PIDs using standard XML parsing."""
        SUPPLIER_PIDs: List[str] = []
        seen: Set[str] = set()

        with open(self.xml_path, 'rb') as f:
            raw = f.read()

        # Remove BOM and strip leading whitespace
        if raw.startswith(b'\xef\xbb\xbf'):
            raw = raw[3:]
        text = raw.decode('utf-8', errors='replace').lstrip()
        
        root = ET.fromstring(text)

        # Determine namespace
        if root.tag.startswith('{'):
            ns = root.tag.split('}')[0] + '}'
        else:
            ns = ''

        # Search for SUPPLIER_PID elements
        for elem in root.findall(f'.//{ns}SUPPLIER_PID'):
            if elem is not None and elem.text:
                val = elem.text.strip()
                if val and val not in seen:
                    seen.add(val)
                    SUPPLIER_PIDs.append(val)

        # Also try without namespace
        for elem in root.findall('.//SUPPLIER_PID'):
            if elem is not None and elem.text:
                val = elem.text.strip()
                if val and val not in seen:
                    seen.add(val)
                    SUPPLIER_PIDs.append(val)

        return SUPPLIER_PIDs

    def _extract_via_lxml(self) -> List[str]:
        """Extract SUPPLIER_PIDs using lxml with recovery mode."""
        from lxml import etree as LXML_ET
        
        SUPPLIER_PIDs: List[str] = []
        seen: Set[str] = set()

        with open(self.xml_path, 'rb') as f:
            raw = f.read()

        # Create parser with recovery mode (tolerates malformed XML)
        parser = LXML_ET.XMLParser(recover=True, encoding='utf-8')
        root = LXML_ET.fromstring(raw, parser)

        # Find all SUPPLIER_PID elements
        for elem in root.xpath('.//SUPPLIER_PID | .//*[local-name()="SUPPLIER_PID"]'):
            if elem.text:
                val = elem.text.strip()
                if val and val not in seen:
                    seen.add(val)
                    SUPPLIER_PIDs.append(val)

        return SUPPLIER_PIDs

    def _extract_via_regex(self) -> List[str]:
        """Extract SUPPLIER_PIDs using regex pattern matching.
        
        This method is resilient to XML structure errors and will work
        even with malformed XML, as long as the tags exist.
        """
        SUPPLIER_PIDs: List[str] = []
        seen: Set[str] = set()

        with open(self.xml_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Pattern to match <SUPPLIER_PID>VALUE</SUPPLIER_PID>
        # Works with or without namespace
        pattern = r'<(?:\w+:)?SUPPLIER_PID[^>]*>(.*?)</(?:\w+:)?SUPPLIER_PID>'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            val = match.strip()
            if val and val not in seen:
                seen.add(val)
                SUPPLIER_PIDs.append(val)

        return SUPPLIER_PIDs