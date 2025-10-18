from __future__ import annotations

"""Comparison table builder orchestrator.

Coordinates data from Original XML, DABAG XML, and web scraped master JSON.
Optionally triggers scraping for missing supplier IDs.
"""

from typing import Dict, List, Any, Tuple, Set
import sys
from pathlib import Path

# Local imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from core.xml_readers import OriginalXMLReader, DABAGXMLReader  # type: ignore
from core.master_json_manager import MasterJSONManager  # type: ignore
import config  # type: ignore

# Scraper import
SCRAPERS_DIR = PROJECT_ROOT / "scrapers"
if str(SCRAPERS_DIR.parent) not in sys.path:
    sys.path.append(str(SCRAPERS_DIR.parent))
from scrapers.dabag_scraper import DABAGScraper  # type: ignore
from utils.logger import setup_logger
from processors.xml_specs_extractor import XMLSpecsExtractor  # type: ignore
from processors.ai_feature_matcher import AIFeatureMatcher  # type: ignore


class ComparisonTableBuilder:
    """Build merged comparison data across sources for each supplier/product."""

    def __init__(
        self,
        original_xml_path: str,
        dabag_xml_path: str,
        master_json_path: str | None = None,
    ) -> None:
        self.logger = setup_logger(__name__)
        self.original_xml_path = original_xml_path
        self.dabag_xml_path = dabag_xml_path
        # Master JSON manager uses OUTPUT_DIR and filename from config
        self.master_manager = MasterJSONManager(
            master_filename=config.MASTER_JSON_FILENAME,
            output_dir=config.OUTPUT_DIR,
            backup_count=config.MASTER_JSON_BACKUP_COUNT,
        )
        # Load or initialize master JSON
        self.master_manager.load()

        self.original_reader = OriginalXMLReader(original_xml_path)
        self.dabag_reader = DABAGXMLReader(dabag_xml_path)
        self.scraper = DABAGScraper()

    def _read_scraped_text(self, supplier_pid: str) -> Dict[str, str]:
        """Read scraped text file for a product if it exists.
        
        Args:
            supplier_pid: Product identifier.
            
        Returns:
            Dict with field names and text, empty dict if file not found.
        """
        from pathlib import Path
        
        text_file = Path(config.SCRAPED_TEXT_DIR) / f"{supplier_pid}.txt"
        
        if not text_file.exists():
            self.logger.debug(f"No scraped text file for {supplier_pid}")
            return {}
        
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse sections back into dict
            result = {}
            current_section = None
            current_text = []
            
            for line in content.split('\n'):
                if line.startswith('=== ') and line.endswith(' ==='):
                    # Save previous section
                    if current_section:
                        result[current_section.lower().replace(' ', '_')] = '\n'.join(current_text).strip()
                    # Start new section
                    current_section = line.strip('= ').strip()
                    current_text = []
                elif current_section and line.strip():
                    current_text.append(line)
            
            # Save last section
            if current_section:
                result[current_section.lower().replace(' ', '_')] = '\n'.join(current_text).strip()
            
            self.logger.debug(f"Read {len(result)} sections from {text_file}")
            return result
            
        except Exception as e:
            self.logger.warning(f"Failed to read scraped text for {supplier_pid}: {e}")
            return {}

    def build_comparison_tables(self, auto_scrape: bool = False) -> Dict[str, Dict[str, Any]]:
        """Build merged comparison data per supplier ID and language.

        Returns:
            Mapping per supplier: {supplier_id: {
                "product_url": str | None,
                "languages": {
                    lang: {
                        "rows": [
                            {
                                "original_fname": str, "original_fvalue": str, "original_funit": str | None,
                                "dabag_fname": str, "dabag_fvalue": str, "dabag_funit": str | None,
                                "web_fname": str, "web_fvalue": str,
                                "ai_fname": str, "ai_fvalue": str,
                            }, ...
                        ]
                    }
                }
            }}
        """
        self.logger.info("="*60)
        self.logger.info("Starting comparison table generation")
        self.logger.info(f"Auto-scrape enabled: {auto_scrape}")

        # Load data from sources
        original_features = self.original_reader.extract_features()  # {pid: [ {fname,fvalue,funit} ]}
        self.logger.info(f"Original XML: loaded {len(original_features)} products")
        dabag_features = self.dabag_reader.extract_features()        # {pid: {lang: [ {fname,fvalue,funit} ]} }
        self.logger.info(f"DABAG XML: loaded {len(dabag_features)} products")

        # NEW: Extract XML specs from UDX fields and match via AI (optional)
        ai_specs_by_pid: Dict[str, List[Dict[str, Any]]] = {}
        if getattr(config, "GROK_API_KEY", None):
            try:
                self.logger.info("Extracting UDX XML specifications and matching with AI...")
                extractor = XMLSpecsExtractor(self.original_xml_path)
                if extractor.load_xml():
                    udx_map = getattr(config, "UDX_FIELD_MAPPING", {})
                    all_udx = extractor.extract_all_products(udx_map)  # {pid: {field: text}}

                    prompt_path = PROJECT_ROOT / "prompts" / "xml_specs_mapping.yaml"
                    csv_path = Path(config.OUTPUT_DIR) / "unique_features.csv"
                    ai_matcher = AIFeatureMatcher(
                        api_key=config.GROK_API_KEY,
                        model=getattr(config, "GROK_MODEL", "grok-4-fast-reasoning"),
                        base_url=getattr(config, "GROK_BASE_URL", "https://api.x.ai/v1"),
                        confidence_threshold=float(getattr(config, "GROK_CONFIDENCE_THRESHOLD", 0.70)),
                        prompt_path=str(prompt_path),
                        csv_path=str(csv_path),
                        ai_features_path=getattr(config, "AI_FEATURES_PATH", str(Path(config.OUTPUT_DIR) / "ai_generated_features.json")),
                    )

                    if not csv_path.exists():
                        self.logger.warning(f"unique_features.csv not found at {csv_path} — AI matching may be limited")

                    if ai_matcher.load_references() and ai_matcher.load_prompt():
                        for pid in all_udx.keys():
                            # Try to read from saved text file first
                            raw_text = self._read_scraped_text(pid)
                            
                            # Fallback to memory if file doesn't exist
                            if not raw_text:
                                raw_text = all_udx.get(pid, {})
                            
                            if not raw_text:
                                continue
                            
                            feats = ai_matcher.match_features(raw_text, pid)
                            if feats:
                                ai_specs_by_pid[pid] = feats
                        self.logger.info(f"AI-matched XML specs for {len(ai_specs_by_pid)} products")
                    else:
                        self.logger.warning("AI matcher references or prompt failed to load; skipping AI matching")
                else:
                    self.logger.warning("Could not load Original XML for UDX extraction; skipping AI matching")
            except Exception as e:
                self.logger.error(f"XML specs extraction/matching failed: {e}")
        else:
            self.logger.info("Grok API key not configured — skipping XML specs extraction")

        # Prepare web data from master JSON
        web_products = self.master_manager.data.get("products", {})
        self.logger.info(f"Master JSON: loaded {len(web_products)} products")
        web_ids: Set[str] = set(web_products.keys())

        # Determine missing IDs to potentially scrape
        original_ids: List[str] = list(original_features.keys())
        missing_ids = self._check_missing_ids(original_ids, list(web_ids))
        self.logger.info(f"Missing IDs to scrape: {len(missing_ids)}")

        if auto_scrape and missing_ids:
            for pid in missing_ids:
                scraped = self.scraper.process_product(pid)
                if scraped:
                    exists, _ = self.master_manager.check_id_exists(pid)
                    if exists:
                        self.master_manager.update_product(pid, scraped)
                    else:
                        self.master_manager.append_product(pid, scraped)
            # Persist updates
            self.master_manager.save()
            web_products = self.master_manager.data.get("products", {})

        # Merge per supplier and per language
        merged: Dict[str, Dict[str, Any]] = {}
        for pid, orig_list in original_features.items():
            pid_dabag = dabag_features.get(pid, {})  # {lang: [..]}
            web_entry = web_products.get(pid, {})     # {product_url, languages: {lang: {label: value}}}
            product_url = web_entry.get("product_url")
            web_langs: Dict[str, Dict[str, str]] = web_entry.get("languages", {})

            # Build per-language rows for de, fr, it
            langs = ["de", "fr", "it"]
            lang_data: Dict[str, Any] = {}
            for lang in langs:
                dabag_list = pid_dabag.get(lang, [])
                web_specs = web_langs.get(lang, {})  # dict label->value
                ai_list = ai_specs_by_pid.get(pid, [])
                rows = self._align_features(orig_list, dabag_list, web_specs, ai_list)
                lang_data[lang] = {"rows": rows}

            merged[pid] = {
                "product_url": product_url,
                "languages": lang_data,
            }

        self.logger.info(f"Comparison tables built for {len(merged)} products")
        self.logger.info("="*60)
        return merged

    def _check_missing_ids(self, original_ids: List[str], web_ids: List[str]) -> List[str]:
        """Return IDs present in original XML but missing in web master JSON."""
        web_set = set(web_ids)
        return [pid for pid in original_ids if pid not in web_set]

    def _align_features(
        self,
        original_list: List[Dict[str, Any]],
        dabag_list: List[Dict[str, Any]],
        web_specs: Dict[str, str],
        ai_list: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Align features across sources by simple exact-name matching.

        Strategy:
        - Use union of all feature names across sources as the index set.
        - For web specs (dict label->value), use labels as names.
        - Construct rows with 8 columns (plus funit for original/dabag), AI left blank.
        """
        # Collect all feature names
        names: Set[str] = set()
        names.update([f.get("fname", "") for f in original_list if f.get("fname")])
        names.update([f.get("fname", "") for f in dabag_list if f.get("fname")])
        names.update([k for k in web_specs.keys() if k])
        names.update([f.get("fname", "") for f in ai_list if f.get("fname")])

        # Build quick lookups
        orig_map = {f.get("fname", ""): f for f in original_list if f.get("fname")}
        dabag_map = {f.get("fname", ""): f for f in dabag_list if f.get("fname")}
        ai_map = {f.get("fname", ""): f for f in ai_list if f.get("fname")}

        rows: List[Dict[str, Any]] = []
        for name in sorted(names):
            o = orig_map.get(name, {})
            d = dabag_map.get(name, {})
            w_val = web_specs.get(name, "")
            a = ai_map.get(name, {})
            rows.append({
                "original_fname": name if o else "",
                "original_fvalue": o.get("fvalue", ""),
                "original_funit": o.get("funit"),
                "dabag_fname": name if d else "",
                "dabag_fvalue": d.get("fvalue", ""),
                "dabag_funit": d.get("funit"),
                "web_fname": name if w_val else "",
                "web_fvalue": w_val,
                "ai_fname": name if a else "",
                "ai_fvalue": a.get("fvalue", "") if a else "",
            })
        return rows
