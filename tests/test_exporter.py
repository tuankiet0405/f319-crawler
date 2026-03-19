"""Tests for CSV exporter."""

import csv
import os
import tempfile
import pytest

from crawler.exporter import export_to_csv, generate_filename, generate_combined_filename

# Override OUTPUT_DIR for tests
import crawler.exporter as exporter_module


class TestExportCsv:
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self._original_output_dir = exporter_module.OUTPUT_DIR
        exporter_module.OUTPUT_DIR = self.temp_dir

    def teardown_method(self):
        exporter_module.OUTPUT_DIR = self._original_output_dir

    def test_creates_csv_file(self):
        posts = [{"title": "Test", "content": "Hello", "date": "2024-01-01",
                   "forum": "F", "post_url": "http://x", "content_type": "snippet"}]
        path = export_to_csv(posts, "test.csv")
        assert os.path.exists(path)

    def test_csv_has_utf8_bom(self):
        posts = [{"title": "Tiếng Việt", "content": "Xin chào", "date": "2024-01-01",
                   "forum": "F", "post_url": "http://x", "content_type": "full"}]
        path = export_to_csv(posts, "viet.csv")
        with open(path, "rb") as f:
            bom = f.read(3)
        assert bom == b"\xef\xbb\xbf"  # UTF-8 BOM

    def test_csv_has_headers(self):
        posts = [{"title": "T", "content": "C", "date": "D",
                   "forum": "F", "post_url": "U", "content_type": "snippet"}]
        path = export_to_csv(posts, "headers.csv")
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            assert "title" in reader.fieldnames
            assert "content" in reader.fieldnames
            assert "stt" in reader.fieldnames

    def test_csv_row_count(self):
        posts = [
            {"title": f"Post {i}", "content": f"Content {i}", "date": "D",
             "forum": "F", "post_url": "U", "content_type": "snippet"}
            for i in range(5)
        ]
        path = export_to_csv(posts, "count.csv")
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) == 6  # header + 5 data rows

    def test_stt_auto_numbered(self):
        posts = [{"title": "A", "content": "B", "date": "D",
                   "forum": "F", "post_url": "U", "content_type": "snippet"}]
        path = export_to_csv(posts, "stt.csv")
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            row = next(reader)
        assert row["stt"] == "1"

    def test_vietnamese_content_preserved(self):
        posts = [{"title": "Cổ phiếu", "content": "Thị trường chứng khoán Việt Nam",
                   "date": "19/03/2026", "forum": "TTCK", "post_url": "http://x",
                   "content_type": "full"}]
        path = export_to_csv(posts, "viet_content.csv")
        with open(path, encoding="utf-8-sig") as f:
            content = f.read()
        assert "Thị trường chứng khoán Việt Nam" in content

    def test_empty_posts(self):
        path = export_to_csv([], "empty.csv")
        assert os.path.exists(path)
        with open(path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) == 1  # header only


class TestGenerateFilename:
    def test_basic_format(self):
        assert generate_filename("ngokha5566", "713779") == "ngokha5566_713779_posts.csv"

    def test_sanitizes_spaces(self):
        assert "some_user" in generate_filename("some user", "123")

    def test_combined_filename(self):
        assert generate_combined_filename() == "combined_posts.csv"
