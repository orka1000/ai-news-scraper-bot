"""
State manager for tracking scraped entries and preventing duplicates.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Set


class StateManager:
    """Manages state file for tracking seen entries."""

    def __init__(self, state_file: str = "state.json"):
        """
        Initialize state manager.

        Args:
            state_file: Path to the state JSON file
        """
        self.state_file = state_file
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """
        Load state from file or create new state if file doesn't exist.

        Returns:
            State dictionary
        """
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load state file: {e}. Creating new state.")
                return self._create_new_state()
        else:
            return self._create_new_state()

    def _create_new_state(self) -> Dict:
        """
        Create a new empty state structure.

        Returns:
            New state dictionary
        """
        return {
            "last_checked": None,
            "seen_entries": {},
            "etags": {},
            "last_modified": {}
        }

    def save_state(self):
        """Save current state to file."""
        self.state["last_checked"] = datetime.utcnow().isoformat() + "Z"

        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Could not save state file: {e}")

    def is_seen(self, source: str, entry_id: str) -> bool:
        """
        Check if an entry has been seen before.

        Args:
            source: Source identifier (e.g., 'openai', 'anthropic')
            entry_id: Unique entry identifier (URL or entry ID)

        Returns:
            True if entry has been seen, False otherwise
        """
        if source not in self.state["seen_entries"]:
            self.state["seen_entries"][source] = []

        return entry_id in self.state["seen_entries"][source]

    def mark_seen(self, source: str, entry_id: str):
        """
        Mark an entry as seen.

        Args:
            source: Source identifier
            entry_id: Unique entry identifier
        """
        if source not in self.state["seen_entries"]:
            self.state["seen_entries"][source] = []

        if entry_id not in self.state["seen_entries"][source]:
            self.state["seen_entries"][source].append(entry_id)

    def get_seen_entries(self, source: str) -> List[str]:
        """
        Get list of seen entries for a source.

        Args:
            source: Source identifier

        Returns:
            List of seen entry IDs
        """
        return self.state["seen_entries"].get(source, [])

    def get_etag(self, source: str) -> str:
        """
        Get stored ETag for a source (for conditional GET requests).

        Args:
            source: Source identifier

        Returns:
            ETag value or empty string
        """
        return self.state["etags"].get(source, "")

    def set_etag(self, source: str, etag: str):
        """
        Store ETag for a source.

        Args:
            source: Source identifier
            etag: ETag value
        """
        self.state["etags"][source] = etag

    def get_last_modified(self, source: str) -> str:
        """
        Get stored Last-Modified header for a source.

        Args:
            source: Source identifier

        Returns:
            Last-Modified value or empty string
        """
        return self.state["last_modified"].get(source, "")

    def set_last_modified(self, source: str, last_modified: str):
        """
        Store Last-Modified header for a source.

        Args:
            source: Source identifier
            last_modified: Last-Modified value
        """
        self.state["last_modified"][source] = last_modified

    def cleanup_old_entries(self, max_entries_per_source: int = 100):
        """
        Clean up old entries to prevent state file from growing too large.
        Keeps only the most recent entries.

        Args:
            max_entries_per_source: Maximum number of entries to keep per source
        """
        for source in self.state["seen_entries"]:
            entries = self.state["seen_entries"][source]
            if len(entries) > max_entries_per_source:
                # Keep only the most recent entries
                self.state["seen_entries"][source] = entries[-max_entries_per_source:]
