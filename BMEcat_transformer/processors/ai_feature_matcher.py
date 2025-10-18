"""AI-powered feature matcher for BMEcat_transformer.

Uses Grok API to intelligently match unstructured XML text to 
structured feature names from unique_features.csv and ai_generated_features.json.
"""

from __future__ import annotations

import json
import csv
import os
from typing import Dict, List, Any
from datetime import datetime
import requests
import re

from utils.logger import setup_logger
from processors.rules_processor import RulesProcessor


class AIFeatureMatcher:
    """Match XML specs to structured features using Grok AI."""

    def __init__(
        self, 
        api_key: str,
        model: str,
        base_url: str,
        confidence_threshold: float,
        prompt_path: str,
        csv_path: str,
        ai_features_path: str
    ) -> None:
        """Initialize with API configuration and reference data paths.

        Args:
            api_key: Grok API key.
            model: Grok model name.
            base_url: Grok API base URL.
            confidence_threshold: Minimum confidence for AI-generated fields (0.0-1.0).
            prompt_path: Path to YAML prompt file.
            csv_path: Path to unique_features.csv (primary reference).
            ai_features_path: Path to ai_generated_features.json (fallback).
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.confidence_threshold = confidence_threshold
        self.prompt_path = prompt_path
        self.csv_path = csv_path
        self.ai_features_path = ai_features_path
        self.logger = setup_logger(__name__)
        
        self.allowed_features: List[Dict[str, str]] = []
        self.ai_features: Dict[str, Any] = {"metadata": {}, "features": []}
        self.prompt_template: str = ""
        
        # Rules processor (NEW)
        self.rules_processor: RulesProcessor | None = None
        self.custom_rules_instructions: str = ""

    def load_references(self) -> bool:
        """Load CSV and AI features references.

        Returns:
            True if successful, False otherwise.
        """
        try:
            # Load primary CSV
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.allowed_features = [row for row in reader]
            self.logger.info(f"Loaded {len(self.allowed_features)} features from CSV")

            # Load AI features (create if doesn't exist)
            if os.path.exists(self.ai_features_path):
                with open(self.ai_features_path, 'r', encoding='utf-8') as f:
                    self.ai_features = json.load(f)
                self.logger.info(f"Loaded {len(self.ai_features.get('features', []))} AI features")
            else:
                self._initialize_ai_features_file()

            return True
        except Exception as e:
            self.logger.error(f"Failed to load references: {e}")
            return False

    def load_prompt(self) -> bool:
        """Load prompt template from YAML file.

        Returns:
            True if successful, False otherwise.
        """
        try:
            import yaml
            with open(self.prompt_path, 'r', encoding='utf-8') as f:
                prompt_config = yaml.safe_load(f)
                self.prompt_template = prompt_config.get('prompt', '')
            self.logger.info("Loaded prompt template")
            
            # Load custom rules (NEW)
            rules_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "ai_extraction_rules.json"
            )
            
            if os.path.exists(rules_path):
                self.rules_processor = RulesProcessor(rules_path)
                if self.rules_processor.load_and_validate():
                    self.custom_rules_instructions = self.rules_processor.convert_to_prompt_instructions()
                    self.logger.info("✅ Custom rules loaded and converted to prompt instructions")
                else:
                    self.logger.warning("⚠️  Rules validation failed - continuing without custom rules")
            else:
                self.logger.info("No custom rules file found - using default extraction logic only")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to load prompt: {e}")
            return False

    def match_features(self, raw_text: Dict[str, str], product_id: str) -> List[Dict[str, Any]]:
        """Match raw XML text to structured features using AI.

        Args:
            raw_text: Dict with field names and unstructured text.
            product_id: SUPPLIER_PID for logging.

        Returns:
            List of matched features with schema:
            [{
                "fname": str,
                "fvalue": str,
                "funit": str | None,
                "source": str,
                "ai_generated": bool,
                "confidence": float
            }]
        """
        if not raw_text or not any(raw_text.values()):
            return []

        # Combine all text fields
        combined_text = "\n\n".join([f"=== {k.upper()} ===\n{v}" for k, v in raw_text.items() if v])

        # Build prompt
        prompt = self._build_prompt(combined_text)

        # Call Grok API
        try:
            response = self._call_grok_api(prompt)
            features = self._parse_grok_response(response, product_id)
            features = self._add_warning_if_needed(features)  # NEW: Add validation
            self.logger.info(f"Matched {len(features)} features for {product_id}")
            return features
        except Exception as e:
            self.logger.error(f"AI matching failed for {product_id}: {e}")
            return []

    def _build_prompt(self, text: str) -> str:
        """Build complete prompt with text and references.

        Args:
            text: Combined raw text.

        Returns:
            Complete prompt string.
        """
        # Format CSV features as reference
        csv_features = "\n".join([
            f"- {row['fname_de']}: {row['fvalue_de']}"
            for row in self.allowed_features[:50]  # Limit to avoid token overflow
        ])

        # Format AI features as secondary reference
        ai_features_list = "\n".join([
            f"- {feat['fname_de']}: {feat['fvalue_de']}"
            for feat in self.ai_features.get('features', [])[:20]
        ])

        prompt = self.prompt_template.replace("{RAW_TEXT}", text)
        prompt = prompt.replace("{ALLOWED_FEATURES_CSV}", csv_features)
        prompt = prompt.replace("{AI_FEATURES_FALLBACK}", ai_features_list)
        prompt = prompt.replace("{CONFIDENCE_THRESHOLD}", str(self.confidence_threshold))
        
        # Inject custom rules (NEW)
        if self.custom_rules_instructions:
            prompt = prompt.replace("{CUSTOM_RULES}", self.custom_rules_instructions)
        else:
            prompt = prompt.replace("{CUSTOM_RULES}", "No custom rules defined.")

        return prompt

    def _call_grok_api(self, prompt: str) -> Dict[str, Any]:
        """Call Grok API with prompt.

        Args:
            prompt: Complete prompt string.

        Returns:
            API response as dict.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,  # Low temp for consistency
            "response_format": {"type": "json_object"}
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        return response.json()

    def _parse_grok_response(self, response: Dict[str, Any], product_id: str) -> List[Dict[str, Any]]:
        """Parse Grok API response into feature list.

        Args:
            response: Raw API response.
            product_id: SUPPLIER_PID for tracking.

        Returns:
            List of structured features.
        """
        try:
            content = response['choices'][0]['message']['content']
            data = json.loads(content)
            features = data.get('features', [])

            # Process and validate features
            result = []
            for feat in features:
                # Check if AI-generated and meets threshold
                if feat.get('ai_generated', False):
                    if feat.get('confidence', 0) < self.confidence_threshold:
                        continue  # Skip low confidence AI fields
                    # Add warning marker
                    feat['fname'] = f"⚠️ {feat['fname']}"
                    # Update AI features JSON
                    self._update_ai_features_json(feat, product_id)

                result.append({
                    "fname": feat.get('fname', ''),
                    "fvalue": feat.get('fvalue', ''),
                    "funit": feat.get('funit'),
                    "source": feat.get('source', ''),
                    "ai_generated": feat.get('ai_generated', False),
                    "confidence": feat.get('confidence', 1.0)
                })

            return result
        except Exception as e:
            self.logger.error(f"Failed to parse Grok response: {e}")
            return []

    def _update_ai_features_json(self, feature: Dict[str, Any], product_id: str) -> None:
        """Update ai_generated_features.json with new field.

        Args:
            feature: Feature dict from AI.
            product_id: SUPPLIER_PID where first seen.
        """
        # Remove warning marker for storage
        fname_clean = feature['fname'].replace('⚠️ ', '')

        # Check if already exists
        existing = next(
            (f for f in self.ai_features['features'] if f['fname_de'] == fname_clean),
            None
        )

        if existing:
            existing['occurrences'] += 1
        else:
            self.ai_features['features'].append({
                "fname_de": fname_clean,
                "fvalue_de": feature.get('fvalue', ''),
                "fname_fr": "",
                "fvalue_fr": "",
                "fname_it": "",
                "fvalue_it": "",
                "confidence": feature.get('confidence', 0.0),
                "first_seen_pid": product_id,
                "occurrences": 1
            })

        # Save immediately
        self._save_ai_features_json()

    def _save_ai_features_json(self) -> None:
        """Save ai_generated_features.json to disk."""
        try:
            self.ai_features['metadata']['last_updated'] = datetime.now().isoformat()
            self.ai_features['metadata']['total_features'] = len(self.ai_features['features'])
            
            with open(self.ai_features_path, 'w', encoding='utf-8') as f:
                json.dump(self.ai_features, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save AI features: {e}")

    def _initialize_ai_features_file(self) -> None:
        """Create initial ai_generated_features.json file."""
        self.ai_features = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "confidence_threshold": self.confidence_threshold,
                "total_features": 0
            },
            "features": []
        }
        self._save_ai_features_json()
        self.logger.info("Initialized ai_generated_features.json")

    def _is_feature_in_csv(self, feature_name: str) -> bool:
        """Check if feature name exists in unique_features.csv.
        
        Normalizes by removing hyphens/spaces and comparing exactly.
        This prevents false positives like "Akku" matching "Akku-Kompatibilität".
        
        Args:
            feature_name: Feature name to check (German).
            
        Returns:
            True if found in CSV, False otherwise.
        """
        if not self.allowed_features:
            return False
        
        import re
        
        # Normalize: lowercase, remove hyphens and spaces
        def normalize(s: str) -> str:
            s = s.lower().strip()
            s = re.sub(r'[-\s]+', '', s)
            return s
        
        feature_normalized = normalize(feature_name)
        
        # Check exact match after normalization
        for row in self.allowed_features:
            csv_name = row.get('fname_de', '')
            if normalize(csv_name) == feature_normalized:
                return True
        
        return False

    def _add_warning_if_needed(self, features: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add ⚠️ prefix to features NOT in unique_features.csv.
        
        Args:
            features: List of feature dicts from AI.
            
        Returns:
            Same list with warning prefixes added where needed.
        """
        for feature in features:
            fname = feature.get('fname', '')
            if fname and not self._is_feature_in_csv(fname):
                # Add warning prefix if not already present
                if not fname.startswith('⚠️ '):
                    feature['fname'] = f"⚠️ {fname}"
                    self.logger.info(f"Feature NOT in CSV taxonomy: {fname}")
        
        return features
