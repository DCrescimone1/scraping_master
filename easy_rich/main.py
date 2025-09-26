#!/usr/bin/env python3
"""
Generic Web Scraper
Searches for user input on the web and scrapes the page content.
"""

from typing import Tuple, Optional, List
from src.serp_api_client import SerpAPIClient
from src.web_scraper import WebScraper


def get_scraping_mode() -> str:
    """Get user's preferred scraping mode."""
    print("\n=== Generic Web Scraper ===")
    print("Choose your option:")
    print("1. Search the web for something")
    print("2. Enter a direct URL to scrape")
    
    while True:
        choice = input("Your choice (1 or 2): ").strip()
        if choice == "1":
            return "search"
        elif choice == "2":
            return "url"
        else:
            print("Please enter 1 or 2")


def get_search_input() -> Tuple[str, Optional[str]]:
    """Get search text and optional website from user."""
    search_text = input("Enter search text (required): ").strip()
    if not search_text:
        raise ValueError("Search text cannot be empty!")
    
    website = input("Enter website to search on (optional, e.g., 'bbc.com'): ").strip()
    return search_text, website if website else None


def get_direct_url() -> str:
    """Get direct URL from user."""
    url = input("Enter the URL to scrape: ").strip()
    if not url:
        raise ValueError("URL cannot be empty!")
    if not (url.startswith('http://') or url.startswith('https://')):
        url = 'https://' + url
    return url


def display_subpage_menu(links: List[Tuple[str, str]]) -> None:
    """Display available subpages in a numbered menu with improved formatting."""
    if not links:
        print("\nNo additional subpages found on this domain.")
        return
    
    print(f"\nFound {len(links)} subpages on the same domain:")
    print("=" * 80)
    for i, (title, url) in enumerate(links, 1):
        # Truncate long titles for readability
        display_title = title[:60] + "..." if len(title) > 60 else title
        print(f"{i:2}. {display_title}")
        print(f"    └─ {url}")
        print()  # Add blank line between items for better readability
    print("=" * 80)


def handle_subpage_choice(links: List[Tuple[str, str]]) -> Optional[str]:
    """Handle user's subpage selection."""
    if not links:
        return None
        
    while True:
        print("\nEnter number (1-{0}), 'n' for new search, or 'q' to quit:".format(len(links)))
        choice = input("> ").strip().lower()
        
        if choice == 'q':
            return 'quit'
        elif choice == 'n':
            return 'new'
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(links):
                return links[num - 1][1]  # Return the URL
            else:
                print(f"\nPlease enter a number between 1 and {len(links)}")
        else:
            print("\nPlease enter a valid number, 'n', or 'q'")


def main() -> None:
    """Main application entry point with enhanced subpage support."""
    print("Starting Enhanced Generic Web Scraper...")
    
    try:
        serp_client = SerpAPIClient()
        web_scraper = WebScraper()
        session_folder = None
        
        while True:
            try:
                # Get scraping mode
                mode = get_scraping_mode()
                
                if mode == "search":
                    # Original search workflow
                    search_text, website = get_search_input()
                    print(f"\nSearching for '{search_text}'" + (f" on {website}" if website else " on the web"))
                    
                    # Search the web
                    search_results = serp_client.search_web(search_text, website)
                    if not search_results:
                        print("Failed to get search results")
                        continue
                    
                    # Extract target URL
                    target_url = serp_client.extract_first_url(search_results, website)
                    if not target_url:
                        print("No relevant URL found in search results")
                        continue
                        
                    print(f"Found URL: {target_url}")
                    filename = f"{search_text.replace(' ', '_').replace('/', '_')}_results"
                    
                else:  # mode == "url"
                    # Direct URL workflow
                    target_url = get_direct_url()
                    print(f"\nPreparing to scrape: {target_url}")
                    
                    # Generate filename from URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(target_url)
                    filename = f"{parsed_url.netloc.replace('.', '_')}_{parsed_url.path.replace('/', '_').strip('_')}"
                    filename = filename or "direct_scrape"

                # Create session folder on first scrape
                if session_folder is None:
                    if mode == "search":
                        session_folder = web_scraper.create_session_folder(target_url, search_text)
                    else:
                        session_folder = web_scraper.create_session_folder(target_url)
                    print(f"Created session folder: {session_folder}")

                # Scrape the page
                print("Scraping page content...")
                scraped_content = web_scraper.scrape_page(target_url)
                
                if not scraped_content:
                    print("Failed to scrape page content")
                    continue

                print(f"Successfully scraped: {scraped_content['title']}")
                
                # Save content to session folder
                web_scraper.save_content_to_session(scraped_content, filename, session_folder)
                
                # Extract and display subpage options
                links = web_scraper.extract_links_from_markdown(
                    scraped_content.get('markdown_content', ''), 
                    target_url
                )
                
                display_subpage_menu(links)
                
                # Handle subpage choice
                while links:
                    choice = handle_subpage_choice(links)
                    
                    if choice == 'quit':
                        print("Thanks for using the Enhanced Web Scraper!")
                        return
                    elif choice == 'new':
                        break  # Break inner loop to start new search
                    elif choice:  # It's a URL
                        # Find the title corresponding to the chosen URL
                        chosen_title = None
                        for title, url in links:
                            if url == choice:
                                chosen_title = title
                                break
                        
                        print(f"\nScraping subpage: {chosen_title or choice}")
                        subpage_content = web_scraper.scrape_page(choice)
                        
                        if subpage_content:
                            # Generate subpage filename using the readable title
                            if chosen_title:
                                subpage_filename = web_scraper.sanitize_filename(chosen_title)
                            else:
                                # Fallback to URL-based naming
                                from urllib.parse import urlparse
                                parsed_subpage = urlparse(choice)
                                subpage_filename = f"subpage_{parsed_subpage.path.replace('/', '_').strip('_')}"
                                subpage_filename = subpage_filename or "subpage"
                            
                            print(f"Successfully scraped subpage: {subpage_content['title']}")
                            web_scraper.save_content_to_session(subpage_content, subpage_filename, session_folder)
                            
                            # Extract links from subpage for further exploration
                            subpage_links = web_scraper.extract_links_from_markdown(
                                subpage_content.get('markdown_content', ''), 
                                choice
                            )
                            
                            if subpage_links:
                                display_subpage_menu(subpage_links)
                                links = subpage_links  # Update links for next iteration
                            else:
                                print("No more subpages found. Returning to main menu.")
                                break
                        else:
                            print("Failed to scrape subpage")
                
                # If no links or user chose 'new', continue to next iteration
                
            except ValueError as e:
                print(f"Input error: {e}")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                
    except Exception as e:
        print(f"Application error: {e}")
    
    print("Scraping session completed!")


if __name__ == "__main__":
    main()
