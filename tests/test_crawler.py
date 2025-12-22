"""Tests for the website crawler."""

import pytest


def test_crawler_initialization():
    """Test crawler initialization with config."""
    from rag_pipeline.crawler import DocumentationCrawler

    config = {
        "base_url": "https://example.com/docs",
        "request_delay": 0.5,
        "timeout": 10,
        "max_pages": 100,
        "user_agent": "TestCrawler/1.0",
    }

    crawler = DocumentationCrawler(config)
    assert crawler.base_url == "https://example.com/docs"
    assert crawler.request_delay == 0.5


def test_url_filtering():
    """Test URL filtering logic."""
    from rag_pipeline.crawler import DocumentationCrawler

    config = {"base_url": "https://example.com/docs", "request_delay": 0}
    crawler = DocumentationCrawler(config)

    # Should include
    assert crawler._should_crawl_url("https://example.com/docs/page1")
    assert crawler._should_crawl_url("https://example.com/documentation/guide")

    # Should exclude
    assert not crawler._should_crawl_url("https://example.com/docs/page1#section")
    assert not crawler._should_crawl_url("https://other-domain.com/docs/page")


@pytest.mark.skip(reason="Requires network access")
def test_url_discovery():
    """Test URL discovery (requires network)."""
    from rag_pipeline.crawler import DocumentationCrawler

    config = {
        "base_url": "https://example.com/docs",
        "request_delay": 1,
        "timeout": 10,
        "max_pages": 5,
    }

    crawler = DocumentationCrawler(config)
    urls = crawler.discover_urls()
    assert len(urls) > 0
