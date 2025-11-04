#!/usr/bin/env python3
"""
AI News Scraper - Main orchestration script.

This script:
1. Scrapes AI news from configured sources (RSS and web)
2. Filters out previously seen entries
3. Sends new updates to Slack
4. Updates state file to track seen entries
"""

import os
import sys
from typing import List

from src.state_manager import StateManager
from src.scrapers.rss_scraper import RSSFeedScraper
from src.scrapers.web_scraper import WebScraper
from src.slack_notifier import SlackNotifier
from config import ALL_SOURCES


def main():
    """Main execution function."""
    print("=" * 60)
    print("AI News Scraper Starting")
    print("=" * 60)

    # Get Slack webhook URL from environment
    slack_webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("ERROR: SLACK_WEBHOOK_URL environment variable not set")
        print("Please set this in your GitHub repository secrets")
        sys.exit(1)

    # Initialize components
    state_manager = StateManager()
    rss_scraper = RSSFeedScraper()
    web_scraper = WebScraper()
    slack_notifier = SlackNotifier(slack_webhook_url)

    all_new_entries = []

    # Scrape RSS sources
    print("\n" + "=" * 60)
    print("Scraping RSS feeds...")
    print("=" * 60)
    try:
        rss_entries = rss_scraper.scrape_sources(ALL_SOURCES, state_manager)
        all_new_entries.extend(rss_entries)
        print(f"\n✓ RSS scraping complete: {len(rss_entries)} new entries")
    except Exception as e:
        print(f"\n✗ Error during RSS scraping: {e}")
        # Continue with web scraping even if RSS fails

    # Scrape web sources
    print("\n" + "=" * 60)
    print("Scraping web sources...")
    print("=" * 60)
    try:
        web_articles = web_scraper.scrape_sources(ALL_SOURCES, state_manager)
        all_new_entries.extend(web_articles)
        print(f"\n✓ Web scraping complete: {len(web_articles)} new articles")
    except Exception as e:
        print(f"\n✗ Error during web scraping: {e}")
        # Continue even if web scraping fails

    # Save state
    print("\n" + "=" * 60)
    print("Saving state...")
    print("=" * 60)
    try:
        state_manager.cleanup_old_entries(max_entries_per_source=200)
        state_manager.save_state()
        print("✓ State saved successfully")
    except Exception as e:
        print(f"✗ Error saving state: {e}")

    # Send updates to Slack
    print("\n" + "=" * 60)
    print("Sending updates to Slack...")
    print("=" * 60)
    if all_new_entries:
        print(f"Total new entries to send: {len(all_new_entries)}")
        try:
            success = slack_notifier.send_updates(all_new_entries)
            if success:
                print("✓ Updates sent to Slack successfully")
            else:
                print("✗ Failed to send updates to Slack")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Error sending to Slack: {e}")
            # Try to send error notification
            try:
                slack_notifier.send_error_notification(str(e))
            except:
                pass
            sys.exit(1)
    else:
        print("No new entries found - skipping Slack notification")

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"RSS entries: {len([e for e in all_new_entries if hasattr(e, '__class__') and e.__class__.__name__ == 'RSSEntry'])}")
    print(f"Web articles: {len([e for e in all_new_entries if hasattr(e, '__class__') and e.__class__.__name__ == 'WebArticle'])}")
    print(f"Total new entries: {len(all_new_entries)}")
    print("\n✓ AI News Scraper finished successfully")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
