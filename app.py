
import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime
from settings import settings

st.set_page_config(page_title="CITD Announcements", layout="wide")

# TODO: Language options

def load_data():
    data = []
    if not os.path.exists(settings.DATA_DIR):
        os.makedirs(settings.DATA_DIR)
    
    # Iterate through category subdirectories
    for cat_dir, cat_info in settings.CATEGORIES.items():
        # settings.CATEGORIES structure: {"hoc-vu": {"url": ..., "name": ..., "dir": ...}}
        # But wait, original CATEGORIES in app.py was simple dict: {"hoc-vu": "Thông báo học vụ", ...}
        # In settings.py it is complex dict.
        # Need to adapt logic.
        
        dir_name = cat_info['dir']
        cat_name = cat_info['name']
        
        dir_path = os.path.join(settings.DATA_DIR, dir_name)
        if not os.path.exists(dir_path):
            continue
            
        for filename in os.listdir(dir_path):
            if filename.endswith(".json"):
                filepath = os.path.join(dir_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        item = json.load(f)
                        item['filename'] = filename # Store filename for updates
                        item['category_key'] = cat_dir # Store category key (e.g., 'hoc-vu')
                        item['category_name'] = cat_name
                         # Ensure date is parsed for sorting
                        # Format: yyyy-mm-dd-hh-mm-ss
                        try:
                            item['date_obj'] = datetime.strptime(item['date'], "%Y-%m-%d-%H-%M-%S")
                        except ValueError:
                            item['date_obj'] = datetime.min
                        data.append(item)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                
    # Sort by date descending
    data.sort(key=lambda x: x['date_obj'], reverse=True)
    return data

def save_tags(item, new_tags):
    if not item.get('filename') or not item.get('category_key'):
        st.error("Cannot save tags: Filename or Category missing.")
        return
        
    # item['category_key'] is 'hoc-vu' or 'chung'
    # Need to get dir from settings
    cat_info = settings.CATEGORIES.get(item['category_key'])
    if not cat_info:
        st.error(f"Category {item['category_key']} not found in settings.")
        return
        
    filepath = os.path.join(settings.DATA_DIR, cat_info['dir'], item['filename'])
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        data['tags'] = new_tags
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        st.success("Tags updated!")
        # Update session state item too to reflect immediately
        item['tags'] = new_tags
        
    except Exception as e:
        st.error(f"Error saving tags: {e}")

def main():
    st.title("📢 CITD Announcements")
    
    # Load Data
    announcements = load_data()
    
    if not announcements:
        st.warning("No announcements found. Please run the scraper first.")
        return

    # Sidebar Filters
    st.sidebar.header("Filters")
    
    # Category Filter
    # Get names from settings
    cat_names = [info['name'] for info in settings.CATEGORIES.values()]
    cat_options = ["All"] + cat_names
    selected_cat = st.sidebar.selectbox("Category", cat_options)

    # Tag Filter
    all_tags = set()
    for item in announcements:
        if 'tags' in item:
            all_tags.update(item['tags'])
            
    selected_tags = st.sidebar.multiselect("Filter by Tags", sorted(list(all_tags)))
    
    # Search
    search_query = st.sidebar.text_input("Search Title/Content")
    
    # Filter Logic
    filtered_data = announcements
    
    if selected_cat != "All":
        filtered_data = [item for item in filtered_data if item['category_name'] == selected_cat]

    if selected_tags:
        filtered_data = [
            item for item in filtered_data 
            if any(tag in item.get('tags', []) for tag in selected_tags)
        ]
        
    if search_query:
        query = search_query.lower()
        filtered_data = [
            item for item in filtered_data
            if query in item['title'].lower() 
        ]
        
    st.sidebar.text(f"Showing {len(filtered_data)} items")

    # Main List
    if "selected_item" not in st.session_state:
        st.session_state.selected_item = None

    # Two columns layout: List and Detail
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Thông Báo")
        for item in filtered_data:
            # Format date for display
            date_display = item['date_obj'].strftime("%d/%m/%Y")
            
            # Card-like button
            # Simple heuristic for icon since we don't have explicit type without lookup
            cat_label = "📚" if "học vụ" in item['category_name'].lower() else "🔔"
            label = f"{item['title']}\n\n**{date_display}** | {cat_label} {item['category_name']}"
            if st.button(label, key=item['id'], use_container_width=True):
                st.session_state.selected_item = item

    with col2:
        if st.session_state.selected_item:
            item = st.session_state.selected_item
            
            st.markdown(f"## {item['title']}")
            st.caption(f"**Date:** {item['date_obj'].strftime('%d/%m/%Y %H:%M')} | **Author:** {item['author']} | **Category:** {item['category_name']}")
            
            # Tagging Interface
            st.divider()
            st.markdown("### Tags")
            
            current_tags = item.get('tags', [])
            
            # Streamlit re-runs on interaction, so input needs to handle state carefully.
            # We use a key based on item id.
            new_tags_str = st.text_input(
                "Edit Tags (comma separated)", 
                value=", ".join(current_tags), 
                key=f"tags_input_{item['id']}"
            )
            
            if st.button("Update Tags", key=f"btn_update_{item['id']}"):
                 new_tags_list = [t.strip() for t in new_tags_str.split(",") if t.strip()]
                 if new_tags_list != current_tags:
                      save_tags(item, new_tags_list)
                      st.rerun()

            st.write("Current tags:", ", ".join(current_tags) if current_tags else "No tags")

            st.divider()
            
            # Content
            # Load MD content
            # md path is relative strictly to category dir in new structure? 
            # In scraper we did: os.path.join(save_dir, md_name)
            # save_dir was DATA_DIR/cat_dir
            # content_md_path in json is basename.
            # So we need to join DATA_DIR, cat_key, and basename.
            
            cat_info = settings.CATEGORIES.get(item['category_key'])
            if cat_info:
                 md_path = os.path.join(settings.DATA_DIR, cat_info['dir'], item['content_md_path'])
                 if os.path.exists(md_path):
                     with open(md_path, 'r', encoding='utf-8') as f:
                         md_content = f.read()
                         st.markdown(md_content)
                 else:
                     st.error(f"Content file not found at {md_path}")
            else:
                 st.error(f"Category info missing for {item['category_key']}")
                
            # Assets
            if item.get('assets'):
                st.markdown("### Attached Files")
                for asset in item['assets']:
                    # Assets are likely still in DATA_DIR/assets or moved?
                    # Scraper says: ASSETS_DIR = DATA_DIR/assets
                    # But metadata stores basename.
                    asset_path = os.path.join(settings.ASSETS_DOCS_DIR, asset)
                    # In streamlit, we can provide download button
                    if os.path.exists(asset_path):
                        with open(asset_path, "rb") as f:
                             st.download_button(
                                 label=f"Download {asset}",
                                 data=f,
                                 file_name=asset,
                                 mime="application/octet-stream"
                             )
        else:
            st.info("Select an announcement from the list to view details.")

if __name__ == "__main__":
    main()
