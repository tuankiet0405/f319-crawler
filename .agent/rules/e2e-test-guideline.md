---
trigger: model_decision
description: Use this rule when writing and running tests for the crawler
---

# Testing Guidelines

## Tech Stack

| Layer | Tool |
|-------|------|
| Test framework | **pytest** |
| HTTP mocking | **responses** or **requests-mock** |
| Pattern | Unit tests for parsing/export, integration tests for scraping |

### Running tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_crawler.py -v

# Run with coverage
pytest tests/ --cov=crawler --cov-report=html
```

## Test Output

```
tests/
├── test_crawler.py      # Integration tests for scraping flow
├── test_parser.py       # Unit tests for HTML parsing
├── test_exporter.py     # Unit tests for CSV export
├── fixtures/            # Sample HTML files for testing
│   ├── search_results.html
│   ├── post_content.html
│   └── empty_results.html
└── output/              # Test output (gitignored)
```

## Testing Rules

1. **Mock all HTTP requests** — never hit f319.com in tests
2. **Use fixture HTML files** — save sample pages as test data
3. **Test edge cases** — empty results, malformed HTML, timeout
4. **Test CSV encoding** — verify UTF-8 BOM and Vietnamese characters
5. **Test input validation** — invalid user IDs, empty input
