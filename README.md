# CITD Scraper & Viewer

This project provides a web scraper for CITD announcements and a Streamlit application to view and tag them locally.

## Setup

1.  **Install dependencies**:
    ```bash
    pip3 install -r requirements.txt
    ```

## Usage

### 1. Scraper

To scrape the latest announcements from the CITD website:

```bash
python3 scraper.py
```

*Note: If the scraper encounters Cloudflare protection (403 Forbidden), it will attempt to use `curl_cffi` to bypass it. If that fails, you can generate data from local HTML files (if available) using:*

```bash
python3 process_local.py
```

### 2. Viewer (Streamlit App)

To view and tag the announcements:

```bash
streamlit run app.py
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

## Project Structure

-   `scraper.py`: Main scraping script.
-   `app.py`: Streamlit application.
-   `process_local.py`: Utility to process local HTML files (fallback).
-   `requirements.txt`: Python dependencies.
-   `thongbao/`: Directory where data is saved (JSON, MD, assets).
