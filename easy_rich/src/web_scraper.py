from typing import Optional, Dict, List, Tuple, Set

import os
from firecrawl import Firecrawl
from dotenv import load_dotenv
import re
from urllib.parse import urlparse, urljoin


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


    def extract_links_from_markdown(self, markdown_content: str, base_url: str) -> List[Tuple[str, str]]:
        """
        Extract all markdown links from content and filter by same domain.
        
        Args:
            markdown_content: The markdown content to parse
            base_url: The original URL to determine the base domain
            
        Returns:
            List of tuples (title, url) for same-domain links
        """
        try:
            # Parse base domain
            base_domain = urlparse(base_url).netloc.lower()
            
            # Extract markdown links using regex
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            matches = re.findall(link_pattern, markdown_content)
            
            same_domain_links: List[Tuple[str, str]] = []
            seen_urls: Set[str] = set()
            
            for title, url in matches:
                # Convert relative URLs to absolute
                if url.startswith('/'):
                    url = urljoin(base_url, url)
                elif not url.startswith('http'):
                    continue
                
                # Check if same domain
                try:
                    link_domain = urlparse(url).netloc.lower()
                    if base_domain in link_domain or link_domain in base_domain:
                        # Avoid duplicates and self-references
                        if url not in seen_urls and url != base_url:
                            same_domain_links.append((title.strip(), url))
                            seen_urls.add(url)
                except Exception:
                    continue
                
            return same_domain_links[:100]
            
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []


    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be safe for use as a filename.
        
        Args:
            filename: The raw filename string
            
        Returns:
            A filesystem-safe filename
        """
        import re
        
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)  # Remove invalid chars
        filename = re.sub(r'\s+', '_', filename.strip())  # Replace spaces with underscores
        filename = re.sub(r'_+', '_', filename)  # Remove multiple underscores
        filename = filename.strip('_')  # Remove leading/trailing underscores
        
        # Limit length and ensure it's not empty
        filename = filename[:50] if filename else "unnamed"
        
        return filename


    def create_session_folder(self, base_url: str, search_term: str = None) -> str:
        """Create a session folder based on domain, search term, and timestamp."""
        try:
            domain = urlparse(base_url).netloc.replace('www.', '').replace('.', '_')
            timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Include search term if available
            if search_term:
                clean_search = self.sanitize_filename(search_term)
                folder_name = f"{domain}_{clean_search}_{timestamp}"
            else:
                folder_name = f"{domain}_{timestamp}"
            
            import os
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            return folder_name
        except Exception as e:
            print(f"Error creating session folder: {e}")
            return "."


    def save_content_to_session(self, content: Dict[str, str], filename: str, session_folder: str) -> None:
        """Save content to session folder."""
        try:
            import json
            
            # Save markdown content
            md_path = os.path.join(session_folder, f"{filename}.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"# {content['title']}\n\n")
                f.write(f"**Source:** {content['url']}\n\n")
                f.write(content.get("markdown_content", ""))
            print(f"Markdown saved to {md_path}")

            # Save structured data if available
            if content.get("structured_data") is not None:
                json_path = os.path.join(session_folder, f"{filename}_data.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "url": content.get("url", ""),
                        "title": content.get("title", ""),
                        "status_code": content.get("status_code", ""),
                        "structured_data": content.get("structured_data", {}),
                    }, f, indent=2, ensure_ascii=False)
                print(f"Structured data saved to {json_path}")
            
        except Exception as e:
            print(f"Error saving content to session: {e}")
