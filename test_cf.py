from curl_cffi import requests
import time

url = "https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-hoc-vu/"

configs = [
    # Basic impersonate without custom headers (let curl_cffi handle defaults)
    {"impersonate": "chrome", "headers": None},
    # Specific versions
    {"impersonate": "chrome110", "headers": None},
    {"impersonate": "chrome120", "headers": None},
    {"impersonate": "safari15_3", "headers": None},
    # With headers (simulating scraper.py but potentially stripping some)
    {"impersonate": "chrome", "headers": {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9', # Changed q value slightly
        # Remove Accept-Encoding to let curl handle it
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }},
]

print("Testing Cloudflare bypass...")

for i, cfg in enumerate(configs):
    print(f"\nTest {i+1}: impersonate={cfg['impersonate']}, headers={bool(cfg['headers'])}")
    try:
        r = requests.get(url, impersonate=cfg['impersonate'], headers=cfg['headers'], timeout=10)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("SUCCESS! This configuration works.")
            break
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(2)
