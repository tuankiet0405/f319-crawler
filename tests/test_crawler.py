"""Tests for scraper — input validation and crawl logic with mocked HTTP."""

import pytest
from unittest.mock import patch, MagicMock
import os

from crawler.scraper import validate_user_input, crawl_user

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _load_fixture(name: str) -> str:
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as f:
        return f.read()


class TestValidateUserInput:
    def test_single_valid_user(self):
        result = validate_user_input("ngokha5566.713779")
        assert result == [("ngokha5566", "713779")]

    def test_multiple_users(self):
        result = validate_user_input("ngokha5566.713779, csdn.699927")
        assert len(result) == 2
        assert result[0] == ("ngokha5566", "713779")
        assert result[1] == ("csdn", "699927")

    def test_empty_input(self):
        with pytest.raises(ValueError, match="ít nhất một User ID"):
            validate_user_input("")

    def test_whitespace_only(self):
        with pytest.raises(ValueError, match="ít nhất một User ID"):
            validate_user_input("   ")

    def test_invalid_format_no_dot(self):
        with pytest.raises(ValueError, match="Format không hợp lệ"):
            validate_user_input("invaliduser")

    def test_invalid_format_no_number(self):
        with pytest.raises(ValueError, match="Format không hợp lệ"):
            validate_user_input("user.name")

    def test_trims_whitespace(self):
        result = validate_user_input("  ngokha5566.713779  ")
        assert result == [("ngokha5566", "713779")]

    def test_handles_extra_commas(self):
        result = validate_user_input("a.1,, b.2,")
        assert len(result) == 2


class TestCrawlUser:
    """Integration tests with mocked HTTP responses."""

    @patch("crawler.scraper.time.sleep")
    @patch("crawler.scraper.requests.Session")
    def test_returns_posts_on_success(self, mock_session_cls, mock_sleep):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        html_page1 = _load_fixture("search_results.html")
        html_empty = _load_fixture("empty_results.html")

        resp1 = MagicMock()
        resp1.text = html_page1
        resp1.status_code = 200

        resp2 = MagicMock()
        resp2.text = html_empty
        resp2.status_code = 200

        # First call returns results with next link, second returns empty
        mock_session.get.side_effect = [resp1, resp2]

        posts = crawl_user("ngokha5566", "713779", full_content_limit=-1)

        assert len(posts) == 3
        assert posts[0]["title"] == "DGC con hào kinh tế"

    @patch("crawler.scraper.time.sleep")
    @patch("crawler.scraper.requests.Session")
    def test_returns_empty_for_no_results(self, mock_session_cls, mock_sleep):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        html = _load_fixture("empty_results.html")
        mock_response = MagicMock()
        mock_response.text = html
        mock_response.status_code = 200
        mock_session.get.return_value = mock_response

        posts = crawl_user("nobody", "000000", full_content_limit=-1)
        assert posts == []

    @patch("crawler.scraper.time.sleep")
    @patch("crawler.scraper.requests.Session")
    def test_content_type_is_snippet_when_no_full(self, mock_session_cls, mock_sleep):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        html_page1 = _load_fixture("search_results.html")
        html_empty = _load_fixture("empty_results.html")

        resp1 = MagicMock()
        resp1.text = html_page1
        resp1.status_code = 200

        resp2 = MagicMock()
        resp2.text = html_empty
        resp2.status_code = 200

        mock_session.get.side_effect = [resp1, resp2]

        posts = crawl_user("ngokha5566", "713779", full_content_limit=-1)
        for p in posts:
            assert p["content_type"] == "snippet"
