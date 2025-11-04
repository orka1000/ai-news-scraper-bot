"""
Slack notifier for sending AI news updates.
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Union
from collections import defaultdict


class SlackNotifier:
    """Sends formatted messages to Slack via webhook."""

    def __init__(self, webhook_url: str):
        """
        Initialize Slack notifier.

        Args:
            webhook_url: Slack webhook URL
        """
        self.webhook_url = webhook_url

    def send_updates(self, entries: List) -> bool:
        """
        Send AI news updates to Slack.

        Args:
            entries: List of RSSEntry or WebArticle objects

        Returns:
            True if successful, False otherwise
        """
        if not entries:
            print("No new entries to send to Slack")
            return True

        # Sort entries by date (newest first)
        sorted_entries = sorted(
            entries,
            key=lambda x: x.published if x.published else datetime.min,
            reverse=True
        )

        # Group entries by source
        entries_by_source = defaultdict(list)
        for entry in sorted_entries:
            entries_by_source[entry.source].append(entry)

        # Build Slack message
        blocks = self._build_message_blocks(entries_by_source, len(sorted_entries))

        # Send to Slack
        return self._send_to_slack(blocks)

    def _build_message_blocks(self, entries_by_source: Dict, total_count: int) -> List[Dict]:
        """
        Build Slack Block Kit message blocks.

        Args:
            entries_by_source: Dictionary mapping source names to entry lists
            total_count: Total number of entries

        Returns:
            List of Slack block dictionaries
        """
        blocks = []

        # Header
        today = datetime.utcnow().strftime("%B %d, %Y")
        header_text = f"🤖 *AI News Update - {today}*\n_{total_count} new update{'s' if total_count != 1 else ''} found_"

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": header_text
            }
        })

        blocks.append({"type": "divider"})

        # Add entries grouped by source
        for source_name, entries in entries_by_source.items():
            # Source header
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{source_name}* ({len(entries)} update{'s' if len(entries) != 1 else ''})"
                }
            })

            # Add each entry
            for entry in entries:
                entry_text = self._format_entry(entry)
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": entry_text
                    }
                })

            # Divider between sources
            blocks.append({"type": "divider"})

        # Footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "_Updates delivered by AI News Bot_ 🤖"
                }
            ]
        })

        return blocks

    def _format_entry(self, entry) -> str:
        """
        Format a single entry for Slack.

        Args:
            entry: RSSEntry or WebArticle object

        Returns:
            Formatted Markdown string
        """
        # Format date
        date_str = ""
        if entry.published:
            date_str = f" • {entry.published.strftime('%b %d, %Y')}"

        # Build entry text
        text_parts = [
            f"• *<{entry.link}|{entry.title}>*{date_str}"
        ]

        if entry.description:
            # Truncate description if too long
            desc = entry.description
            if len(desc) > 200:
                desc = desc[:197] + "..."
            text_parts.append(f"  _{desc}_")

        return "\n".join(text_parts)

    def _send_to_slack(self, blocks: List[Dict]) -> bool:
        """
        Send message blocks to Slack webhook.

        Args:
            blocks: List of Slack block dictionaries

        Returns:
            True if successful, False otherwise
        """
        # Slack has a limit on message size, so we may need to split
        # For now, we'll send all blocks (up to ~50 blocks is usually safe)
        if len(blocks) > 50:
            print(f"Warning: Message has {len(blocks)} blocks, may exceed Slack limits")
            # Keep header, divider, and footer, truncate middle
            blocks = blocks[:3] + blocks[3:47] + [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "_... and more updates. Check the sources for complete list._"
                    }
                }
            ] + blocks[-2:]

        payload = {
            "blocks": blocks
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()

            print(f"✓ Successfully sent update to Slack")
            return True

        except requests.RequestException as e:
            print(f"✗ Error sending message to Slack: {e}")
            return False

    def send_error_notification(self, error_message: str) -> bool:
        """
        Send error notification to Slack.

        Args:
            error_message: Error message to send

        Returns:
            True if successful, False otherwise
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"⚠️ *AI News Bot Error*\n```{error_message}```"
                }
            }
        ]

        return self._send_to_slack(blocks)
