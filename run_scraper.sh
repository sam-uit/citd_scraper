#!/bin/bash
# Wrapper script to run the CITD Scraper Service
# Usage: ./run_scraper.sh [args]
# Example: ./run_scraper.sh --pages 1 --headless

uv run python -m services.scraper_service "$@"
