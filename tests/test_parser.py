"""Tests for HTML parser — all mocked, no HTTP requests."""

import os
import pytest

from crawler.parser import (
    parse_search_results,
    parse_pagination,
    parse_post_content,
    _extract_post_id,
    _extract_author,
    _extract_date,
    _extract_forum,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _load_fixture(name: str) -> str:
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return f.read()


class TestParseSearchResults:
    def test_parses_three_posts(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert len(posts) == 3

    def test_extracts_title(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert posts[0]["title"] == "DGC con hào kinh tế"
        assert posts[1]["title"] == "MSN cổ phiếu về vùng giá đáy nhiều năm"

    def test_extracts_snippet(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert "dgc nó vẫn hoạt động" in posts[0]["snippet"]

    def test_extracts_post_url(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert "/posts/48099891/" in posts[0]["post_url"]

    def test_extracts_post_id(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert posts[0]["post_id"] == "48099891"

    def test_extracts_author(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert posts[0]["author"] == "ngokha5566"

    def test_extracts_relative_date(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert "19:10" in posts[0]["date"]  # "Hôm nay, lúc 19:10"

    def test_extracts_absolute_date(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert posts[2]["date"] == "19/03/2026"

    def test_extracts_forum(self):
        html = _load_fixture("search_results.html")
        posts = parse_search_results(html)
        assert "Thị trường chứng khoán" in posts[0]["forum"]

    def test_empty_results(self):
        html = _load_fixture("empty_results.html")
        posts = parse_search_results(html)
        assert posts == []

    def test_handles_malformed_html(self):
        posts = parse_search_results("<html><body>garbage</body></html>")
        assert posts == []


class TestParsePagination:
    def test_extracts_page_info(self):
        html = _load_fixture("search_results.html")
        info = parse_pagination(html)
        assert info["current_page"] == 1
        assert info["total_pages"] == 3

    def test_extracts_next_url(self):
        html = _load_fixture("search_results.html")
        info = parse_pagination(html)
        assert info["next_url"] is not None
        assert "page=2" in info["next_url"]

    def test_single_page_no_next(self):
        html = _load_fixture("empty_results.html")
        info = parse_pagination(html)
        assert info["next_url"] is None
        assert info["total_pages"] == 1


class TestParsePostContent:
    def test_extracts_content(self):
        html = _load_fixture("post_content.html")
        content = parse_post_content(html)
        assert "nội dung bài viết thực sự" in content

    def test_removes_quoted_text(self):
        html = _load_fixture("post_content.html")
        content = parse_post_content(html)
        assert "Quoted text that should be removed" not in content

    def test_empty_content(self):
        content = parse_post_content("<html><body></body></html>")
        assert content == ""


class TestHelperFunctions:
    def test_extract_post_id_from_url(self):
        assert _extract_post_id("/posts/48099891/") == "48099891"

    def test_extract_post_id_from_anchor(self):
        assert _extract_post_id("/threads/abc.123/#post-48099891") == "48099891"

    def test_extract_post_id_empty(self):
        assert _extract_post_id("/invalid/url") == ""

    def test_extract_author(self):
        assert _extract_author("Đăng bởi: ngokha5566, yesterday") == "ngokha5566"

    def test_extract_author_empty(self):
        assert _extract_author("no author info") == ""

    def test_extract_date_absolute(self):
        assert _extract_date("posted on 19/03/2026") == "19/03/2026"

    def test_extract_date_relative(self):
        result = _extract_date("Hôm nay, lúc 19:10")
        assert "19:10" in result

    def test_extract_forum(self):
        assert _extract_forum("trong diễn đàn: Thị trường chứng khoán") == "Thị trường chứng khoán"
