"""Extract article content from webpages using Playwright."""

import time
from bs4 import BeautifulSoup
from .browser_utils import handle_any_popups, add_human_pause, extract_readable_text

class ContentExtractor:
    """Extract article content from a webpage."""
    
    def __init__(self):
        pass
    
    def extract_article_content(self, page, url, article, domain, source, user_email=None):
        """Extract article content from the page.
        
        Args:
            page: The Playwright page object
            url: The URL of the article
            article: The article metadata
            domain: The domain of the article
            source: The source of the article
            user_email: Optional user email for validation context
            
        Returns:
            tuple: (success, article_content, title, rejection_reason)
        """
        print("Extracting article content...")
                
        try:
            # Start with aggressive popup handling first
            print("Applying aggressive popup/cookie handling approach...")
            handle_any_popups(page, aggressive=True)
            page.wait_for_timeout(1000)
            
            # Perform progressive scrolling for content exposure
            print("Performing progressive scrolling for content exposure...")
            self._perform_progressive_scrolling(page)
            
            # Handle any popups that appeared after scrolling
            print("Handling any new popups after scrolling...")
            handle_any_popups(page, aggressive=True)
            page.wait_for_timeout(1000)
            
            # Wait for page to be fully loaded with a timeout
            print("Waiting for page ready state before content extraction...")
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
                print("Page ready state reached")
            except Exception as e:
                print(f"Error waiting for page ready state (continuing anyway): {e}")
            
            # Extract content with BeautifulSoup
            article_content = self._extract_content_with_soup(page)
            
            # Get character count
            chars_count = len(article_content) if article_content else 0
            print(f"Extracted {chars_count} chars with content extraction")
            
            # Include the full content in logs when it's less than 100 characters
            if article_content and chars_count < 100:
                print(f"Content (under 100 chars): {article_content}")
            
            # If we have substantial content (>5500 chars), consider it valid
            if article_content and len(article_content) > 5500:
                title = self._extract_title(page, article)
                print(f"Article has substantial content ({len(article_content)} chars), accepting")
                return True, article_content, title, None
            
            # Continue with validation for articles with less content
            if article_content and len(article_content) > 150:
                title = self._extract_title(page, article)
            
                # Return the content for validation
                if len(article_content) < 1600:
                    print(f"Content too short: {len(article_content)} chars (minimum 1600)")
                    
                    # Try a more aggressive approach as fallback
                    try:
                        print("Attempting more aggressive content extraction as fallback...")
                        
                        fallback_content = page.evaluate("""() => {
                            const bodyText = document.body.innerText;
                            return bodyText || '';
                        }""")
                        
                        if fallback_content and len(fallback_content) > 1600:
                            print(f"Fallback extraction succeeded, got {len(fallback_content)} chars")
                            return True, fallback_content, title, None
                    except Exception as fallback_error:
                        print(f"Fallback extraction failed: {fallback_error}")
                    
                    rejection_reason = f"Content too short: {len(article_content)} chars (minimum 1600)"
                    return False, "", title, rejection_reason
                
                return True, article_content, title, None
            else:
                rejection_reason = "Content too short: 0 chars"
                print("Content extraction failed: Empty or very short content")
                return False, "", article.get("title", ""), rejection_reason
            
        except Exception as e:
            print(f"Error extracting content: {e}")
            import traceback
            print(f"Extraction error traceback: {traceback.format_exc()}")
            rejection_reason = f"Error: {str(e)}"
            return False, "", article.get("title", ""), rejection_reason

    def _perform_progressive_scrolling(self, page):
        """Perform progressive scrolling to expose all content."""
        try:
            page_height = page.evaluate("document.body.scrollHeight")
            view_height = page.evaluate("window.innerHeight")
            
            scroll_steps = min(4, max(2, int(page_height / view_height)))
            print(f"Performing {scroll_steps} scroll steps to load all content...")
            
            for i in range(1, scroll_steps + 1):
                scroll_position = (i * page_height) / scroll_steps
                page.evaluate(f"window.scrollTo(0, {scroll_position})")
                page.wait_for_timeout(1000)
            
            # Go back to top before extraction
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(1000)
            
        except Exception as e:
            print(f"Error during progressive scrolling: {e}")

    def _extract_content_with_soup(self, page):
        """Extract content using BeautifulSoup parsing."""
        try:
            # Get page HTML and parse with BeautifulSoup
            html_content = page.content()
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract readable text
            return extract_readable_text(soup)
            
        except Exception as e:
            print(f"Error during content extraction: {e}")
            return ""

    def _extract_title(self, page, article):
        """Extract title from the page."""
        try:
            # Try to get title from page
            page_title = page.title()
            if page_title and len(page_title.strip()) > 0:
                return page_title.strip()
                
            # Fallback to original title
            return article.get("title", "")
            
        except Exception as e:
            print(f"Error extracting title: {e}")
            return article.get("title", "")
