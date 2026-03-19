"""HTML parser for f319.com pages using BeautifulSoup."""

import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from config import BASE_URL


def parse_search_results(html: str) -> list[dict]:
    """Parse search results page and extract post entries.
    
    Returns list of dicts with keys: title, snippet, author, date, forum, post_url, post_id
    """
    soup = BeautifulSoup(html, "lxml")
    posts = []
    
    # Each search result is an <li> with class "searchResult"
    results = soup.select("li.searchResult")
    
    for item in results:
        try:
            # Title and link
            title_el = item.select_one("h3.title a")
            if not title_el:
                continue
            
            title = title_el.get_text(strip=True)
            post_url = urljoin(BASE_URL, title_el.get("href", ""))
            
            # Extract post ID from URL
            post_id = _extract_post_id(post_url)
            
            # Content snippet
            snippet_el = item.select_one(".contentRow-snippet")
            if not snippet_el:
                snippet_el = item.select_one("blockquote")
            snippet = snippet_el.get_text(strip=True) if snippet_el else ""
            
            # Meta info (author, date, forum)
            meta_el = item.select_one(".contentRow-minor") or item.select_one(".meta")
            meta_text = meta_el.get_text(" ", strip=True) if meta_el else ""
            
            author = _extract_author(meta_text)
            date = _extract_date(meta_text)
            forum = _extract_forum(meta_text)
            
            posts.append({
                "title": title,
                "snippet": snippet,
                "author": author,
                "date": date,
                "forum": forum,
                "post_url": post_url,
                "post_id": post_id,
            })
        except Exception:
            continue
    
    return posts


def parse_pagination(html: str) -> dict:
    """Parse pagination info from search results.
    
    Returns dict with: current_page, total_pages, next_url
    """
    soup = BeautifulSoup(html, "lxml")
    
    result = {"current_page": 1, "total_pages": 1, "next_url": None}
    
    # Look for page nav: "Trang 1/5"
    page_nav = soup.select_one("nav.pageNavWrapper")
    if not page_nav:
        # Try alternative: look for page links
        page_links = soup.select(".PageNav a.text")
        if not page_links:
            page_links = soup.select(".pageNav-page")
        
        if page_links:
            # Get total from last page link
            last_link = page_links[-1]
            try:
                result["total_pages"] = int(last_link.get_text(strip=True))
            except ValueError:
                pass
    
    # Try "Trang X/Y" pattern
    page_text = soup.find(string=re.compile(r"Trang\s+\d+/\d+"))
    if page_text:
        match = re.search(r"Trang\s+(\d+)/(\d+)", page_text)
        if match:
            result["current_page"] = int(match.group(1))
            result["total_pages"] = int(match.group(2))
    
    # Find "next" link
    next_link = soup.select_one("a.pageNav-jump--next")
    if not next_link:
        # Try finding by text
        for link in soup.select("a"):
            text = link.get_text(strip=True)
            if text in ("Tiếp >", "Tiếp", ">", "›"):
                next_link = link
                break
    
    if next_link and next_link.get("href"):
        result["next_url"] = urljoin(BASE_URL, next_link["href"])
    
    return result


def parse_post_content(html: str) -> str:
    """Parse full post content from a post page.
    
    Returns the text content of the post.
    """
    soup = BeautifulSoup(html, "lxml")
    
    # Primary selector
    content = soup.select_one(".messageText.SelectQuoteContainer.ugc.baseHtml")
    
    if not content:
        # Fallback selectors
        content = soup.select_one("article .bbWrapper")
        if not content:
            content = soup.select_one(".message-body .bbWrapper")
        if not content:
            content = soup.select_one("blockquote.messageText")
    
    if content:
        # Remove quoted text to get only the user's own content
        for quote in content.select("div.bbCodeBlock--quote, .quoteContainer"):
            quote.decompose()
        
        return content.get_text(strip=True)
    
    return ""


def _extract_post_id(url: str) -> str:
    """Extract post ID from URL like /posts/48099891/ or #post-48099891."""
    match = re.search(r"posts/(\d+)", url)
    if match:
        return match.group(1)
    match = re.search(r"#post-(\d+)", url)
    if match:
        return match.group(1)
    return ""


def _extract_author(meta_text: str) -> str:
    """Extract author from meta text like 'Đăng bởi: ngokha5566, ...'."""
    match = re.search(r"Đăng bởi:\s*(\S+)", meta_text)
    if match:
        return match.group(1).rstrip(",")
    return ""


def _extract_date(meta_text: str) -> str:
    """Extract date from meta text."""
    # Match absolute dates: 19/03/2026
    match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", meta_text)
    if match:
        return match.group(0)
    
    # Match relative: "Hôm nay, lúc 19:10" or "52 phút trước"
    match = re.search(r"(Hôm (?:nay|qua)[^,]*,\s*(?:lúc\s*)?\d{1,2}:\d{2}|\d+\s*(?:phút|giờ|giây)\s*trước|Thứ\s+\w+[^,]*,\s*lúc\s*\d{1,2}:\d{2})", meta_text)
    if match:
        return match.group(0)
    
    return ""


def _extract_forum(meta_text: str) -> str:
    """Extract forum name from meta text like '... trong diễn đàn: Thị trường chứng khoán'."""
    match = re.search(r"(?:trong )?diễn đàn:\s*(.+?)(?:\s*$)", meta_text)
    if match:
        return match.group(1).strip()
    return ""
