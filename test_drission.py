from DrissionPage import ChromiumPage, ChromiumOptions
import time

def test_drission():
    print("Initializing DrissionPage...")
    co = ChromiumOptions()
    # Mac optimization: try to find chrome path if not default? 
    # Usually DrissionPage finds it.
    
    # Set args to be less detectable (though DP handles much of this)
    co.set_argument('--no-first-run')
    # Explicit path for reliability on macOS
    co.set_browser_path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
    # co.set_local_port(9310)
    # co.headless() # Try headful first as it is more robust against CF
    print("DrissionPage options set. Launching...")
    
    try:
        page = ChromiumPage(co)
        print("Navigating to target...")
        page.get("https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-hoc-vu/")
        
        # Wait for page load (up to 20s)
        # page.wait.ele_displayed works for checking if an element appears
        if page.wait.ele_displayed('.tdb-category-grid-posts', timeout=20):
            print("SUCCESS! Found content.")
            print(f"Title: {page.title}")
            # Get the full HTML
            html_content = page.html
            print(f"HTML len: {len(html_content)}")
        else:
            print("Timeout waiting for specific element.")
            print(f"Title: {page.title}")
            print("Content snapshot:")
            print(page.html[:500]) # Print first 500 chars to verify logic
            
        page.quit()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_drission()
