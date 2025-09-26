from typing import Optional, Dict, List, Tuple, Set
import os
import sys
import re
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright

# Add config imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from config import (
        BOT_DETECTION_CODES, STEALTH_COST_WARNING, 
        STEALTH_CREDITS_COST, STEALTH_WARNING_MSG, BOT_DETECTED_MSG, 
        STEALTH_PROMPT_MSG, STEALTH_TRYING_MSG
    )
except ImportError:
    # Fallback values if config.py doesn't exist yet
    BOT_DETECTION_CODES = [401, 403, 500]
    STEALTH_COST_WARNING = True
    STEALTH_CREDITS_COST = 5
    STEALTH_WARNING_MSG = "💰 Stealth mode costs {} credits per request"
    BOT_DETECTED_MSG = "❌ Bot detected (Status: {})"
    STEALTH_PROMPT_MSG = "🤔 Try stealth mode? [y/N]: "
    STEALTH_TRYING_MSG = "🥷 Trying stealth mode..."

from .browsers.browser_factory import BrowserFactory
from .content_extractor import ContentExtractor


class WebScraper:
    """Web scraper for extracting content from web pages."""

    def __init__(self) -> None:
        """Initialize web scraper with Playwright."""
        self.content_extractor = ContentExtractor()

    def is_bot_detected(self, status_code: str) -> bool:
        """Check if the response indicates bot detection."""
        try:
            return int(status_code) in BOT_DETECTION_CODES
        except (ValueError, TypeError):
            return False

    def prompt_stealth_retry(self) -> bool:
        """Prompt user for stealth mode retry with cost warning."""
        if STEALTH_COST_WARNING:
            print(STEALTH_WARNING_MSG.format(STEALTH_CREDITS_COST))
        
        while True:
            choice = input(STEALTH_PROMPT_MSG).strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' or 'n'")

    def scrape_with_playwright(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape content with Playwright browser.
        
        Args:
            url: URL to scrape
        
        Returns:
            Scraped content dict or None if failed
        """
        try:
            with sync_playwright() as p:
                # Create browser instance
                browser_config = BrowserFactory.create()
                browser = browser_config.launch(p, headless=True)
                
                # Create context with stealth settings
                user_agents = browser_config.get_user_agents()
                import random
                context = browser.new_context(
                    user_agent=random.choice(user_agents),
                    viewport={"width": 1280, "height": 1200}
                )
                page = context.new_page()
                
                # Set timeout
                page.set_default_navigation_timeout(60000)
                
                try:
                    # Navigate to URL
                    response = page.goto(url, wait_until="domcontentloaded")
                    
                    if response and response.status >= 400:
                        print(f"HTTP error {response.status} while accessing content")
                        return None
                    
                    # Extract domain and create article dict
                    domain = urlparse(url).netloc
                    article = {"title": f"Article from {domain}"}
                    
                    # Extract content
                    success, article_content, title, rejection_reason = self.content_extractor.extract_article_content(
                        page, url, article, domain, domain
                    )
                    
                    if not success:
                        print(f"Content extraction failed: {rejection_reason}")
                        return None
                    
                    return {
                        "url": url,
                        "title": title,
                        "markdown_content": article_content,
                        "structured_data": {},
                        "status_code": str(response.status if response else 200),
                    }
                    
                finally:
                    page.close()
                    context.close()
                    browser.close()

        except Exception as e:  # noqa: BLE001 - broad except with logging for robustness
            print(f"Error scraping {url}: {e}")
            return None

    def scrape_page(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape content from a given URL using Playwright with bot detection.

        Args:
            url: URL to scrape.

        Returns:
            A dict containing metadata, markdown content, and structured data, or None if the request fails.
        """
        # Scrape with Playwright
        scraped_content = self.scrape_with_playwright(url)
        
        if not scraped_content:
            return None
        
        # Check for bot detection
        status_code = scraped_content.get("status_code", "Unknown")
        if self.is_bot_detected(status_code):
            print(BOT_DETECTED_MSG.format(status_code))
            
            # For now, just return None - stealth retry could be implemented later
            print("⭐ Bot detection encountered")
        
        return scraped_content

    def save_content(self, content: Dict[str, str], filename: str = "scraped_content") -> None:
        """
        Args:
            content: Scraped content dict.
            filename: Base filename (without extension).
        """
        try:
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