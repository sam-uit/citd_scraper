import re
import hashlib
from datetime import datetime
from urllib.parse import urlparse
from slugify import slugify

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
