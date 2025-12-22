"""Website crawler for extracting documentation content."""

import re
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .logging_utils import get_logger


@dataclass
class CrawlResult:
    """Result of crawling a single page."""

    url: str
    title: str
    module: str
    section: str
    html_content: str
    text_content: str
    crawled_at: datetime
    page_type: str
    hierarchy_level: int


class DocumentationCrawler:
    """Crawls documentation websites and extracts content."""

    def __init__(self, config: Dict):
        """Initialize crawler with configuration."""
        self.config = config
        self.logger = get_logger()
        self.base_url = config.get("base_url", "")
        self.request_delay = config.get("request_delay", 0.5)
        self.timeout = config.get("timeout", 10)
        self.max_pages = config.get("max_pages")
        self.user_agent = config.get("user_agent", "RAGCrawler/1.0")
        self.session = self._create_session()
        self._crawled_urls: Set[str] = set()

    def _create_session(self) -> requests.Session:
        """Create HTTP session with headers."""
        session = requests.Session()
        session.headers.update({"User-Agent": self.user_agent})
        return session

    def _should_crawl_url(self, url: str) -> bool:
        """Determine if URL should be crawled."""
        # Skip anchors
        if "#" in url:
            return False
        # Skip already crawled
        if url in self._crawled_urls:
            return False
        # Filter for documentation paths
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Include documentation paths
        include_patterns = ["/docs", "/documentation", "/guide", "/manual"]
        return any(pattern in path for pattern in include_patterns)

    def discover_urls(self) -> List[str]:
        """Discover all documentation URLs using BFS."""
        discovered = set()
        queue = deque([self.base_url])
        discovered.add(self.base_url)

        while queue and (self.max_pages is None or len(discovered) < self.max_pages):
            current_url = queue.popleft()

            try:
                response = self.session.get(current_url, timeout=self.timeout)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")

                # Extract all links
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    absolute_url = urljoin(current_url, href)

                    # Check domain match
                    if urlparse(absolute_url).netloc != urlparse(self.base_url).netloc:
                        continue

                    if absolute_url not in discovered and self._should_crawl_url(absolute_url):
                        discovered.add(absolute_url)
                        queue.append(absolute_url)

                # Respect rate limiting
                time.sleep(self.request_delay)
            except Exception as e:
                self.logger.log_error(f"Error crawling {current_url}: {e}")
                continue

        return sorted(list(discovered))

    def extract_hierarchy_metadata(self, url: str, html: str) -> Dict:
        """Extract metadata from URL and HTML."""
        soup = BeautifulSoup(html, "html.parser")

        # Extract title
        title = None
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text().strip()
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip()
        if not title:
            title = url.split("/")[-1].replace("-", " ").title()

        # Extract module from URL
        path_parts = urlparse(url).path.split("/")
        module = "General"
        for part in path_parts:
            if part.startswith("module-") or part.startswith("lesson-"):
                module = part.replace("-", " ").title()
                break

        # Extract section
        section = "Default"
        h2 = soup.find("h2")
        if h2:
            section = h2.get_text().strip()

        return {
            "url": url,
            "title": title,
            "module": module,
            "section": section,
            "hierarchy_level": len(path_parts),
            "breadcrumbs": path_parts[1:-1],
        }

    def extract_documentation_content(self, html: str) -> str:
        """Extract main documentation content from HTML."""
        soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Find main content
        main_content = None
        for selector in ["main", "article", ".docusaurus_container", ".main-content", ".content"]:
            main_content = soup.select_one(selector)
            if main_content:
                break

        if not main_content:
            main_content = soup.body if soup.body else soup

        # Remove navigation elements
        for element in main_content.find_all(["nav", "aside", "footer", ".sidebar", ".toc"]):
            element.decompose()

        # Get text
        text = main_content.get_text(separator="\n", strip=True)

        # Clean up whitespace
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def crawl_website(self) -> List[CrawlResult]:
        """Crawl website and extract all documentation pages."""
        self.logger.log_operation("crawl_start", {"base_url": self.base_url})

        urls = self.discover_urls()
        results = []

        for idx, url in enumerate(urls):
            try:
                self.logger.log_info(f"Crawling {idx + 1}/{len(urls)}: {url}")

                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                # Extract metadata
                metadata = self.extract_hierarchy_metadata(url, response.text)

                # Extract content
                text_content = self.extract_documentation_content(response.text)

                result = CrawlResult(
                    url=url,
                    title=metadata["title"],
                    module=metadata["module"],
                    section=metadata["section"],
                    html_content=response.text,
                    text_content=text_content,
                    crawled_at=datetime.utcnow(),
                    page_type="documentation",
                    hierarchy_level=metadata["hierarchy_level"],
                )

                results.append(result)
                self._crawled_urls.add(url)
                time.sleep(self.request_delay)

            except Exception as e:
                self.logger.log_error(f"Error processing {url}: {e}")
                continue

        self.logger.log_operation(
            "crawl_complete",
            {"urls_discovered": len(urls), "urls_crawled": len(results)},
        )

        return results
