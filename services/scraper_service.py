import os
import time
import json
import argparse
from DrissionPage import ChromiumPage, ChromiumOptions
from lxml import html
from datetime import datetime
import hashlib
from urllib.parse import urljoin, urlparse
from markdownify import markdownify as md

from models.ThongBao import ThongBao
from utils.helpers import clean_text, parse_date, extract_id_from_url, generate_id_and_date
from utils.network import download_resource, fetch_url

# Configuration
BASE_URL = "https://www.citd.edu.vn"
CATEGORIES = {
    "hoc-vu": {
        "url": "https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-hoc-vu/",
        "name": "Thông báo học vụ",
        "dir": "hoc-vu"
    },
    "chung": {
        "url": "https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-chung/",
        "name": "Thông báo chung",
        "dir": "chung"
    }
}

DATA_DIR = "thongbao"
ASSETS_DIR = os.path.join(DATA_DIR, "assets")
ASSETS_IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
ASSETS_DOCS_DIR = os.path.join(ASSETS_DIR, "documents")
DB_FILE = os.path.join(DATA_DIR, "thongbao.json")

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_IMAGES_DIR, exist_ok=True)
os.makedirs(ASSETS_DOCS_DIR, exist_ok=True)
for cat in CATEGORIES.values():
    os.makedirs(os.path.join(DATA_DIR, cat["dir"]), exist_ok=True)

# Database Management
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading DB: {e}")
    return {}

def save_db(db):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving DB: {e}")

# DrissionPage Initialization
browser = None

def init_browser(headless=False):
    global browser
    print("Initializing Browser...")
    try:
        co = ChromiumOptions()
        co.set_argument('--no-first-run')
        # Explicit path for reliability on macOS
        co.set_browser_path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        # co.set_local_port(9310) 
        
        if headless:
            co.headless()
            
        print(f"DrissionPage options set (Headless: {headless}). Launching...")
        browser = ChromiumPage(co)
        print("Browser initialized successfully.")
        return browser
    except Exception as e:
        print(f"Error initializing browser: {e}")
        return None


def parse_list_page(content, is_local=False):
    tree = html.fromstring(content)
    announcements = []
    # Logic to find all announcement items
    # Restrict to Main Content areas to avoid Sidebars (e.g., "Bài viết mới nhất")
    # 1. Grid Items (Top featured): inside .tdb-category-grid-posts -> .tdb_module_cat_grid
    # 2. Loop Items (Main list): inside .tdb-category-loop-posts -> .td_module_wrap
    xpath_query = (
        '//div[contains(@class, "tdb-category-grid-posts")]//div[contains(@class, "tdb_module_cat_grid")] | '
        '//div[contains(@class, "tdb-category-loop-posts")]//div[contains(@class, "td_module_wrap")]'
    )
    items = tree.xpath(xpath_query)

    seen_urls = set()

    for item in items:
        try:
            # Title & URL
            link_node = item.xpath('.//h3[contains(@class, "entry-title")]/a')
            if not link_node:
                continue

            url = link_node[0].get('href')
            title = link_node[0].get('title')

            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Author
            author_node = item.xpath('.//span[contains(@class, "td-post-author-name")]/a')
            author = author_node[0].text if author_node else "Unknown"

            # Time
            time_node = item.xpath('.//span[contains(@class, "td-post-date")]/time')
            time_str = time_node[0].get('datetime') if time_node else ""

            announcements.append({
                "url": url,
                "title": title,
                "author": author,
                "time_str": time_str
            })
        except Exception as e:
            print(f"Error parsing item: {e}")
            continue

    return announcements

def parse_detail_page(content, url, browser):
    tree = html.fromstring(content)

    try:
        # Title
        title_nodes = tree.xpath('//h1[contains(@class, "tdb-title-text")]/text()')
        title = title_nodes[0] if title_nodes else ""

        # Author
        author_nodes = tree.xpath('//a[contains(@class, "tdb-author-name")]/text()')
        author = author_nodes[0] if author_nodes else "Unknown"

        # Date
        date_nodes = tree.xpath('//time[contains(@class, "entry-date")]/@datetime')
        date_str = date_nodes[0] if date_nodes else ""

        # Content
        content_divs = tree.xpath('//div[contains(@class, "tdb_single_content")]//div[contains(@class, "tdb-block-inner")]')
        local_assets_map = {}
        
        if content_divs:
            content_div = content_divs[0]

            # 1. Process Images
            # Find all img tags, download content, and replace src with local relative path
            for img in content_div.xpath('.//img'):
                src = img.get('src')
                if src:
                    # Fix relative URLs
                    if not src.startswith('http'):
                        src = urljoin(BASE_URL, src)
                        
                    # Download image
                    local_path = download_resource(src, ASSETS_IMAGES_DIR, browser)
                    if local_path:
                        # Compute relative path for Markdown (thongbao/hoc-vu/.. -> thongbao/assets/images/..)
                        # We save MD in thongbao/hoc-vu/. So rel path is ../../assets/images/filename
                        # Actually simpler: just use relative path from the DATA_DIR root if we view from there?
                        # But MD is viewed relative to MD file.
                        # MD is in `thongbao/category/`. Assets in `thongbao/assets/images/`.
                        # So relative path is `../../assets/images/filename`.
                        
                        filename = os.path.basename(local_path)
                        rel_path = f"../assets/images/{filename}"
                        img.set('src', rel_path)
                        # Also replace srcset if exists to prevent browser loading original
                        if img.get('srcset'):
                            del img.attrib['srcset']
                        
                        # Remove parent <a> tag if exists (to remove original link)
                        parent = img.getparent()
                        if parent is not None and parent.tag == 'a':
                            # To replace 'parent' (<a>) with 'img', we need the grandparent
                            grandparent = parent.getparent()
                            if grandparent is not None:
                                grandparent.replace(parent, img)
                        
                        local_assets_map[src] = filename

            # Remove redundant "Download" buttons from wp-block-file
            for btn in content_div.xpath('.//a[contains(@class, "wp-block-file__button")]'):
                btn.getparent().remove(btn)

            # Remove object tags
            for obj in content_div.xpath('.//object'):
                obj.getparent().remove(obj)

            # Convert to Markdown
            content_html = html.tostring(content_div, encoding='unicode')
            content_text = md(content_html, heading_style="ATX").strip()

            # Extract assets (Docs)
            # Find all links to files
            asset_links = content_div.xpath('.//a[contains(@href, ".pdf") or contains(@href, ".doc") or contains(@href, ".xls") or contains(@href, ".zip") or contains(@href, ".rar") or contains(@href, ".ppt")]/@href')
            asset_links = list(set(asset_links))
        else:
            content_text = ""
            asset_links = []

        # Tags
        tags = tree.xpath('//ul[contains(@class, "tdb-tags")]/li/a/text()')

        return {
            "title": title,
            "author": author,
            "date": date_str,
            "content": content_text,
            "tags": tags,
            "asset_links": asset_links
        }
    except Exception as e:
        print(f"Error parsing detail {url}: {e}")
        return None



def check_if_exists(slug, formatted_date, category_key, db, force_pull=False):
    """
    Check if a ThongBao with this ID exists in DB or file system.
    Returns: (exists: bool, should_update: bool)
    """
    if force_pull:
        return True, True

    # 1. Check in Database
    if slug in db:
        existing_date = db[slug].get('date', '')
        if existing_date == formatted_date:
            print(f"Skipping {slug} (DB): Date {formatted_date} unchanged.")
            return True, False
        else:
            print(f"Updating {slug} (DB): Date changed from {existing_date} to {formatted_date}")
            return True, True

    # 2. Fallback: Check file system (for first run or out-of-sync)
    cat_dir = os.path.join(DATA_DIR, CATEGORIES[category_key]['dir'])
    try:
        if not os.path.exists(cat_dir):
            return False, True
            
        valid_files = [f for f in os.listdir(cat_dir) if f.endswith(f"_{slug}.json") or f.endswith(f"-{slug}.json")]
    except FileNotFoundError:
        return False, True

    if not valid_files:
        return False, True

    # Check the latest one
    latest_file = sorted(valid_files)[-1]
    json_path = os.path.join(cat_dir, latest_file)

    try:
        existing = ThongBao.load_from_json(json_path)
        # Update DB since we found it on disk but not in DB
        db[slug] = {
            "id": slug,
            "date": existing.date,
            "type": existing.topic,
            "scraped_time": existing.created_at
        }
        # Save DB immediately or wait? Better save to avoid data loss, but costly. 
        # For now, we just update memory and it will be saved if we hit save_announcement or at end.
        # But here we might skip saving, so DB won't persist if we skip.
        # So we should save DB if we populate it from file.
        save_db(db) # Sync back to DB
        
        if existing.date == formatted_date:
            print(f"Skipping {slug} (File->DB): Date {formatted_date} unchanged.")
            return True, False 
        else:
            print(f"Updating {slug} (File): Date changed from {existing.date} to {formatted_date}")
            return True, True
    except Exception as e:
        print(f"Error checking duplicate for {slug}: {e}")
        return False, True

def save_announcement(data, category_key="hoc-vu", db=None, download_docs=False, no_md=False):
    # ID from URL or title hash
    if not data or not data.get('title'):
        return

    slug, formatted_date = generate_id_and_date(data)

    cat_info = CATEGORIES.get(category_key, CATEGORIES["hoc-vu"])
    save_dir = os.path.join(DATA_DIR, cat_info["dir"])

    # Filenames
    base_name = f"{formatted_date}-{slug}"
    json_path = os.path.join(save_dir, f"{base_name}.json")
    md_path = os.path.join(save_dir, f"{base_name}.md")

    # Handle Assets
    local_assets = []
    
    # Check if download flag is on for documents
    if download_docs:
        for asset_url in data.get('asset_links', []):
            # Fix relative URLs if needed
            if not asset_url.startswith('http'):
                asset_url = urljoin(BASE_URL, asset_url)
                
            local_path = download_resource(asset_url, ASSETS_DOCS_DIR, browser)
            if local_path:
                local_assets.append(local_path)

    # Save Markdown Content
    if not no_md:
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# {data['title']}\n\n")
            f.write(f"- **Author:** {data['author']}\n")
            f.write(f"- **Date:** {data['date']}\n")
            f.write(f"- **Original URL:** {data['url']}\n\n")
            f.write(data['content'])

            if data.get('asset_links'):
                f.write("\n\n## Attachments\n\n")
                for asset_url in data.get('asset_links'):
                     # Fix relative URLs if needed
                    if not asset_url.startswith('http'):
                        asset_url = urljoin(BASE_URL, asset_url)
                    
                    filename = os.path.basename(urlparse(asset_url).path)
                    
                    # Check if we have it locally (either just downloaded or existed)
                    local_path = os.path.join(ASSETS_DOCS_DIR, filename)
                    
                    if download_docs and os.path.exists(local_path):
                         # Rel path from save_dir (thongbao/cat) to ASSETS_DOCS_DIR (thongbao/assets/documents)
                         # ../assets/documents/filename
                         rel_path = f"../assets/documents/{filename}"
                         f.write(f"- [{filename}]({rel_path}) (Local) | [Original]({asset_url})\n")
                    else:
                         f.write(f"- [{filename}]({asset_url}) (Online)\n")

    # Create ThongBao object
    tb = ThongBao(
        id=slug,
        title=data['title'],
        date=formatted_date,
        author=data['author'],
        topic=cat_info["name"],
        tags=data.get('tags', []),
        content_md_path=os.path.basename(md_path) if not no_md else "",
        original_url=data['url'],
        assets=[os.path.basename(a) for a in local_assets],
        content=data['content']
    )

    # Save using Model
    tb.save_to_json(json_path)
    
    # Update DB
    if db is not None:
        db[slug] = {
            "id": slug,
            "date": formatted_date,
            "type": cat_info["name"],
            "scraped_time": tb.created_at
        }
        save_db(db)
        
    print(f"Saved to {cat_info['dir']}: {data['title']}")

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

    print("Starting CITD Scraper...")

    if args.regenerate:
        print("Mode: Regenerating Markdown files...")
        # Load all JSONs and regenerate MD
        for cat_key, cat_info in CATEGORIES.items():
            cat_dir = os.path.join(DATA_DIR, cat_info['dir'])
            if not os.path.exists(cat_dir):
                continue
                
            print(f"Processing {cat_info['name']}...")
            for filename in os.listdir(cat_dir):
                if filename.endswith(".json"):
                    json_path = os.path.join(cat_dir, filename)
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # If content is missing, we can't regenerate fully unless we re-fetch?
                        # But scraper logic saves content if available.
                        # data usually has 'content' field now.
                        
                        if 'content' not in data:
                             print(f"Skipping {filename}: No content field.")
                             continue
                             
                        # Reuse save_announcement logic? 
                        # Ideally yes, but save_announcement also creates ThongBao obj and updates DB.
                        # We just want to rewrite MD.
                        
                        # Let's extract save_md logic or just repeat it here properly.
                        # Or call save_announcement but modify it to accept data directly?
                        # save_announcement expects `data` dict with specific keys.
                        # `ThongBao.to_dict()` has these keys.
                        
                        # Let's use save_announcement but with a flag to ONLY save MD?
                        # No, save_announcement does too much.
                        
                        md_path = os.path.join(cat_dir, filename.replace(".json", ".md"))
                        
                        with open(md_path, 'w', encoding='utf-8') as f:
                            f.write(f"# {data['title']}\n\n")
                            f.write(f"- **Author:** {data['author']}\n")
                            f.write(f"- **Date:** {data['date']}\n")
                            f.write(f"- **Original URL:** {data['original_url']}\n\n")
                            f.write(data['content'])

                            if data.get('assets'): # ThongBao obj stores assets filenames
                                f.write("\n\n## Attachments\n\n")
                                for asset in data.get('assets'):
                                    # Local asset path
                                    # md is in thongbao/cat/
                                    # assets in thongbao/assets/documents/
                                    rel_path = f"../assets/documents/{asset}"
                                    # We don't have original URL easily for assets unless preserved in data?
                                    # ThongBao obj stores 'assets' as list of strings (filenames).
                                    # The original 'asset_links' might be lost if not stored in ThongBao model!
                                    # Checked ThongBao.py: it stores 'assets' list.
                                    # But `data` loaded from json IS the ThongBao dict.
                                    
                                    # Wait, `save_announcement` uses `data['asset_links']` which comes from parser.
                                    # `ThongBao` object does NOT store `asset_links` (original URLs).
                                    # So we can't regenerate the "| [Original](url)" part if we only have `ThongBao` json.
                                    # Unless we add `asset_links` to `ThongBao` model too!
                                    
                                    f.write(f"- [{asset}]({rel_path}) (Local)\n")
                                    
                        print(f"Regenerated {md_path}")
                        
                    except Exception as e:
                        print(f"Error regenerating {filename}: {e}")
        return

    # Init Browser
    if not init_browser(headless=args.headless):
        print("Failed to initialize browser. Exiting.")
        return

    # Load DB
    db = load_db()
    print(f"Loaded {len(db)} items from database.")
    
    if args.all:
        print("Mode: Scraping ALL pages.")
        max_pages = 1000 # High limit to scrape everything until no content
    elif args.pages > 1:
        print(f"Mode: Scraping first {args.pages} pages.")
        max_pages = args.pages
    else:
        print("Mode: Scraping first page ONLY.")
        max_pages = 1

    if args.download:
        print("Mode: Downloading document attachments enabled.")

    if args.no_md:
        print("Mode: No Markdown generation (saving JSON only).")

    for cat_key, cat_info in CATEGORIES.items():
        print(f"Scraping Category: {cat_info['name']}...")
        page = 1
        while page <= max_pages:
            url = cat_info['url']
            if page > 1:
                url = f"{cat_info['url']}page/{page}/"

            print(f"Scraping Page {page}...")
            content = fetch_url(url, browser)
            if not content:
                print("Failed to retrieve page content. Stopping.")
                break

            announcements = parse_list_page(content)
            if not announcements:
                print("No announcements found on this page. Stopping.")
                break

            for item in announcements:
                # Check duplicate before fetching details
                temp_data = {'title': item['title'], 'driver': '', 'url': item['url']}
                if item.get('time_str'):
                     temp_data['date'] = item['time_str']

                slug, formatted_date = generate_id_and_date(temp_data)

                # Check if exists
                exists, should_update = check_if_exists(slug, formatted_date, cat_key, db, force_pull=args.pull)

                if exists and not should_update:
                    continue

                detail_url = item['url']
                detail_content = fetch_url(detail_url, browser)
                if detail_content:
                    detail_data = parse_detail_page(detail_content, detail_url, browser)
                    if detail_data:
                        detail_data['url'] = detail_url
                        save_announcement(detail_data, category_key=cat_key, db=db, download_docs=args.download, no_md=args.no_md)

                # Rate limiting
                time.sleep(1)

            page += 1
            time.sleep(2)

    print("Scraping completed.")
    
    # Save final state of DB just in case
    save_db(db)
    
    if browser:
        browser.quit()

if __name__ == "__main__":
    main()
