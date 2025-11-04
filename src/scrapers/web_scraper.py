"""
Web scraper for AI news sources without RSS feeds.
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from typing import List, Dict, Optional
from dateutil import parser as date_parser
from urllib.parse import urljoin

from config import USER_AGENT, REQUEST_TIMEOUT, REQUEST_DELAY


class WebArticle:
    """Represents a single article scraped from a website."""

    def __init__(self, title: str, link: str, description: str, published: Optional[datetime], source: str):
        """
        Initialize web article.

        Args:
            title: Article title
            link: Article URL
            description: Article description/excerpt
            published: Publication date (may be None)
            source: Source name
        """
        self.title = title.strip()
        self.link = link.strip()
        self.description = description.strip()
        self.published = published
        self.source = source

    def to_dict(self) -> Dict:
        """Convert article to dictionary format."""
        return {
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "published": self.published.isoformat() if self.published else None,
            "source": self.source
        }

    def get_id(self) -> str:
        """Get unique identifier for this article (uses URL)."""
        return self.link


class WebScraper:
    """Scrapes websites for AI news articles."""

    def __init__(self):
        """Initialize web scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def scrape_page(self, url: str, source_name: str, selectors: Dict) -> List[WebArticle]:
        """
        Scrape a single web page for articles.

        Args:
            url: Page URL
            source_name: Name of the source
            selectors: Dictionary of CSS selectors for finding elements

        Returns:
            List of WebArticle objects
        """
        articles = []

        try:
            print(f"Fetching web page: {url}")

            # Fetch page
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find article elements
            article_selector = selectors.get('article', 'article')
            article_elements = soup.select(article_selector)

            if not article_elements:
                print(f"  Warning: No articles found with selector '{article_selector}'")
                return articles

            print(f"  Found {len(article_elements)} article elements")

            # Parse each article
            for article_elem in article_elements[:20]:  # Limit to first 20 to avoid spam
                try:
                    # Extract title
                    title = self._extract_text(article_elem, selectors.get('title', 'h2, h3'))
                    if not title:
                        continue

                    # Extract link
                    link = self._extract_link(article_elem, selectors.get('link', 'a'), url)
                    if not link:
                        continue

                    # Extract description
                    description = self._extract_text(article_elem, selectors.get('description', 'p'))
                    if description and len(description) > 300:
                        description = description[:297] + "..."

                    # Extract date
                    published = self._extract_date(article_elem, selectors.get('date', 'time'))

                    # Create article object
                    article = WebArticle(
                        title=title,
                        link=link,
                        description=description or "No description available",
                        published=published,
                        source=source_name
                    )
                    articles.append(article)

                except Exception as e:
                    print(f"  Warning: Error parsing article element: {e}")
                    continue

            print(f"  Successfully parsed {len(articles)} articles")

        except requests.RequestException as e:
            print(f"  Error fetching web page {url}: {e}")
        except Exception as e:
            print(f"  Error parsing web page {url}: {e}")

        # Be respectful - add delay between requests
        time.sleep(REQUEST_DELAY)

        return articles

    def _extract_text(self, element, selector: str) -> str:
        """
        Extract text from element using CSS selector.

        Args:
            element: BeautifulSoup element to search within
            selector: CSS selector string (can be comma-separated)

        Returns:
            Extracted text or empty string
        """
        try:
            # Try each selector in the comma-separated list
            for sel in selector.split(','):
                sel = sel.strip()
                found = element.select_one(sel)
                if found:
                    text = found.get_text(strip=True)
                    if text:
                        return text
        except Exception as e:
            print(f"  Warning: Error extracting text with selector '{selector}': {e}")

        return ""

    def _extract_link(self, element, selector: str, base_url: str) -> str:
        """
        Extract link from element using CSS selector.

        Args:
            element: BeautifulSoup element to search within
            selector: CSS selector for link element
            base_url: Base URL for resolving relative links

        Returns:
            Absolute URL or empty string
        """
        try:
            # Try each selector in the comma-separated list
            for sel in selector.split(','):
                sel = sel.strip()
                found = element.select_one(sel)
                if found and found.get('href'):
                    href = found.get('href')
                    # Convert relative URLs to absolute
                    return urljoin(base_url, href)
        except Exception as e:
            print(f"  Warning: Error extracting link with selector '{selector}': {e}")

        return ""

    def _extract_date(self, element, selector: str) -> Optional[datetime]:
        """
        Extract date from element using CSS selector.

        Args:
            element: BeautifulSoup element to search within
            selector: CSS selector for date element

        Returns:
            Parsed datetime or None
        """
        try:
            # Try each selector in the comma-separated list
            for sel in selector.split(','):
                sel = sel.strip()
                found = element.select_one(sel)
                if found:
                    # Try datetime attribute first
                    if found.get('datetime'):
                        try:
                            return date_parser.parse(found.get('datetime'))
                        except:
                            pass

                    # Try text content
                    date_text = found.get_text(strip=True)
                    if date_text:
                        try:
                            return date_parser.parse(date_text)
                        except:
                            pass
        except Exception as e:
            print(f"  Warning: Error extracting date with selector '{selector}': {e}")

        return None

    def scrape_sources(self, sources: Dict, state_manager) -> List[WebArticle]:
        """
        Scrape multiple web sources.

        Args:
            sources: Dictionary of source configurations
            state_manager: State manager instance for tracking seen entries

        Returns:
            List of new articles
        """
        all_new_articles = []

        for source_id, source_config in sources.items():
            if source_config.get("type") != "web":
                continue

            source_name = source_config["name"]
            selectors = source_config.get("selectors", {})

            for url in source_config["urls"]:
                # Scrape page
                articles = self.scrape_page(url, source_name, selectors)

                # Filter out seen articles
                new_articles = []
                for article in articles:
                    article_id = article.get_id()
                    if not state_manager.is_seen(source_id, article_id):
                        new_articles.append(article)
                        state_manager.mark_seen(source_id, article_id)

                if new_articles:
                    print(f"  {len(new_articles)} new articles from {source_name}")
                    all_new_articles.extend(new_articles)

        return all_new_articles
