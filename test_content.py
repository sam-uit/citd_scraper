from curl_cffi import requests

url = "https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-hoc-vu/"

try:
    print(f"Fetching {url}...")
    # Basic request to see the block page
    r = requests.get(url, impersonate="chrome110", timeout=10)
    print(f"Status: {r.status_code}")
    print("Content Preview:")
    print(r.text[:1000]) # First 1000 chars
except Exception as e:
    print(f"Error: {e}")
