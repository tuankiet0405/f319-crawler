---
name: crawler-dev
description: >
  Python web crawler development knowledge for crawwAI.
  Covers Flask web app, BeautifulSoup/requests scraping, CSV export,
  config management, and error handling patterns.
  Use when working on any crawler task — including scraping logic,
  Flask routes, data parsing, CSV export, and testing.
---

# Crawler Development Skill

## Use this skill when

- Implementing, modifying, or debugging crawler code
- Working with Flask routes, templates, or static files
- Adding or modifying scraping logic (requests + BeautifulSoup)
- Working with CSV export or data transformation
- Writing or updating tests
- Reviewing crawler PRs or understanding project architecture

## Do not use this skill when

- Working exclusively on infrastructure or deployment
- The task has no crawler or web app component

---

## Stack and Runtime

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Web Framework | Flask |
| HTTP Client | requests |
| HTML Parser | BeautifulSoup4 (bs4) |
| CSV | Python csv module (UTF-8 BOM) |
| Config | config.py (plain Python module) |
| Logging | Python logging module |
| Testing | pytest |

## Quick Commands (run from project root)

| Command | Purpose |
|---------|---------|
| `pip install -r requirements.txt` | Install dependencies |
| `python app.py` | Run dev server (localhost:5000) |
| `pytest tests/` | Run all tests |
| `pytest tests/test_crawler.py -v` | Run specific test file |

## Project Structure

```
crawwAI/
├── app.py                  # Flask app entry point + routes
├── config.py               # Configuration constants
├── requirements.txt        # Python dependencies
├── crawler/
│   ├── __init__.py
│   ├── scraper.py          # Core scraping logic (search + parse)
│   ├── parser.py           # HTML parsing (BeautifulSoup)
│   └── exporter.py         # CSV export with UTF-8 BOM
├── templates/
│   └── index.html          # Web interface (Jinja2)
├── static/
│   ├── css/
│   └── js/
├── output/                 # Generated CSV files (gitignored)
├── tests/
│   ├── test_crawler.py
│   ├── test_parser.py
│   └── test_exporter.py
├── docs/
│   └── specs/              # BDD specs
└── .agent/                 # AI agent config
```

## Code Patterns

### Scraping Pattern — requests + BeautifulSoup

```python
import requests
from bs4 import BeautifulSoup

def fetch_page(url: str, timeout: int = 30) -> BeautifulSoup:
    """Fetch and parse a page. Raises on HTTP errors."""
    response = requests.get(url, timeout=timeout, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; CrawwAI/1.0)'
    })
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')
```

### CSV Export Pattern — UTF-8 BOM

```python
import csv
import io

def export_csv(posts: list[dict], filepath: str):
    """Export posts to CSV with UTF-8 BOM for Excel compatibility."""
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['stt', 'title', 'content', 'date', 'forum', 'link'])
        writer.writeheader()
        writer.writerows(posts)
```

### Rate Limiting Pattern

```python
import time
from config import FULL_CONTENT_DELAY

def crawl_with_delay(urls: list[str]):
    """Crawl URLs with delay between requests to avoid blocking."""
    for url in urls:
        result = fetch_page(url)
        yield result
        time.sleep(FULL_CONTENT_DELAY)
```

## f319.com Specific Knowledge

| Endpoint | URL Pattern | Notes |
|----------|-------------|-------|
| User Search | `/search/member?user_id={userid}` | Redirects to `/search/{search_id}/` |
| Pagination | `/search/{search_id}/?page={n}` | ~20 posts per page |
| Full Post | `/posts/{postid}/` | Redirects to thread with anchor |
| Content Selector | `.messageText.SelectQuoteContainer.ugc.baseHtml` | Inside `<article>` tag |

## Important Implementation Notes

- Always use `time.sleep()` between requests (3-5 sec) to avoid IP blocking
- Parse timestamps carefully — f319 uses both relative ("52 phút trước") and absolute ("19/03/2026") formats
- CSV files MUST use `utf-8-sig` encoding (UTF-8 with BOM) for Excel compatibility with Vietnamese characters
- Use `requests.Session()` for connection reuse across multiple requests
- Always set User-Agent header to avoid basic bot detection
- Log all errors to `enhanced_crawler.log` for debugging