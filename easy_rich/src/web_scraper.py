from typing import Optional, Dict

import requests
from bs4 import BeautifulSoup


class WebScraper:
    """Web scraper for extracting content from web pages."""

    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
            }
        )

    def scrape_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape content from a given URL.

        Args:
            url: URL to scrape.

        Returns:
            A dict containing metadata and content, or None if the request fails.
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            return {
                "url": url,
                "title": self._extract_title(soup),
                "html_content": str(soup),
                "text_content": soup.get_text(strip=True),
                "status_code": str(response.status_code),
            }

        except requests.exceptions.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from soup object."""
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else "No title found"

    def save_content(self, content: Dict[str, str], filename: str = "scraped_content.html") -> None:
        """
        Save scraped HTML content to file.

        Args:
            content: Scraped content dict.
            filename: Output filename.
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content["html_content"])
            print(f"Content saved to {filename}")
        except Exception as e:  # noqa: BLE001 - broad except with logging for robustness
            print(f"Error saving content: {e}")

