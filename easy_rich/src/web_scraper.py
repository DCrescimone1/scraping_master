from typing import Optional, Dict

import os
from firecrawl import Firecrawl
from dotenv import load_dotenv


class WebScraper:
    """Web scraper for extracting content from web pages."""

    def __init__(self) -> None:
        """Initialize Firecrawl client."""
        load_dotenv()
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment variables")
        self.firecrawl = Firecrawl(api_key=api_key)

    def scrape_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape content from a given URL using Firecrawl.

        Args:
            url: URL to scrape.

        Returns:
            A dict containing metadata, markdown content, and structured data, or None if the request fails.
        """
        try:
            result = self.firecrawl.scrape(
                url,
                formats=[
                    "markdown",
                    {
                        "type": "json",
                        "prompt": "Extract key information from this page including title, main content summary, key points, and any important data like prices, dates, or contact information.",
                    },
                ],
            )

            # Access attributes from Firecrawl Document object safely
            has_metadata = hasattr(result, "metadata") and result.metadata is not None
            title = getattr(result.metadata, "title", "No title found") if has_metadata else "No title found"
            status_code = getattr(result.metadata, "statusCode", "Unknown") if has_metadata else "Unknown"
            markdown_content = getattr(result, "markdown", "")
            structured_data = getattr(result, "json", {})

            return {
                "url": url,
                "title": title,
                "markdown_content": markdown_content,
                "structured_data": structured_data,
                "status_code": str(status_code),
            }

        except Exception as e:  # noqa: BLE001 - broad except with logging for robustness
            print(f"Error scraping {url}: {e}")
            return None

    

    def save_content(self, content: Dict[str, str], filename: str = "scraped_content") -> None:
        """
        Save scraped content to both markdown and JSON files.

        Args:
            content: Scraped content dict.
            filename: Base filename (without extension).
        """
        try:
            # Save markdown content
            md_filename = f"{filename}.md"
            with open(md_filename, "w", encoding="utf-8") as f:
                f.write(f"# {content['title']}\n\n")
                f.write(f"**Source:** {content['url']}\n\n")
                f.write(content.get("markdown_content", ""))
            print(f"Markdown content saved to {md_filename}")

            # Save structured data if available
            if content.get("structured_data") is not None:
                json_filename = f"{filename}_data.json"
                import json
                with open(json_filename, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "url": content.get("url", ""),
                            "title": content.get("title", ""),
                            "status_code": content.get("status_code", ""),
                            "structured_data": content.get("structured_data", {}),
                        },
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )
                print(f"Structured data saved to {json_filename}")

        except Exception as e:  # noqa: BLE001 - broad except with logging for robustness
            print(f"Error saving content: {e}")

