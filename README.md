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

To scrape the latest announcements (Học vụ & Chung):

```bash
uv run main.py
```

**Options:**

-   `--all`: Scrape **all** pages (deep scrape).
-   `--pages N`: Scrape the first **N** pages.
-   `--pull`: **Force refresh** all announcements (re-scrape even if exists in DB).
-   `--download`: **Download document attachments** (PDF, DOC, ZIP, etc.).
-   `--no-md`: Skip Markdown file generation (JSON only).
-   `--regenerate`: **Regenerate Markdown files** from local JSON data (useful after template updates).
-   `--headless`: Run browser in **headless mode** (no visible UI).

**Examples:**

```bash
# Scrape the first 2 pages of all categories in headless mode
uv run main.py --pages 2 --headless

# Deep scrape everything and download documents
uv run main.py --all --download
```

### 📂 Directory Structure
Scraped data is organized in the `thongbao/` directory:
- `thongbao.json`: Centralized index database.
- `thongbao/[category]/`: Contains JSON data and Markdown files.
- `thongbao/[category]/assets/`: Contains downloaded images and documents.

### 2. Viewer (Streamlit App)

To view and tag the announcements:

```bash
uv run streamlit run app.py
```

The app will open in your default browser (usually at `http://localhost:8501`).

## Features

-   **Robust Scraper**: Uses `DrissionPage` to bypass Cloudflare protection.
-   **Multi-Category Support**: Scrapes both "Thông báo học vụ" and "Thông báo chung".
-   **Local Asset Storage**: Images and documents are saved locally in `thongbao/[category]/assets/`, ensuring portability.
-   **Markdown Generation**: Automatically converts HTML content to clean Markdown with embedded local images.
-   **Streamlit Viewer**:
    -   Sorts announcements by date (newest first).
    -   Filter by **Category** and **Tags**.
    -   Search by title/content.
    -   View details with rendered Markdown and images.
    -   **Tagging**: Add/Edit tags for any announcement (persisted locally).
-   **Centralized Configuration**: All settings managed in `settings/settings.py`.

## Project Structure

-   `main.py`: CLI entry point for the scraper.
-   `app.py`: Streamlit application entry point.
-   `services/scraper_service.py`: Core scraping logic.
-   `settings/settings.py`: Configuration (URLs, directories).
-   `models/ThongBao.py`: Data model.
-   `utils/`: Helper utilities for networking, markdown, etc.
-   `thongbao/`: Data directory.
