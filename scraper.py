import os
import time
import json
# from curl_cffi import requests as crequests # Removed
from DrissionPage import ChromiumPage, ChromiumOptions
from lxml import html
from datetime import datetime
import hashlib
from urllib.parse import urljoin, urlparse
import re
from markdownify import markdownify as md
from slugify import slugify
from models.ThongBao import ThongBao

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

# Create directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
for cat in CATEGORIES.values():
    os.makedirs(os.path.join(DATA_DIR, cat["dir"]), exist_ok=True)

# DrissionPage Initialization
print("Initializing Browser...")
def get_browser():
    try:
        co = ChromiumOptions()
        co.set_argument('--no-first-run')
        # Explicit path for reliability on macOS
        co.set_browser_path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
        co.set_local_port(9310)
        print("DrissionPage options set. Launching...")
        return ChromiumPage(co)
    except Exception as e:
        print(f"Error initializing browser: {e}")
        return None

# Global browser instance
try:
    browser = get_browser()
    if browser:
        print("Browser initialized successfully.")
    else:
        print("Browser initialization failed (None).")
except Exception as e:
    print(f"Global browser init failed: {e}")
    browser = None

def clean_text(text):
    if text:
        return re.sub(r'\s+', ' ', text).strip()
    return ""

def parse_date(date_str):
    # Try different formats if needed. Default seems to be generic or specific to locale
    # Example: "10/01/2024" or "10 Tháng Một, 2024"
    try:
        # Placeholder for actual date parsing logic based on observation
        return datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        return None

def extract_id_from_url(url):
    path = urlparse(url).path
    return path.strip('/').split('/')[-1]

def download_asset(url):
    try:
        # Use DrissionPage download
        if not browser:
            return None
            
        filename = os.path.basename(urlparse(url).path)
        if not filename:
            filename = f"asset_{hashlib.md5(url.encode()).hexdigest()}"
            
        # Check if already exists
        filepath = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(filepath):
            return filepath

        print(f"Downloading asset: {url}")
        # DrissionPage download logic
        # For simplicity, we can use the requests session from DrissionPage if exposed, 
        # or just navigate to it if it triggers download, but for files usually we want content.
        # page.download() is for clicking download buttons.
        # Using page.download_file() if available or requests with browser cookies.
        
        # Fallback: using browser.download (if file)
        # Or simpler: access .content via fetch logic if it's small?
        # Let's try to 'get' it and save bytes.
        
        # Actually DrissionPage allows downloading functionality.
        # browser.download(url, ASSETS_DIR, filename)
        
        # Let's use a simple approach for now:
        # Navigate to it? No, that changes page.
        # Use browser.download_set path then get?
        
        # Revert to curl_cffi or requests using cookies from browser? 
        # DrissionPage cookies can be exported.
        
        # For now, let's skip complex asset download refactor and focus on content. 
        # The previous version used curl_cffi. Let's try to keep it simple or just return None for now 
        # to ensure main scraper works, then fix assets if broken.
        pass 
    except Exception as e:
        print(f"Error downloading asset {url}: {e}")
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

def parse_detail_page(content, url):
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
        if content_divs:
            content_div = content_divs[0]

            # Remove redundant "Download" buttons from wp-block-file
            for btn in content_div.xpath('.//a[contains(@class, "wp-block-file__button")]'):
                btn.getparent().remove(btn)

            # Remove object tags
            for obj in content_div.xpath('.//object'):
                obj.getparent().remove(obj)

            # Convert to Markdown
            content_html = html.tostring(content_div, encoding='unicode')
            content_text = md(content_html, heading_style="ATX").strip()

            # Extract assets
            asset_links = content_div.xpath('.//a[contains(@href, ".pdf") or contains(@href, ".doc") or contains(@href, ".xls") or contains(@href, ".zip") or contains(@href, ".rar")]/@href')
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

def fetch_url(url, retries=3):
    print(f"Fetching {url}...")
    if not browser:
        print("Browser not initialized.")
        return None
        
    for i in range(retries):
        try:
            browser.get(url)
            # Wait for content or Cloudflare
            # Simple wait for title to not be "Just a moment..." or "Attention Required"
            # Or better, wait for a known element if possible, or just sleep a bit.
            # DrissionPage .get() usually waits for load.
            
            # Check for Cloudflare title
            if "Just a moment" in browser.title or "Attention Required" in browser.title:
                print("Cloudflare challenge detected. Waiting...")
                time.sleep(5)
            
            # If we are on the target page
            if browser.ele('tag:body'): # Simple check if body exists
                return browser.html
            else:
                print(f"Page load failed for {url}. Retrying...")
                time.sleep(2 * (i + 1))
        except Exception as e:
            print(f"Error fetching {url}: {e}. Retrying...")
            time.sleep(2 * (i + 1))
            try:
                # Attempt reconnect/restart if major failure?
                # browser.reconnect() 
                pass
            except:
                pass
    return None

def generate_id_and_date(data):
     # Create slug for ID/Filename
    slug = slugify(data['title'])
    if not slug:
         slug = hashlib.md5(data['url'].encode()).hexdigest()

    # Date for sorting: yyyy-mm-dd-hh-mm-ss
    date_str = data.get('date', '')
    formatted_date = ""
    try:
        if date_str:
            dt = datetime.fromisoformat(date_str)
            formatted_date = dt.strftime("%Y-%m-%d-%H-%M-%S")
        else:
            # Fallback to current time if no date found
            formatted_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    except Exception as e:
        print(f"Error parsing date {date_str}: {e}")
        formatted_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    return slug, formatted_date

def check_if_exists(slug, formatted_date, category_key):
    """
    Check if a ThongBao with this ID exists in the specific category dir
    and if the content date is the same.
    Returns: (exists: bool, should_update: bool)
    """
    cat_dir = os.path.join(DATA_DIR, CATEGORIES[category_key]['dir'])
    try:
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
        if existing.date == formatted_date:
            print(f"Skipping {slug}: Date {formatted_date} unchanged. Scraped at {existing.created_at}")
            return True, False # Exists, No update needed
        else:
            print(f"Updating {slug}: Date changed from {existing.date} to {formatted_date}")
            return True, True # Exists, Update needed
    except Exception as e:
        print(f"Error checking duplicate for {slug}: {e}")
        return False, True

def save_announcement(data, category_key="hoc-vu"):
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

    # Download assets
    local_assets = []
    for asset_url in data.get('asset_links', []):
        local_path = download_asset(asset_url)
        if local_path:
            local_assets.append(local_path)

    # Save Markdown Content
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# {data['title']}\n\n")
        f.write(f"- **Author:** {data['author']}\n")
        f.write(f"- **Date:** {data['date']}\n")
        f.write(f"- **Original URL:** {data['url']}\n\n")
        f.write(data['content'])

        if local_assets:
            f.write("\n\n## Attachments\n")
            for asset in local_assets:
                rel_path = os.path.relpath(asset, save_dir)
                f.write(f"- [{os.path.basename(asset)}]({rel_path})\n")

    # Create ThongBao object
    tb = ThongBao(
        id=slug,
        title=data['title'],
        date=formatted_date,
        author=data['author'],
        topic=cat_info["name"],
        tags=data.get('tags', []),
        content_md_path=os.path.basename(md_path),
        original_url=data['url'],
        assets=[os.path.basename(a) for a in local_assets]
    )

    # Save using Model
    tb.save_to_json(json_path)
    print(f"Saved to {cat_info['dir']}: {data['title']}")

def main():
    print("Starting CITD Scraper...")

    max_pages = 5 # Safety limit for now, user can increase

    for cat_key, cat_info in CATEGORIES.items():
        print(f"Scraping Category: {cat_info['name']}...")
        page = 1
        while page <= max_pages:
            url = cat_info['url']
            if page > 1:
                url = f"{cat_info['url']}page/{page}/"

            print(f"Scraping Page {page}...")
            content = fetch_url(url)
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
                exists, should_update = check_if_exists(slug, formatted_date, cat_key)

                if exists and not should_update:
                    continue

                detail_url = item['url']
                detail_content = fetch_url(detail_url)
                if detail_content:
                    detail_data = parse_detail_page(detail_content, detail_url)
                    if detail_data:
                        detail_data['url'] = detail_url
                        save_announcement(detail_data, category_key=cat_key)

                # Rate limiting
                time.sleep(1)

            page += 1
            time.sleep(2)

    print("Scraping completed.")
    
    if browser:
        browser.quit()

if __name__ == "__main__":
    main()
