
import os
import json
from scraper import parse_list_page, parse_detail_page, save_announcement, check_if_exists, generate_id_and_date

BASE_PATH = "/Users/samdinh/UIT/citd_scraper"
FILES = {
    "hoc-vu": os.path.join(BASE_PATH, "thongbaohocvu.html"),
    "chung": os.path.join(BASE_PATH, "thongbaochung.html")
}
DETAIL_FILE = os.path.join(BASE_PATH, "thongbaocuthe.html")

def process_local():
    print("Processing local files...")
    
    if not os.path.exists(DETAIL_FILE):
        print(f"Detail file not found: {DETAIL_FILE}")
        return

    with open(DETAIL_FILE, 'r', encoding='utf-8') as df:
        detail_content = df.read()

    for cat_key, file_path in FILES.items():
        print(f"Processing category: {cat_key} from {file_path}")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                announcements = parse_list_page(content, is_local=True)
                print(f"Found {len(announcements)} items in {cat_key}.")
                
                for item in announcements:
                    # Check duplicate before processing
                    temp_data = {'title': item['title'], 'driver': '', 'url': item['url']}
                    if item.get('time_str'):
                            temp_data['date'] = item['time_str']
                    
                    slug, formatted_date = generate_id_and_date(temp_data)
                    
                    # Check if exists in the specific category
                    exists, should_update = check_if_exists(slug, formatted_date, cat_key)
                    if exists and not should_update:
                        continue

                    # We use the title from the list, but content from the detail file
                    detail_data = parse_detail_page(detail_content, item['url'])
                    if detail_data:
                        detail_data['url'] = item['url']
                        detail_data['title'] = item['title'] 
                        
                        # Use Author and Date from LIST page for local simulation
                        if item.get('author') and item['author'] != "Unknown":
                            detail_data['author'] = item['author']
                            
                        if item.get('time_str'):
                            detail_data['date'] = item['time_str']
                        
                        save_announcement(detail_data, category_key=cat_key)
        else:
             print(f"File not found: {file_path}")
                            
    print("Local processing completed.")

if __name__ == "__main__":
    process_local()
