"""
SQLite Event Logger
Stores detections, violations, crowd stats, and alerts for historical analysis.
"""
import sqlite3
import json
import time
import os
from typing import List, Dict, Any


class EventLogger:
    """SQLite-based event logging for the AI Visual Intelligence System."""

    def __init__(self, db_path: str = None):
        if db_path is None:
            from config import DB_PATH
            db_path = DB_PATH

        # Ensure data directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                event_type TEXT NOT NULL,
                details_json TEXT,
                frame_number INTEGER DEFAULT 0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crowd_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                count INTEGER NOT NULL,
                density_level TEXT NOT NULL,
                density_value REAL DEFAULT 0.0
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                violation_type TEXT NOT NULL,
                track_id INTEGER,
                details_json TEXT
            )
        """)

        self.conn.commit()

    def log_event(self, event_type: str, details: Dict[str, Any], frame_number: int = 0):
        """Log a general event."""
        self.conn.execute(
            "INSERT INTO events (timestamp, event_type, details_json, frame_number) VALUES (?, ?, ?, ?)",
            (time.time(), event_type, json.dumps(details), frame_number),
        )
        self.conn.commit()

    def log_crowd_stats(self, count: int, density_level: str, density_value: float = 0.0):
        """Log crowd statistics."""
        self.conn.execute(
            "INSERT INTO crowd_stats (timestamp, count, density_level, density_value) VALUES (?, ?, ?, ?)",
            (time.time(), count, density_level, density_value),
        )
        self.conn.commit()

    def log_violation(self, violation_type: str, track_id: int, details: str):
        """Log a traffic or safety violation."""
        self.conn.execute(
            "INSERT INTO violations (timestamp, violation_type, track_id, details_json) VALUES (?, ?, ?, ?)",
            (time.time(), violation_type, track_id, json.dumps({"details": details})),
        )
        self.conn.commit()

    def get_recent_events(self, n: int = 20) -> List[Dict]:
        """Get the N most recent events."""
        cursor = self.conn.execute(
            "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (n,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_recent_violations(self, n: int = 20) -> List[Dict]:
        """Get the N most recent violations."""
        cursor = self.conn.execute(
            "SELECT * FROM violations ORDER BY timestamp DESC LIMIT ?", (n,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_recent_crowd_stats(self, n: int = 20) -> List[Dict]:
        """Get the N most recent crowd stats."""
        cursor = self.conn.execute(
            "SELECT * FROM crowd_stats ORDER BY timestamp DESC LIMIT ?", (n,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_event_count(self) -> int:
        """Total number of events logged."""
        cursor = self.conn.execute("SELECT COUNT(*) FROM events")
        return cursor.fetchone()[0]

    def close(self):
        """Close the database connection."""
        self.conn.close()
