import argparse
from services.scraper import run_scraper

def main():
    parser = argparse.ArgumentParser(description="Scrape CITD announcements.")
    parser.add_argument("--all", action="store_true", help="Scrape all pages (default: page 1 only)")
    parser.add_argument("--pull", action="store_true", help="Force refresh all announcements")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no UI)")
    parser.add_argument("--download", action="store_true", help="Download document attachments (PDF, DOC, etc.)")
    parser.add_argument("-p", "--pages", type=int, default=1, help="Number of pages to scrape (default: 1)")
    parser.add_argument("--no-md", action="store_true", help="Skip Markdown file generation")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate Markdown files from JSON")
    args = parser.parse_args()
    
    run_scraper(args)

if __name__ == "__main__":
    main()
