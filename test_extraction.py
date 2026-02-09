from lxml import html
import os

with open("thongbaocuthe.html", "r", encoding="utf-8") as f:
    content = f.read()

tree = html.fromstring(content)
content_divs = tree.xpath('//div[contains(@class, "tdb_single_content")]//div[contains(@class, "tdb-block-inner")]')

print(f"Found {len(content_divs)} content divs")

if content_divs:
    content_div = content_divs[0]
    
    # Check links BEFORE modification
    raw_links = content_div.xpath('.//a/@href')
    print(f"Raw links count: {len(raw_links)}")
    
    # Try finding PDF
    pdfs = content_div.xpath('.//a[contains(@href, ".pdf")]/@href')
    print(f"PDFs found: {pdfs}")
    
    # Simulate modification
    for btn in content_div.xpath('.//a[contains(@class, "wp-block-file__button")]'):
        print("Removing button")
        btn.getparent().remove(btn)
    
    for obj in content_div.xpath('.//object'):
        print("Removing object")
        obj.getparent().remove(obj)
        
    # Check links AFTER modification
    asset_links = content_div.xpath('.//a[contains(@href, ".pdf") or contains(@href, ".doc") or contains(@href, ".xls") or contains(@href, ".zip") or contains(@href, ".rar")]/@href')
    print(f"Asset links extracted: {asset_links}")
