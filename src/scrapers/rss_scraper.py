"""
RSS feed scraper for AI news sources.
"""

import feedparser
import time
from datetime import datetime
from typing import List, Dict, Optional
from dateutil import parser as date_parser
import requests

from config import USER_AGENT, REQUEST_TIMEOUT, REQUEST_DELAY


class RSSEntry:
    """Represents a single RSS feed entry."""

    def __init__(self, title: str, link: str, description: str, published: Optional[datetime], source: str):
        """
        Initialize RSS entry.

        Args:
            title: Entry title
            link: Entry URL
            description: Entry description/summary
            published: Publication date
            source: Source name
        """
        self.title = title.strip()
        self.link = link.strip()
        self.description = description.strip()
        self.published = published
        self.source = source

    def to_dict(self) -> Dict:
        """Convert entry to dictionary format."""
        return {
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "published": self.published.isoformat() if self.published else None,
            "source": self.source
        }

    def get_id(self) -> str:
        """
        Get unique identifier for this entry.
        Uses link as primary ID, falls back to title+source hash.
        """
        return self.link


class RSSFeedScraper:
    """Scrapes RSS/Atom feeds for AI news."""

    def __init__(self):
        """Initialize RSS scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })

    def scrape_feed(self, url: str, source_name: str, etag: str = "", last_modified: str = "") -> tuple[List[RSSEntry], str, str]:
        """
        Scrape a single RSS/Atom feed.

        Args:
            url: Feed URL
            source_name: Name of the source
            etag: Optional ETag for conditional GET
            last_modified: Optional Last-Modified for conditional GET

        Returns:
            Tuple of (entries list, new_etag, new_last_modified)
        """
        entries = []
        new_etag = ""
        new_last_modified = ""

        try:
            print(f"Fetching RSS feed: {url}")

            # Parse feed with conditional GET support
            feed = feedparser.parse(
                url,
                etag=etag if etag else None,
                modified=last_modified if last_modified else None,
                agent=USER_AGENT,
                request_headers={
                    'User-Agent': USER_AGENT
                }
            )

            # Check if feed was modified (304 = not modified)
            if hasattr(feed, 'status'):
                if feed.status == 304:
                    print(f"  Feed not modified since last check (304)")
                    return entries, etag, last_modified
                elif feed.status != 200:
                    print(f"  Warning: Feed returned status {feed.status}")

            # Store new ETag and Last-Modified if available
            if hasattr(feed, 'etag'):
                new_etag = feed.etag
            if hasattr(feed, 'modified'):
                new_last_modified = feed.modified

            # Parse entries
            for entry in feed.entries:
                try:
                    # Extract title
                    title = entry.get('title', 'No title')

                    # Extract link
                    link = entry.get('link', '')
                    if not link:
                        # Try alternative link fields
                        link = entry.get('id', '')

                    # Extract description
                    description = entry.get('summary', entry.get('description', ''))

                    # Clean HTML tags from description if present
                    if description:
                        description = self._clean_html(description)
                        # Truncate long descriptions
                        if len(description) > 300:
                            description = description[:297] + "..."

                    # Extract published date
                    published = None
                    if 'published_parsed' in entry and entry.published_parsed:
                        published = datetime(*entry.published_parsed[:6])
                    elif 'updated_parsed' in entry and entry.updated_parsed:
                        published = datetime(*entry.updated_parsed[:6])
                    elif 'published' in entry:
                        try:
                            published = date_parser.parse(entry.published)
                        except:
                            pass

                    # Create entry object
                    rss_entry = RSSEntry(
                        title=title,
                        link=link,
                        description=description,
                        published=published,
                        source=source_name
                    )
                    entries.append(rss_entry)

                except Exception as e:
                    print(f"  Warning: Error parsing entry: {e}")
                    continue

            print(f"  Found {len(entries)} entries")

        except Exception as e:
            print(f"  Error fetching RSS feed {url}: {e}")

        # Be respectful - add delay between requests
        time.sleep(REQUEST_DELAY)

        return entries, new_etag, new_last_modified

    def _clean_html(self, text: str) -> str:
        """
        Remove HTML tags from text.

        Args:
            text: Text potentially containing HTML

        Returns:
            Clean text without HTML tags
        """
        from html.parser import HTMLParser

        class HTMLStripper(HTMLParser):
            def __init__(self):
                super().__init__()
                self.reset()
                self.strict = False
                self.convert_charrefs = True
                self.text = []

            def handle_data(self, d):
                self.text.append(d)

            def get_data(self):
                return ''.join(self.text)

        stripper = HTMLStripper()
        try:
            stripper.feed(text)
            return stripper.get_data().strip()
        except:
            # If HTML parsing fails, return original text
            return text

    def scrape_sources(self, sources: Dict, state_manager) -> List[RSSEntry]:
        """
        Scrape multiple RSS feed sources.

        Args:
            sources: Dictionary of source configurations
            state_manager: State manager instance for tracking seen entries

        Returns:
            List of new RSS entries
        """
        all_new_entries = []

        for source_id, source_config in sources.items():
            if source_config.get("type") != "rss":
                continue

            source_name = source_config["name"]

            for url in source_config["urls"]:
                # Get cached ETag and Last-Modified
                etag = state_manager.get_etag(f"{source_id}_{url}")
                last_modified = state_manager.get_last_modified(f"{source_id}_{url}")

                # Scrape feed
                entries, new_etag, new_last_modified = self.scrape_feed(
                    url, source_name, etag, last_modified
                )

                # Update ETag and Last-Modified in state
                if new_etag:
                    state_manager.set_etag(f"{source_id}_{url}", new_etag)
                if new_last_modified:
                    state_manager.set_last_modified(f"{source_id}_{url}", new_last_modified)

                # Filter out seen entries
                new_entries = []
                for entry in entries:
                    entry_id = entry.get_id()
                    if not state_manager.is_seen(source_id, entry_id):
                        new_entries.append(entry)
                        state_manager.mark_seen(source_id, entry_id)

                if new_entries:
                    print(f"  {len(new_entries)} new entries from {source_name}")
                    all_new_entries.extend(new_entries)

        return all_new_entries
