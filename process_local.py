
import os
import json
from scraper import parse_list_page, parse_detail_page, save_announcement

BASE_PATH = "/Users/samdinh/UIT/citd_scraper"
LIST_FILE = os.path.join(BASE_PATH, "thongbaohocvu.html")
DETAIL_FILE = os.path.join(BASE_PATH, "thongbaocuthe.html")

def process_local():
    print("Processing local files...")
    
    # Simulate List Page
    if os.path.exists(LIST_FILE):
        with open(LIST_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            announcements = parse_list_page(content, is_local=True)
            print(f"Found {len(announcements)} items in list.")
            
            # Since we only have one detail page, we will use it for ALL items 
            # to populate data for testing UI.
            # In a real scenario, we would have matched filenames or similar.
            
            if os.path.exists(DETAIL_FILE):
                with open(DETAIL_FILE, 'r', encoding='utf-8') as df:
                    detail_content = df.read()
                    
                    for item in announcements:
                        # We use the title from the list, but content from the detail file
                        # We need to preserve the URL from the list for unique ID generation
                        
                        detail_data = parse_detail_page(detail_content, item['url'])
                        if detail_data:
                            # Override title/date/author from list if we want consistency, 
                            # OR use detail page data. 
                            # Since all items will point to same detail content, they will look identical
                            # except for URL. 
                            # Let's mix them: Use list title/date/url, but detail content.
                            
                            detail_data['url'] = item['url']
                            detail_data['title'] = item['title'] 
                            
                            # Critical: Use Author and Date from LIST page for local simulation
                            # because the single detail file (thongbaocuthe.html) has static info.
                            if item.get('author') and item['author'] != "Unknown":
                                detail_data['author'] = item['author']
                                
                            if item.get('time_str'):
                                detail_data['date'] = item['time_str']
                            
                            save_announcement(detail_data)
                            
    print("Local processing completed.")

if __name__ == "__main__":
    process_local()
