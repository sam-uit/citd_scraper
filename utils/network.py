import os
import hashlib
from urllib.parse import urlparse

def download_resource(url, save_dir, browser, base_url="https://www.citd.edu.vn"):
    try:
        if not browser:
            return None
            
        # Extract filename
        path = urlparse(url).path
        filename = os.path.basename(path)
        if not filename:
            filename = f"resource_{hashlib.md5(url.encode()).hexdigest()}"
            
        # Check if exists
        filepath = os.path.join(save_dir, filename)
        if os.path.exists(filepath):
            return filepath

        print(f"Downloading: {url} ...")
        
        # Method 1: requests with browser cookies (most robust for images)
        import requests
        
        # Correct DrissionPage usage based on debug:
        # browser.cookies() returns CookiesList which has as_dict() method.
        try:
             cookies = browser.cookies().as_dict()
        except Exception as e:
             print(f"Cookie error: {e}")
             cookies = {}

        headers = {
            "User-Agent": browser.user_agent,
            "Referer": base_url
        }
        
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        else:
            print(f"Failed to download {url}: Status {response.status_code}")
            
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    return None

def fetch_url(url, browser, retries=3):
    import time
    print(f"Fetching {url}...")
    if not browser:
        print("Browser not initialized.")
        return None
        
    for i in range(retries):
        try:
            browser.get(url)
            
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
                pass
            except:
                pass
    return None
