#!/usr/bin/env python3
"""
Generic Web Scraper
Searches for user input on the web and scrapes the page content.
"""

from src.serp_api_client import SerpAPIClient
from src.web_scraper import WebScraper


def main() -> None:
    """Main application entry point."""
    print("Starting Generic Web Scraper...")

    # Collect user input
    print("\n--- Generic Web Scraper ---")
    search_text = input("Enter search text (required): ").strip()
    website = input("Enter website to search on (optional, e.g., 'bbc.com'): ").strip()

    # Validate input
    if not search_text:
        print("Error: Search text cannot be empty!")
        return

    website = website if website else None
    print(f"\nSearching for '{search_text}'" + (f" on {website}" if website else " on the web"))

    # Initialize clients
    try:
        serp_client = SerpAPIClient()
        web_scraper = WebScraper()

        print("Searching the web...")

        # Search the web
        search_results = serp_client.search_web(search_text, website)

        if not search_results:
            print("Failed to get search results")
            return

        # Extract target URL
        target_url = serp_client.extract_first_url(search_results, website)

        if not target_url:
            print("No relevant URL found in search results")
            return

        print(f"Found URL: {target_url}")

        # Scrape the page
        print("Scraping page content...")
        scraped_content = web_scraper.scrape_page(target_url)

        if scraped_content:
            print(f"Successfully scraped: {scraped_content['title']}")

            # Save content
            filename = f"{search_text.replace(' ', '_').replace('/', '_')}_results"
            web_scraper.save_content(scraped_content, filename)

            print("Scraping completed successfully!")
        else:
            print("Failed to scrape page content")

    except Exception as e:
        print(f"Application error: {e}")


if __name__ == "__main__":
    main()
