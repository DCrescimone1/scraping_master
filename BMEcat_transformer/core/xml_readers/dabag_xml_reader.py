from __future__ import annotations

"""DABAG BMEcat XML reader with multi-language feature extraction.

Extracts per-product, per-language features from a DABAG-style BMEcat XML.
Supported languages: deu, fra, ita mapped to de, fr, it.

Returns data grouped by `SUPPLIER_PID` and language.
"""

from typing import Dict, List, Any, DefaultDict
from collections import defaultdict
import xml.etree.ElementTree as ET
from utils.logger import setup_logger


LANG_MAP = {
    "deu": "de",
    "fra": "fr",
    "ita": "it",
    # also accept short codes if encountered
    "de": "de",
    "fr": "fr",
    "it": "it",
}


class DABAGXMLReader:
    """Read DABAG XML and extract per-product, per-language features."""

    def __init__(self, xml_path: str) -> None:
        self.xml_path = xml_path
        self.logger = setup_logger(__name__)

    def extract_features(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Extract features per product and language keyed by `SUPPLIER_PID`.

        Parsing strategy (in order):
        1) lxml with recovery (if available)
        2) Standard xml.etree parsing

        Returns:
            Mapping: {supplier_id: {lang: [{"fname": str, "fvalue": str, "funit": str|None}, ...]}}
        """
        self.logger.info(f"Starting DABAG feature extraction from: {self.xml_path}")
        
        try:
            from lxml import etree as LXML_ET  # type: ignore
            self.logger.debug("Attempting extraction with lxml")
            result = self._extract_via_lxml()
            self.logger.info(f"DABAG lxml extraction: found {len(result)} products")
            return result
        except Exception as e:
            self.logger.warning(f"DABAG lxml extraction failed: {e}")
            self.logger.debug("Falling back to xml.etree.ElementTree")
            result = self._extract_via_xml_parsing()
            self.logger.info(f"DABAG ElementTree extraction: found {len(result)} products")
            return result

    def _extract_via_xml_parsing(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        results: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        try:
            self.logger.debug("Reading DABAG XML file")
            with open(self.xml_path, "rb") as f:
                raw = f.read()
            self.logger.debug(f"DABAG XML file size: {len(raw)} bytes")
            if raw.startswith(b"\xef\xbb\xbf"):
                raw = raw[3:]
            text = raw.decode("utf-8", errors="replace").lstrip()
            root = ET.fromstring(text)
        except Exception as e:
            self.logger.error(f"DABAG XML parsing failed: {e}")
            return results

        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"
        else:
            ns = ""
        self.logger.debug(f"DABAG root tag: {root.tag}, namespace: {ns if ns else 'none'}")

        product_nodes_list = root.findall(f".//{ns}PRODUCT") + root.findall(".//PRODUCT")
        self.logger.debug(f"DABAG found {len(product_nodes_list)} PRODUCT nodes")
        for prod in product_nodes_list:
            pid = self._get_first_text(prod, [f"{ns}SUPPLIER_PID", "SUPPLIER_PID"]) or ""
            if not pid:
                continue

            lang_map: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

            for feat in prod.findall(f".//{ns}FEATURE") + prod.findall(".//FEATURE"):
                funit = self._get_first_text(feat, [f"{ns}FUNIT", "FUNIT"]) or None

                # FNAME and FVALUE may appear multiple times with lang attribute
                for fname_node in feat.findall(f".//{ns}FNAME") + feat.findall(".//FNAME"):
                    lang_attr = fname_node.attrib.get("lang") or fname_node.attrib.get("xml:lang")
                    lang = LANG_MAP.get((lang_attr or "").strip().lower())
                    if not lang:
                        # skip unsupported or missing language entries gracefully
                        continue
                    fname = (fname_node.text or "").strip()
                    # find corresponding FVALUE with same lang, if any
                    fvalue = ""
                    for fvalue_node in feat.findall(f".//{ns}FVALUE") + feat.findall(".//FVALUE"):
                        v_lang_attr = fvalue_node.attrib.get("lang") or fvalue_node.attrib.get("xml:lang")
                        v_lang = LANG_MAP.get((v_lang_attr or "").strip().lower())
                        if v_lang == lang:
                            fvalue = (fvalue_node.text or "").strip()
                            break

                    if fname or fvalue or funit:
                        lang_map[lang].append({
                            "fname": fname,
                            "fvalue": fvalue,
                            "funit": funit.strip() if isinstance(funit, str) else funit,
                        })

            if lang_map:
                results[pid] = dict(lang_map)

        return results

    def _extract_via_lxml(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        from lxml import etree as LXML_ET  # type: ignore

        results: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        with open(self.xml_path, "rb") as f:
            raw = f.read()
        parser = LXML_ET.XMLParser(recover=True, encoding="utf-8")
        root = LXML_ET.fromstring(raw, parser)

        product_nodes = root.xpath('.//PRODUCT | .//*[local-name()="PRODUCT"]')
        self.logger.debug(f"DABAG lxml found {len(product_nodes)} PRODUCT nodes")
        for prod in product_nodes:
            pid_nodes = prod.xpath('.//SUPPLIER_PID | .//*[local-name()="SUPPLIER_PID"]')
            pid = pid_nodes[0].text.strip() if pid_nodes and pid_nodes[0].text else ""
            if not pid:
                continue

            lang_map: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

            feat_nodes = prod.xpath('.//FEATURE | .//*[local-name()="FEATURE"]')
            for feat in feat_nodes:
                funit_nodes = feat.xpath('.//FUNIT | .//*[local-name()="FUNIT"]')
                funit = (funit_nodes[0].text or "").strip() if funit_nodes and funit_nodes[0].text else None

                fname_nodes = feat.xpath('.//FNAME | .//*[local-name()="FNAME"]')
                for fname_node in fname_nodes:
                    lang_attr = fname_node.attrib.get("lang") or fname_node.attrib.get("xml:lang")
                    lang = LANG_MAP.get((lang_attr or "").strip().lower())
                    if not lang:
                        continue
                    fname = (fname_node.text or "").strip()

                    fvalue = ""
                    fvalue_nodes = feat.xpath('.//FVALUE | .//*[local-name()="FVALUE"]')
                    for fvalue_node in fvalue_nodes:
                        v_lang_attr = fvalue_node.attrib.get("lang") or fvalue_node.attrib.get("xml:lang")
                        v_lang = LANG_MAP.get((v_lang_attr or "").strip().lower())
                        if v_lang == lang:
                            fvalue = (fvalue_node.text or "").strip()
                            break

                    if fname or fvalue or funit:
                        lang_map[lang].append({
                            "fname": fname,
                            "fvalue": fvalue,
                            "funit": funit,
                        })

            if lang_map:
                results[pid] = dict(lang_map)

        return results

    def _get_first_text(self, node: Any, tags: List[str]) -> str | None:
        for tag in tags:
            elem = node.find(f".//{tag}")
            if elem is not None and elem.text:
                return elem.text
        return None
