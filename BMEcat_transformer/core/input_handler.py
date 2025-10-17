"""Input handler for BMEcat_transformer.

Provides `InputHandler` that auto-detects and loads SUPPLIER_PIDs from
supported input files (XML or JSON).
"""

from __future__ import annotations

from pathlib import Path
from typing import List
import json

from core.xml_reader import XMLReader


class InputHandler:
    """Handle loading SUPPLIER_PIDs from XML or JSON input files.

    This is a stateless utility class that provides a single entry point to
    load product identifiers for downstream processing.
    """

    @staticmethod
    def load_supplier_ids(file_path: str) -> List[str]:
        """Auto-detect file type and return list of SUPPLIER_PIDs.

        Args:
            file_path: Path to input file (.xml or .json).

        Returns:
            List of unique SUPPLIER_PID strings.

        Raises:
            ValueError: If the file does not exist, has an unsupported type,
                or contains invalid JSON/invalid content.
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"Input file does not exist: {file_path}")

        suffix = path.suffix.lower()
        if suffix == ".xml":
            print("🔍 Detected XML file, extracting SUPPLIER_PIDs...")
            reader = XMLReader(str(path))
            ids = reader.extract_SUPPLIER_PIDs()
            # Ensure uniqueness and cleanliness
            seen = set()
            cleaned: List[str] = []
            for val in ids:
                v = val.strip()
                if v and v not in seen:
                    seen.add(v)
                    cleaned.append(v)
            print(f"✅ Successfully loaded {len(cleaned)} SUPPLIER_PID(s) from XML")
            return cleaned
        elif suffix == ".json":
            print("🔍 Detected JSON file, loading SUPPLIER_PIDs...")
            ids = InputHandler._load_from_json(str(path))
            print(f"✅ Successfully loaded {len(ids)} SUPPLIER_PID(s) from JSON")
            return ids
        else:
            raise ValueError(
                f"Unsupported input format '{suffix}'. Only .xml and .json are supported."
            )

    @staticmethod
    def _load_from_json(file_path: str) -> List[str]:
        """Load SUPPLIER_PIDs from a JSON array file.

        The JSON file must contain a simple array of strings, e.g.:
        ["ID1", "ID2", "ID3"]

        Args:
            file_path: Path to the JSON file.

        Returns:
            List of unique SUPPLIER_PID strings.

        Raises:
            ValueError: If JSON is invalid or content fails validation.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"⚠️  Invalid JSON: {e}")
            raise ValueError(f"Invalid JSON in file: {file_path}") from e

        # Validate structure: must be a list
        if not isinstance(data, list):
            print("⚠️  JSON must be an array of strings, e.g. [\"ID1\", \"ID2\"]")
            raise ValueError("JSON must be an array of strings")

        # Validate elements are strings
        if not all(isinstance(x, str) for x in data):
            print("⚠️  All elements in the JSON array must be strings")
            raise ValueError("All elements in the JSON array must be strings")

        # Clean, strip, and filter out empty strings; enforce uniqueness preserving order
        seen = set()
        cleaned: List[str] = []
        for x in data:
            v = x.strip()
            if v and v not in seen:
                seen.add(v)
                cleaned.append(v)

        if not cleaned:
            print("⚠️  JSON array is empty or contains only empty/whitespace strings")
            raise ValueError("JSON must contain at least one non-empty string")

        return cleaned
