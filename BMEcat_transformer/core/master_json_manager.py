"""Master JSON manager for BMEcat_transformer.

Manages a persistent master JSON file that tracks all scraped products.
Provides functionality to check existence, append new entries, update existing ones,
and maintain backup versions.
"""

from __future__ import annotations

import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, Tuple


class MasterJSONManager:
    """Manage the master JSON file for scraped product data."""

    def __init__(self, master_filename: str, output_dir: str, backup_count: int = 2) -> None:
        """Initialize the master JSON manager.

        Args:
            master_filename: Name of the master JSON file.
            output_dir: Directory where master JSON is stored.
            backup_count: Number of backup versions to keep.
        """
        self.master_filename = master_filename
        self.output_dir = output_dir
        self.backup_count = backup_count
        self.master_path = os.path.join(output_dir, master_filename)
        self.data: Dict[str, Any] = {"metadata": {}, "products": {}}
        os.makedirs(output_dir, exist_ok=True)

    def load(self) -> None:
        """Load the master JSON file. Creates new if doesn't exist."""
        if os.path.exists(self.master_path):
            try:
                with open(self.master_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                print(f"✓ Loaded master JSON from: {self.master_path}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Warning: Failed to load master JSON ({e}). Starting fresh.")
                self._initialize_fresh()
        else:
            print(f"✓ Master JSON not found. Starting fresh: {self.master_path}")
            self._initialize_fresh()

    def _initialize_fresh(self) -> None:
        """Initialize a fresh master JSON structure."""
        self.data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_products": 0,
            },
            "products": {},
        }

    def check_id_exists(self, supplier_pid: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Check if a SUPPLIER_PID exists in master JSON.

        Args:
            supplier_pid: The product ID to check.

        Returns:
            Tuple of (exists: bool, existing_data: dict or None)
        """
        exists = supplier_pid in self.data.get("products", {})
        existing_data = self.data["products"].get(supplier_pid) if exists else None
        return exists, existing_data

    def append_product(self, supplier_pid: str, product_data: Dict[str, Any]) -> None:
        """Append a new product to the master JSON.

        Args:
            supplier_pid: The product ID.
            product_data: The scraped product data.
        """
        enriched_data = product_data.copy()
        enriched_data["scraped_at"] = datetime.now().isoformat()
        self.data["products"][supplier_pid] = enriched_data
        self.data["metadata"]["total_products"] = len(self.data["products"])
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        print(f"✓ Appended {supplier_pid} to master JSON")

    def update_product(self, supplier_pid: str, product_data: Dict[str, Any]) -> None:
        """Update an existing product in the master JSON.

        Args:
            supplier_pid: The product ID.
            product_data: The new scraped product data.
        """
        enriched_data = product_data.copy()
        enriched_data["scraped_at"] = datetime.now().isoformat()
        enriched_data["updated_at"] = datetime.now().isoformat()
        self.data["products"][supplier_pid] = enriched_data
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()
        print(f"✓ Updated {supplier_pid} in master JSON")

    def save(self) -> None:
        """Save the master JSON with backup rotation."""
        self._rotate_backups()
        try:
            with open(self.master_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✓ Saved master JSON to: {self.master_path}")
        except IOError as e:
            print(f"❌ Error saving master JSON: {e}")

    def _rotate_backups(self) -> None:
        """Rotate backup files, keeping only the specified number of backups."""
        if not os.path.exists(self.master_path):
            return

        # Shift existing backups
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = f"{self.master_path}.backup{i}"
            new_backup = f"{self.master_path}.backup{i+1}"
            if os.path.exists(old_backup):
                if i == self.backup_count - 1:
                    # Remove oldest backup if at limit
                    if os.path.exists(new_backup):
                        os.remove(new_backup)
                shutil.move(old_backup, new_backup)

        # Create backup of current master
        backup_path = f"{self.master_path}.backup1"
        shutil.copy2(self.master_path, backup_path)

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the master JSON.

        Returns:
            Dictionary with statistics.
        """
        return {
            "total_products": len(self.data.get("products", {})),
            "created_at": self.data.get("metadata", {}).get("created_at", "N/A"),
            "last_updated": self.data.get("metadata", {}).get("last_updated", "N/A"),
        }
