"""
Client for handling SerpAPI search requests.
"""

import os
from typing import Dict, Optional, List

import requests
from dotenv import load_dotenv


class SerpAPIClient:
    """Client for handling SerpAPI search requests."""

    def __init__(self) -> None:
        """Initialize client by loading environment variables and base config."""
        # Load environment variables from .env (searched from CWD upward)
        load_dotenv()
        self.api_key: Optional[str] = os.getenv("SERP_API_KEY")
        self.base_url: str = "https://serpapi.com/search.json"

        if not self.api_key:
            raise ValueError("SERP_API_KEY not found in environment variables")

    def search_web(self, query: str, website: Optional[str] = None) -> Optional[Dict]:
        """
        Search the web using SerpAPI with optional site restriction.

        Args:
            query: Search query (e.g., "ninja assassin").
            website: Optional website to restrict search to (e.g., "imdb.com").

        Returns:
            The parsed JSON response as a dict, or None if the request failed.
        """
        # Construct search query
        if website:
            search_query = f"site:{website} {query}"
        else:
            search_query = query

        params: Dict[str, str | int] = {
            "engine": "google",
            "q": search_query,
            "api_key": self.api_key or "",
            "num": 10,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None

    def extract_first_url(self, search_results: Dict, website: Optional[str] = None) -> Optional[str]:
        """
        Extract the first relevant URL from search results.

        Args:
            search_results: SerpAPI response payload.
            website: Optional website domain to filter by.

        Returns:
            First relevant URL if found, otherwise None.
        """
        try:
            organic_results: List[Dict] = search_results.get("organic_results", [])  # type: ignore[assignment]

            for result in organic_results:
                url: str = result.get("link", "")
                if website:
                    if website.lower() in url.lower():
                        return url
                else:
                    if url:
                        return url

            return None
        except Exception as e:  # noqa: BLE001 - broad except with logging for robustness
            print(f"Error extracting URL: {e}")
            return None
