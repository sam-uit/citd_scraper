import os
import shutil
import json
from settings import settings

def migrate_assets_local():
    print("Starting migration of assets to local category folders...")
    
    STATIC_IMG = "static/images"
    STATIC_DOC = "static/documents"
    
    # Iterate through categories
    for cat_key, cat_info in settings.CATEGORIES.items():
        cat_dir = os.path.join(settings.DATA_DIR, cat_info['dir'])
        if not os.path.exists(cat_dir):
            print(f"Directory not found: {cat_dir}")
            continue
            
        print(f"Processing category: {cat_info['name']}")
        
        # Create local asset dirs
        local_assets_img = os.path.join(cat_dir, settings.ASSETS_DIR_NAME, "images")
        local_assets_doc = os.path.join(cat_dir, settings.ASSETS_DIR_NAME, "documents")
        os.makedirs(local_assets_img, exist_ok=True)
        os.makedirs(local_assets_doc, exist_ok=True)
        
        files = [f for f in os.listdir(cat_dir) if f.endswith(".json")]
        for filename in files:
            filepath = os.path.join(cat_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                content = data.get('content', '')
                if not content:
                    continue
                
                # Update content paths AND move files if they exist in static
                # We need to parse content to find assets? 
                # Or just string replace and move files if we can guess filenames?
                # String replace is safer for content update.
                # But we need to move files.
                # We can iterate files in static/images and check if they are used in this content?
                # Or simpler:
                # 1. Replace `/app/static/images/` with `./assets/images/`
                # 2. Extract filename from the path.
                # 3. Check if file exists in static, move/copy it to local.
                
                # Let's do simple replaces first
                new_content = content.replace('/app/static/images/', './assets/images/')
                new_content = new_content.replace('/app/static/documents/', './assets/documents/')
                
                # Also handle old `../assets/` if any left
                new_content = new_content.replace('../assets/images/', './assets/images/')
                new_content = new_content.replace('../assets/documents/', './assets/documents/')
                
                # Now scan for filenames to move
                # Simple dumb scan: any file in static/images that appears in content?
                # Better: extract from content. But strict parsing is hard.
                # Let's iterate all files in static and see if they are in data['assets'] or content.
                
                # Check data['assets'] list (images + docs)
                # But ThongBao doesn't distinguish between image and doc easily in 'assets' list, just filenames.
                # But we know images are locally likely unique?
                # Actually, `scraper.py` logic was:
                # Images -> static/images
                # Docs -> static/documents
                
                # Let's just move ALL files from static to EACH category asset folder if referenced?
                # Or easier: Move ALL static files to ALL category folders? (Wasteful)
                # Correct way: Check usage.
                
                # Let's parse generated `new_content` for `./assets/images/filename`
                import re
                images = re.findall(r'\./assets/images/([^)\"\s]+)', new_content)
                docs = re.findall(r'\./assets/documents/([^)\"\s]+)', new_content)
                
                for img in images:
                    src = os.path.join(STATIC_IMG, img)
                    dst = os.path.join(local_assets_img, img)
                    if os.path.exists(src):
                        shutil.copy2(src, dst) # Copy to preserve for other cats if shared? (Unlikely but safe)
                        
                for doc in docs:
                    src = os.path.join(STATIC_DOC, doc)
                    dst = os.path.join(local_assets_doc, doc)
                    if os.path.exists(src):
                        shutil.copy2(src, dst)

                if content != new_content:
                    data['content'] = new_content
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"Updated {filename}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("Migration completed.")
    # Optional: cleanup static if empty? or keep for safety.

if __name__ == "__main__":
    migrate_assets_local()
