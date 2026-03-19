"""Core scraper for f319.com — search-based post extraction."""

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from config import (
    BASE_URL,
    FULL_CONTENT_DELAY,
    HEADERS,
    LONG_POST_THRESHOLD,
    MAX_FULL_CONTENT_POSTS,
    POST_URL,
    REQUEST_TIMEOUT,
    SEARCH_URL,
    SKIP_LONG_POSTS,
)
from crawler.parser import parse_pagination, parse_post_content, parse_search_results

logger = logging.getLogger(__name__)


def validate_user_input(user_input: str) -> list[tuple[str, str]]:
    """Validate and parse user input into list of (username, userid) tuples.

    Accepts formats: 'username.userid' or 'username.userid, username2.userid2'
    
    Raises ValueError for invalid format.
    """
    users = []
    parts = [p.strip() for p in user_input.split(",") if p.strip()]

    if not parts:
        raise ValueError("Vui lòng nhập ít nhất một User ID")

    for part in parts:
        match = re.match(r"^([a-zA-Z0-9_]+)\.(\d+)$", part)
        if not match:
            raise ValueError(
                f"Format không hợp lệ: '{part}'. "
                "Vui lòng nhập theo format: username.userid (vd: ngokha5566.713779)"
            )
        users.append((match.group(1), match.group(2)))

    return users


def crawl_user(
    username: str,
    userid: str,
    full_content_limit: int | None = None,
    max_posts: int = 0,
    progress_callback=None,
) -> list[dict]:
    """Crawl all posts for a single user.

    Args:
        username: Forum username
        userid: Numeric user ID
        full_content_limit: Override MAX_FULL_CONTENT_POSTS. None=use config.
        max_posts: Max total posts to crawl. 0=all.
        progress_callback: Optional callable(message: str) for progress updates.

    Returns:
        List of post dicts.
    """
    if full_content_limit is None:
        full_content_limit = MAX_FULL_CONTENT_POSTS

    session = requests.Session()
    session.headers.update(HEADERS)

    def _progress(msg: str):
        logger.info(msg)
        if progress_callback:
            progress_callback(msg)

    # Step 1: Search for user posts
    _progress(f"Đang tìm bài viết của {username}...")
    all_posts = _fetch_all_search_pages(session, userid, _progress, max_posts=max_posts)

    if not all_posts:
        _progress(f"Không tìm thấy bài viết nào cho {username}")
        return []

    _progress(f"Tìm thấy {len(all_posts)} bài viết cho {username}")

    # Step 2: Fetch full content for top N posts
    if full_content_limit == -1:
        _progress("Bỏ qua full content (snippet only)")
    elif full_content_limit == 0:
        _fetch_full_contents(session, all_posts, len(all_posts), _progress)
    else:
        _fetch_full_contents(session, all_posts, full_content_limit, _progress)

    # Set content field
    for post in all_posts:
        post["content"] = post.get("full_content") or post.get("snippet", "")
        post["content_type"] = "full" if post.get("full_content") else "snippet"

    _progress(f"Hoàn tất crawl {username}: {len(all_posts)} bài viết")
    return all_posts


def _fetch_all_search_pages(
    session: requests.Session, userid: str, progress, max_posts: int = 0
) -> list[dict]:
    """Fetch all pages of search results for a user."""
    all_posts = []
    url = f"{SEARCH_URL}?user_id={userid}"
    page = 1

    while url:
        try:
            progress(f"  Đang lấy trang {page}...")
            response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Lỗi kết nối trang {page}: {e}")
            progress(f"  Lỗi kết nối trang {page}: {e}")
            break

        posts = parse_search_results(response.text)
        all_posts.extend(posts)

        # Stop if we have enough posts
        if max_posts > 0 and len(all_posts) >= max_posts:
            all_posts = all_posts[:max_posts]
            progress(f"  Đạt giới hạn {max_posts} bài, dừng phân trang.")
            break

        pagination = parse_pagination(response.text)
        url = pagination.get("next_url")
        page += 1

        if url:
            time.sleep(0.1)  # minimal delay between search pages

    return all_posts


def _fetch_full_contents(
    session: requests.Session,
    posts: list[dict],
    limit: int,
    progress,
):
    """Fetch full content for the first `limit` posts using parallel threads."""
    to_fetch = posts[:limit]
    progress(f"  Đang lấy full content cho {len(to_fetch)}/{len(posts)} bài viết...")

    completed = [0]  # mutable counter for thread-safe incrementing

    def _fetch_one(post):
        post_id = post.get("post_id")
        if not post_id:
            return

        try:
            url = f"{POST_URL}/{post_id}/"
            response = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            response.raise_for_status()

            content = parse_post_content(response.text)

            if SKIP_LONG_POSTS and len(content) > LONG_POST_THRESHOLD:
                logger.info(
                    f"Skipped post {post_id} - content too long ({len(content)} chars)"
                )
                return

            if content:
                post["full_content"] = content

        except requests.RequestException as e:
            logger.warning(f"Lỗi lấy bài #{post_id}: {e}")

        time.sleep(FULL_CONTENT_DELAY)  # rate limit per request

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(_fetch_one, post): post for post in to_fetch}
        for future in as_completed(futures):
            completed[0] += 1
            progress(f"  [{completed[0]}/{len(to_fetch)}] Full content...")
            future.result()  # propagate exceptions if any

