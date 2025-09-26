"""Browser utilities for popup handling, data extraction, and stealth operations."""

import time
import random
from bs4 import BeautifulSoup

def get_human_delay(min_ms=800, max_ms=2500):
    """Get a random delay that mimics human behavior."""
    return random.randint(min_ms, max_ms)

def add_human_pause(page, min_ms=1000, max_ms=3000):
    """Add a human-like pause with mouse movement."""
    try:
        viewport = page.viewport_size
        if viewport:
            x = random.randint(100, viewport['width'] - 100)
            y = random.randint(100, viewport['height'] - 100)
            page.mouse.move(x, y)
        page.wait_for_timeout(get_human_delay(min_ms, max_ms))
    except Exception:
        page.wait_for_timeout(get_human_delay(min_ms, max_ms))

def handle_cookies_and_consent(page, timeout=15000):
    """Handle cookies and consent dialogs with Playwright selectors."""
    print("Handling cookies and consent with Playwright selectors...")
    
    start_time = time.time()
    max_time_ms = timeout
    
    try:
        if (time.time() - start_time) * 1000 > max_time_ms:
            print(f"Cookie handling timed out after {timeout}ms")
            return False
        
        # Priority 1: Explicit accept buttons
        accept_buttons = [
            "button:has-text('I accept all cookies')",
            "button:has-text('Accept all cookies')", 
            "button:has-text('Accept All')",
            "button:has-text('Accept')",
            "button:has-text('Accetta tutto')",  # Italian
            "button:has-text('Accetto')",       # Italian
        ]
        
        # Priority 2: Close/dismiss buttons  
        close_buttons = [
            "button:has-text('Close')",
            "button:has-text('Chiudi')",        # Italian
            "button:has-text('×')",
            "button[aria-label*='close']",
            "button[class*='close']",
        ]
        
        # Priority 3: Generic attribute-based selectors
        generic_buttons = [
            "[id*='accept'] button:not([href]):not(a)",
            "[class*='accept'] button:not([href]):not(a)", 
            "[id*='cookie'] button:not([href]):not(a)",
            "[class*='cookie'] button:not([href]):not(a)",
            "[data-testid*='accept'] button:not([href]):not(a)",
        ]
        
        # Combine all selectors in priority order
        button_selectors = accept_buttons + close_buttons + generic_buttons
        
        clicked = False
        
        # Try each selector with timeout check
        for selector in button_selectors:
            if (time.time() - start_time) * 1000 > max_time_ms:
                print(f"Cookie handling timed out during selector iteration")
                return False
            
            try:
                if page.query_selector(selector):
                    print(f"Found popup button with selector: {selector}")
                    page.click(selector, timeout=2000)
                    print(f"Successfully clicked popup button with selector: {selector}")
                    clicked = True
                    break
            except Exception:
                continue
        
        if clicked:
            print("Cookie/consent button clicked, waiting for page to stabilize...")
            remaining_time = max(0, max_time_ms - (time.time() - start_time) * 1000)
            if remaining_time > 1000:
                page.wait_for_timeout(min(2000, int(remaining_time)))
            return True
        
        return False
        
    except Exception as e:
        print(f"Error handling cookies and consent: {e}")
        return False

def handle_any_popups(page, aggressive=False):
    """Handle any type of popup, consent dialog, or cookie banner."""
    print(f"Trying {'aggressive ' if aggressive else ''}popup handling...")
    
    # Step 1: Try button clicking with human delays
    add_human_pause(page, 500, 1200)
    
    button_clicked = handle_cookies_and_consent(page, timeout=8000 if aggressive else 5000)
    
    if button_clicked:
        print("✅ Successfully handled popup with button clicking")
        add_human_pause(page, 1000, 2000)
        return True
    
    # Step 2: DOM removal fallback if aggressive
    if aggressive:
        print("Using DOM removal fallback...")
        add_human_pause(page, 1000, 2000)
        
        try:
            removed_count = page.evaluate("""() => {
                const removeElements = (selector) => {
                    const elements = document.querySelectorAll(selector);
                    let removed = 0;
                    elements.forEach(el => {
                        el.remove();
                        removed++;
                    });
                    return removed;
                };
                
                let removedCount = 0;
                
                // Remove elements with high z-index that could be overlays
                document.querySelectorAll('*').forEach(el => {
                    const style = window.getComputedStyle(el);
                    const zIndex = parseInt(style.zIndex);
                    if (zIndex > 999) {
                        const position = style.position;
                        if (position === 'fixed' || position === 'absolute') {
                            el.remove();
                            removedCount++;
                        }
                    }
                });
                
                // Remove common cookie/consent banners
                removedCount += removeElements('[class*="cookie"]:not(html):not(body)');
                removedCount += removeElements('[class*="consent"]:not(html):not(body)');
                removedCount += removeElements('[class*="popup"]:not(html):not(body)');
                removedCount += removeElements('[class*="banner"]:not(html):not(body)');
                removedCount += removeElements('[class*="overlay"]:not(html):not(body)');
                removedCount += removeElements('[class*="modal"]:not(html):not(body)');
                removedCount += removeElements('[id*="cookie"]:not(html):not(body)');
                removedCount += removeElements('[id*="consent"]:not(html):not(body)');
                
                document.body.style.overflow = 'auto';
                document.documentElement.style.overflow = 'auto';
                
                return removedCount;
            }""")
            
            if removed_count > 0:
                print("DOM removal: removed ${removed_count} elements")
                add_human_pause(page, 1500, 3000)
                return True
        except Exception as e:
            print(f"DOM removal failed: {e}")
    
    return False

def extract_readable_text(soup):
    """Extract readable text from BeautifulSoup object."""
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
        element.decompose()
    
    # Try to find main content areas
    content_selectors = [
        'article', 
        '[role="main"]', 
        '.content', 
        '#content',
        '.post-content',
        '.article-body',
        '.entry-content'
    ]
    
    for selector in content_selectors:
        content = soup.select_one(selector)
        if content:
            text = content.get_text(separator=' ', strip=True)
            if len(text) > 500:  # Only return if substantial content
                return text
    
    # Fallback to body text
    return soup.get_text(separator=' ', strip=True)
