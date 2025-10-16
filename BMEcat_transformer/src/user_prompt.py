"""User prompt handler for BMEcat_transformer.

Handles user interaction when an existing product is found in master JSON.
Shows existing data and prompts for update decision.
"""

from __future__ import annotations

from typing import Dict, Any, Literal


class UserPrompt:
    """Handle user prompts and display existing data."""

    @staticmethod
    def show_existing_data(supplier_pid: str, existing_data: Dict[str, Any]) -> None:
        """Display existing data from master JSON.

        Args:
            supplier_pid: The product ID.
            existing_data: Data currently in master JSON.
        """
        print("\n" + "=" * 80)
        print(f"🔍 Product {supplier_pid} already exists in master JSON")
        print("-" * 80)

        # Show timestamps
        scraped_at = existing_data.get("scraped_at", "N/A")
        updated_at = existing_data.get("updated_at", scraped_at)
        print(f"Last scraped: {scraped_at}")
        if updated_at != scraped_at:
            print(f"Last updated: {updated_at}")

        # Show language coverage
        existing_langs = existing_data.get("languages", {})
        print("\nLanguage Coverage:")
        for lang in ["de", "fr", "it"]:
            spec_count = len(existing_langs.get(lang, {}))
            print(f"  {lang.upper()}: {spec_count} specs")

        # Show URL
        existing_url = existing_data.get("product_url", "N/A")
        print(f"\nURL: {existing_url}")

        print("-" * 80)

    @staticmethod
    def prompt_update_decision(supplier_pid: str) -> Literal["update", "skip"]:
        """Prompt user to decide whether to update or skip.

        Args:
            supplier_pid: The product ID.

        Returns:
            'update' if user wants to update, 'skip' otherwise.
        """
        while True:
            response = input(f"Update {supplier_pid}? [y/n]: ").strip().lower()
            if response in ["y", "yes"]:
                return "update"
            elif response in ["n", "no"]:
                return "skip"
            else:
                print("⚠️  Invalid input. Please enter 'y' or 'n'.")
