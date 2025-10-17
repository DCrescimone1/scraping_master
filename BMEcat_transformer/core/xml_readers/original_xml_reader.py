from __future__ import annotations

"""Original BMEcat XML reader.

Extracts per-product features from an Original BMEcat XML, using `FDESCR` as
feature names and normalizing numeric values in German format.

Returns data grouped by `SUPPLIER_PID`.
"""

from typing import Dict, List, Any
import re
from utils.logger import setup_logger


class OriginalXMLReader:
    """Read Original BMEcat XML and extract per-product features.

    Uses regex-based extraction to handle malformed XML that lxml/ElementTree can't parse.
    Product identification: checks SUPPLIER_AID first, falls back to SUPPLIER_PID.
    
    Attributes:
        xml_path: Path to the BMEcat XML file.
    """

    def __init__(self, xml_path: str) -> None:
        """Initialize with the XML file path.

        Args:
            xml_path: Path to the BMEcat XML file.
        """
        self.xml_path = xml_path
        self.logger = setup_logger(__name__)

    def extract_features(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract features per product keyed by SUPPLIER_AID or SUPPLIER_PID.

        Uses regex parsing to handle malformed XML.
        Priority: SUPPLIER_AID checked first, SUPPLIER_PID as fallback.

        Returns:
            Mapping: {supplier_id: [{"fname": str, "fvalue": str, "funit": str|None}, ...]}
        """
        self.logger.info(f"Starting feature extraction from: {self.xml_path}")
        
        results: Dict[str, List[Dict[str, Any]]] = {}
        
        try:
            with open(self.xml_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            self.logger.debug(f"File size: {len(content)} characters")
            
            # Find all PRODUCT blocks using regex
            product_pattern = r'<PRODUCT[^>]*>(.*?)</PRODUCT>'
            products = re.findall(product_pattern, content, re.DOTALL)
            
            self.logger.info(f"Found {len(products)} PRODUCT blocks")
            
            for product_xml in products:
                # Extract SUPPLIER_AID first (primary), fallback to SUPPLIER_PID
                aid_match = re.search(r'<SUPPLIER_AID>\s*([^<]+?)\s*</SUPPLIER_AID>', product_xml)
                pid_match = re.search(r'<SUPPLIER_PID>\s*([^<]+?)\s*</SUPPLIER_PID>', product_xml)

                # Priority: AID first, then PID
                if aid_match:
                    supplier_id = aid_match.group(1).strip()
                elif pid_match:
                    supplier_id = pid_match.group(1).strip()
                else:
                    self.logger.debug("Skipping product without SUPPLIER_AID or SUPPLIER_PID")
                    continue
                self.logger.debug(f"Processing product: {supplier_id}")
                
                # Extract all FEATURE blocks
                feature_pattern = r'<FEATURE>(.*?)</FEATURE>'
                features_xml = re.findall(feature_pattern, product_xml, re.DOTALL)
                
                features: List[Dict[str, Any]] = []
                
                for feature_xml in features_xml:
                    # Extract FDESCR (feature name)
                    fname_match = re.search(r'<FDESCR>\s*([^<]+?)\s*</FDESCR>', feature_xml)
                    fname = fname_match.group(1).strip() if fname_match else ""
                    
                    # Extract FVALUE (feature value)
                    fvalue_match = re.search(r'<FVALUE>\s*([^<]+?)\s*</FVALUE>', feature_xml)
                    fvalue = fvalue_match.group(1).strip() if fvalue_match else ""
                    
                    # Extract FUNIT (feature unit)
                    funit_match = re.search(r'<FUNIT>\s*([^<]+?)\s*</FUNIT>', feature_xml)
                    funit = funit_match.group(1).strip() if funit_match else None
                    
                    # Normalize German number format
                    if fvalue:
                        fvalue = self._normalize_number(fvalue)
                    
                    # Only add if we have at least a name or value
                    if fname or fvalue or funit:
                        features.append({
                            "fname": fname,
                            "fvalue": fvalue,
                            "funit": funit,
                        })
                
                if features:
                    results[supplier_id] = features
                    self.logger.debug(f"Product {supplier_id}: extracted {len(features)} features")
            
            self.logger.info(f"Successfully extracted features for {len(results)} products")
            
        except Exception as e:
            self.logger.error(f"Feature extraction failed: {e}")
        
        return results

    def _normalize_number(self, value: str) -> str:
        """Normalize German-formatted numbers to dot-decimal.

        Examples:
            "2,5" -> "2.5"
            "1.234,56" -> "1234.56"

        If the value is not numeric-like, returns original string.
        """
        s = value.strip()
        # Potential patterns like 1.234,56 or 2,5 or 1234
        # Heuristic: if there's a comma and (digits or dot+digits) before it, treat comma as decimal
        if re.search(r"\d,\d", s):
            s_no_thousands = s.replace(".", "")
            s_norm = s_no_thousands.replace(",", ".")
            return s_norm
        # If only thousands separators (e.g., 1.234), keep as is but also offer a version without dots if it parses
        if re.fullmatch(r"\d{1,3}(\.\d{3})+", s):
            return s.replace(".", "")
        return s