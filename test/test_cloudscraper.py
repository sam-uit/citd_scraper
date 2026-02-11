import cloudscraper

try:
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'darwin', 'mobile': False})
    print("Testing cloudscraper...")
    r = scraper.get("https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-hoc-vu/")
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("SUCCESS with cloudscraper!")
        print(f"Content length: {len(r.text)}")
    else:
        print("Failed with cloudscraper.")
except Exception as e:
    print(f"Error: {e}")
