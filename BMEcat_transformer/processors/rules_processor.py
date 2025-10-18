from __future__ import annotations

"""Rules Processor for AI Feature Extraction.

Validates, loads, and converts custom business rules into AI prompt instructions.
"""

import json
import os
from typing import Dict, List, Any
from utils.logger import setup_logger


class RulesProcessor:
    """Process and validate custom extraction rules."""

    def __init__(self, rules_path: str) -> None:
        """Initialize with rules JSON path.
        
        Args:
            rules_path: Path to ai_extraction_rules.json
        """
        self.rules_path = rules_path
        self.logger = setup_logger(__name__)
        self.rules: Dict[str, Any] = {"metadata": {}, "rules": []}
        self.validation_errors: List[str] = []

    def load_and_validate(self) -> bool:
        """Load and validate rules file.
        
        Returns:
            True if successful, False otherwise.
        """
        # Load JSON
        if not os.path.exists(self.rules_path):
            self.logger.error(f"Rules file not found: {self.rules_path}")
            return False

        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                self.rules = json.load(f)
            self.logger.info(f"Loaded {len(self.rules.get('rules', []))} rules from {self.rules_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in rules file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to load rules: {e}")
            return False

        # Validate structure
        if not self._validate_structure():
            for error in self.validation_errors:
                self.logger.error(f"Validation error: {error}")
            return False

        self.logger.info("✅ Rules validation passed")
        return True

    def _validate_structure(self) -> bool:
        """Validate rules JSON structure.
        
        Returns:
            True if valid, False otherwise.
        """
        self.validation_errors = []

        # Check metadata
        if "metadata" not in self.rules:
            self.validation_errors.append("Missing 'metadata' section")

        # Check rules array
        if "rules" not in self.rules:
            self.validation_errors.append("Missing 'rules' array")
            return False

        if not isinstance(self.rules["rules"], list):
            self.validation_errors.append("'rules' must be an array")
            return False

        # Validate each rule
        for idx, rule in enumerate(self.rules["rules"]):
            rule_id = rule.get("id", f"rule_{idx}")
            
            # Required fields
            required = ["id", "description", "priority", "trigger", "actions"]
            for field in required:
                if field not in rule:
                    self.validation_errors.append(f"Rule '{rule_id}': missing required field '{field}'")

            # Priority must be int
            if "priority" in rule and not isinstance(rule["priority"], int):
                self.validation_errors.append(f"Rule '{rule_id}': 'priority' must be integer, got {type(rule['priority']).__name__}")

            # Trigger must be dict
            if "trigger" in rule and not isinstance(rule["trigger"], dict):
                self.validation_errors.append(f"Rule '{rule_id}': 'trigger' must be object/dict")

            # Actions must be dict
            if "actions" in rule and not isinstance(rule["actions"], dict):
                self.validation_errors.append(f"Rule '{rule_id}': 'actions' must be object/dict")

        return len(self.validation_errors) == 0

    def get_enabled_rules(self) -> List[Dict[str, Any]]:
        """Get list of enabled rules sorted by priority.
        
        Returns:
            List of enabled rule dictionaries.
        """
        enabled = [r for r in self.rules.get("rules", []) if r.get("enabled", True)]
        return sorted(enabled, key=lambda x: x.get("priority", 999))

    def convert_to_prompt_instructions(self) -> str:
        """Convert rules to natural language instructions for AI prompt.
        
        Returns:
            Formatted string of rule instructions.
        """
        enabled_rules = self.get_enabled_rules()
        if not enabled_rules:
            return "No custom rules defined."

        instructions = ["## CUSTOM EXTRACTION RULES (CRITICAL - FOLLOW STRICTLY)\n"]
        
        for rule in enabled_rules:
            rule_id = rule.get("id", "unknown")
            description = rule.get("description", "")
            priority = rule.get("priority", 0)
            trigger = rule.get("trigger", {})
            actions = rule.get("actions", {})

            instructions.append(f"### Rule {priority}: {rule_id}")
            instructions.append(f"**Description:** {description}\n")

            # Trigger conditions
            instructions.append("**When:**")
            trigger_type = trigger.get("type", "")
            
            if trigger_type == "text_contains":
                patterns = trigger.get("patterns", [])
                fields = trigger.get("fields", [])
                instructions.append(f"- If ANY of these fields: {', '.join(fields)}")
                instructions.append(f"- Contains ANY of: {', '.join(patterns)}")
            
            elif trigger_type == "text_analysis":
                conditions = trigger.get("conditions", [])
                for cond in conditions:
                    field = cond.get("field", "")
                    if "not_contains" in cond:
                        patterns = cond["not_contains"]
                        instructions.append(f"- Field '{field}' does NOT contain: {', '.join(patterns)}")
                    if "contains_any" in cond:
                        patterns = cond["contains_any"]
                        instructions.append(f"- Field '{field}' contains ANY: {', '.join(patterns)}")

            # Actions
            instructions.append("\n**Then:**")
            action_type = actions.get("type", "")
            
            if action_type == "add_mandatory_fields":
                fields = actions.get("fields", [])
                instructions.append(f"- MUST include these fields in output: {', '.join(fields)}")
                instructions.append("- These fields are MANDATORY even if values need to be extracted")
            
            elif action_type == "set_field_values":
                values = actions.get("values", {})
                instructions.append("- Set these exact values:")
                for fname, fvalue in values.items():
                    instructions.append(f"  * {fname}: \"{fvalue}\"")
            
            elif action_type == "extract_and_add_field":
                field_name = actions.get("field_name", "")
                extraction = actions.get("extraction", {})
                patterns = extraction.get("patterns", [])
                instructions.append(f"- Add new field: '{field_name}'")
                instructions.append(f"- Extract value matching patterns: {', '.join(patterns[:3])}...")
                
                normalize = extraction.get("normalize", {})
                if normalize:
                    instructions.append("- Normalize extracted values:")
                    for standard, variants in normalize.items():
                        instructions.append(f"  * If found {variants} → use '{standard}'")

            instructions.append("")  # Empty line between rules

        return "\n".join(instructions)

    def log_rule_match(self, rule_id: str, product_id: str, details: str) -> None:
        """Log when a rule is triggered.
        
        Args:
            rule_id: Rule identifier
            product_id: Product SUPPLIER_PID
            details: Description of what matched
        """
        self.logger.info(f"🔍 Rule '{rule_id}' → TRIGGERED for {product_id}: {details}")
