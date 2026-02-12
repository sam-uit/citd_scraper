import os

# Configuration
BASE_URL = "https://www.citd.edu.vn"
CATEGORIES = {
    "hoc-vu": {
        "url": "https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-hoc-vu/",
        "name": "Thông báo học vụ",
        "dir": "hoc-vu"
    },
    "chung": {
        "url": "https://www.citd.edu.vn/chuyen-muc/dao-tao/thong-bao-chung/",
        "name": "Thông báo chung",
        "dir": "chung"
    }
}

DATA_DIR = "thongbao"
ASSETS_DIR_NAME = "assets"
# ASSETS_IMAGES_DIR and ASSETS_DOCS_DIR are now relative to category dir, handled in scraper
DB_FILE = os.path.join(DATA_DIR, "thongbao.json")
