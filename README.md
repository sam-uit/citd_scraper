# CITD Scraper & Viewer

This project provides a web scraper for CITD announcements and a Streamlit application to view and tag them locally.

## Setup

1.  **Install uv** (if not already installed):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Usage

### 1. Scraper

To scrape the latest announcements:

```bash
uv run python scraper.py
```

To scrape **all** pages (deep scrape):
```bash
uv run python scraper.py --all
```

To **force refresh** all announcements (ignore local database):
```bash
uv run python scraper.py --pull
```

To **download document attachments** (PDF, DOC, etc.):
```bash
uv run python scraper.py --download
```

To **scrape a specific number of pages** (e.g., 2 newest pages):
```bash
uv run python scraper.py -p 2
```

To run in **headless mode** (experimental, may be blocked by Cloudflare):
```bash
uv run python scraper.py --headless
```

### 📂 Directory Structure
Scraped data is organized in the `thongbao/` directory:
- `thongbao.json`: Centralized index database.
- `thongbao/assets/images/`: Downloaded images.
- `thongbao/assets/documents/`: Downloaded documents (if `--download` is used).
- `thongbao/[category]/`: Markdown and JSON metadata for each announcement.

*Note: If the scraper encounters Cloudflare protection (403 Forbidden), it will attempt to use `curl_cffi` to bypass it. If that fails, you can generate data from local HTML files (if available) using:*

```bash
uv run python process_local.py
```

### 2. Viewer (Streamlit App)

To view and tag the announcements:

```bash
uv run streamlit run app.py
```

The app will open in your default browser (usually at `http://localhost:8501`).

## Features

-   **Scraper**: Fetches title, date, author, content, and assets (PDFs).
-   **Viewer**:
    -   Sorts announcements by date (newest first).
    -   Filter by tags.
    -   Search by title/content.
    -   View details and download attachments.
    -   **Tagging**: Add or edit tags for any announcement. Tags are saved locally.

## Known Issues

-   **Asset Downloading**: The CITD website uses strict Cloudflare protection which may block automated downloads of attached files (PDF/Doc), resulting in 403 Forbidden errors. The scraper will attempt to download them, but if blocked, the files will not be saved locally. You can still access the files via the links in the generated Markdown content.

## Project Structure

-   `scraper.py`: Main scraping script.
-   `app.py`: Streamlit application.
-   `process_local.py`: Utility to process local HTML files (fallback).
-   `requirements.txt`: Python dependencies.
-   `thongbao/`: Directory where data is saved (JSON, MD, assets).
