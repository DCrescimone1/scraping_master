from __future__ import annotations

"""Original BMEcat XML reader.

Extracts per-product features from an Original BMEcat XML, using `FDESCR` as
feature names and normalizing numeric values in German format.

Returns data grouped by `SUPPLIER_PID`.
"""

from typing import Dict, List, Any
import re
import xml.etree.ElementTree as ET
from utils.logger import setup_logger


class OriginalXMLReader:
    """Read Original BMEcat XML and extract per-product features.

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
        """Extract features per product keyed by `SUPPLIER_PID`.

        Returns:
            Mapping: {supplier_id: [{"fname": str, "fvalue": str, "funit": str|None}, ...]}
        """
        self.logger.info(f"Starting feature extraction from: {self.xml_path}")
        
        try:
            from lxml import etree as LXML_ET  # type: ignore
            self.logger.debug("Attempting extraction with lxml")
            result = self._extract_via_lxml()
            self.logger.info(f"lxml extraction: found {len(result)} products")
            return result
        except Exception as e:
            self.logger.warning(f"lxml extraction failed: {e}")
            self.logger.debug("Falling back to xml.etree.ElementTree")
            result = self._extract_via_xml_parsing()
            self.logger.info(f"ElementTree extraction: found {len(result)} products")
            return result

    def _extract_via_xml_parsing(self) -> Dict[str, List[Dict[str, Any]]]:
        results: Dict[str, List[Dict[str, Any]]] = {}

        try:
            self.logger.debug("Reading XML file")
            with open(self.xml_path, "rb") as f:
                raw = f.read()
            self.logger.debug(f"XML file size: {len(raw)} bytes")

            if raw.startswith(b"\xef\xbb\xbf"):
                raw = raw[3:]
            text = raw.decode("utf-8", errors="replace").lstrip()

            root = ET.fromstring(text)
        except Exception as e:
            self.logger.error(f"XML parsing failed: {e}")
            return results

        # Namespace if present
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"
        else:
            ns = ""
        self.logger.debug(f"Root tag: {root.tag}, namespace: {ns if ns else 'none'}")

        # Iterate products
        product_nodes = root.findall(f".//{ns}PRODUCT") + root.findall(".//PRODUCT")
        self.logger.debug(f"Found {len(product_nodes)} PRODUCT nodes")
        for prod in product_nodes:
            supplier_id = self._get_first_text(prod, [f"{ns}SUPPLIER_PID", "SUPPLIER_PID"]) or ""
            if not supplier_id:
                continue

            features: List[Dict[str, Any]] = []
            feature_nodes = (
                prod.findall(f".//{ns}FEATURE") + prod.findall(".//FEATURE")
            )
            for feat in feature_nodes:
                fname = self._get_first_text(feat, [f"{ns}FDESCR", "FDESCR"]) or ""
                fvalue = self._get_first_text(feat, [f"{ns}FVALUE", "FVALUE"]) or ""
                funit = self._get_first_text(feat, [f"{ns}FUNIT", "FUNIT"]) or None

                if fvalue:
                    fvalue = self._normalize_number(fvalue)

                if fname or fvalue or funit:
                    features.append({
                        "fname": fname.strip(),
                        "fvalue": (fvalue.strip() if isinstance(fvalue, str) else fvalue),
                        "funit": (funit.strip() if isinstance(funit, str) else funit),
                    })

            if features:
                results[supplier_id] = features

        return results

    def _extract_via_lxml(self) -> Dict[str, List[Dict[str, Any]]]:
        from lxml import etree as LXML_ET  # type: ignore

        results: Dict[str, List[Dict[str, Any]]] = {}

        with open(self.xml_path, "rb") as f:
            raw = f.read()

        parser = LXML_ET.XMLParser(recover=True, encoding="utf-8")
        root = LXML_ET.fromstring(raw, parser)

        # PRODUCT nodes (with or without namespace)
        product_nodes = root.xpath('.//PRODUCT | .//*[local-name()="PRODUCT"]')
        self.logger.debug(f"lxml found {len(product_nodes)} PRODUCT nodes")
        for prod in product_nodes:
            # SUPPLIER_PID
            pid_nodes = prod.xpath('.//SUPPLIER_PID | .//*[local-name()="SUPPLIER_PID"]')
            supplier_id = pid_nodes[0].text.strip() if pid_nodes and pid_nodes[0].text else ""
            if not supplier_id:
                continue

            features: List[Dict[str, Any]] = []
            feat_nodes = prod.xpath('.//FEATURE | .//*[local-name()="FEATURE"]')
            for feat in feat_nodes:
                fname_nodes = feat.xpath('.//FDESCR | .//*[local-name()="FDESCR"]')
                fvalue_nodes = feat.xpath('.//FVALUE | .//*[local-name()="FVALUE"]')
                funit_nodes = feat.xpath('.//FUNIT | .//*[local-name()="FUNIT"]')

                fname = (fname_nodes[0].text or "").strip() if fname_nodes and fname_nodes[0].text else ""
                fvalue = (fvalue_nodes[0].text or "").strip() if fvalue_nodes and fvalue_nodes[0].text else ""
                funit = (funit_nodes[0].text or "").strip() if funit_nodes and funit_nodes[0].text else None

                if fvalue:
                    fvalue = self._normalize_number(fvalue)

                if fname or fvalue or funit:
                    features.append({
                        "fname": fname,
                        "fvalue": fvalue,
                        "funit": funit,
                    })

            if features:
                results[supplier_id] = features

        return results

    def _get_first_text(self, node: Any, tags: List[str]) -> str | None:
        for tag in tags:
            elem = node.find(f".//{tag}")
            if elem is not None and elem.text:
                return elem.text
        return None

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
