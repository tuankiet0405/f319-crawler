# F319 Crawler Configuration
import os

BASE_URL = "https://f319.com"
SEARCH_URL = f"{BASE_URL}/search/member"
POST_URL = f"{BASE_URL}/posts"

# Crawling settings
REQUEST_TIMEOUT = 8               # seconds per request (fail fast)
FULL_CONTENT_DELAY = 0.3          # seconds between full-content requests
MAX_FULL_CONTENT_POSTS = 10       # default: only get full content for top 10 posts (0=all, -1=none)
SKIP_LONG_POSTS = True            # skip posts longer than threshold
LONG_POST_THRESHOLD = 5000        # characters

# Request headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
}

# Output
OUTPUT_DIR = "output"
LOG_FILE = "enhanced_crawler.log"

# Flask
HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))
DEBUG = os.environ.get("DEBUG", "true").lower() == "true"
