"""Migrate change_requests table to add new columns for semantic requests."""
from __future__ import annotations

import sqlite3


def migrate_change_requests(conn: sqlite3.Connection) -> None:
    """Add new columns to change_requests if they don't exist. Safe to re-run."""
    cursor = conn.execute("PRAGMA table_info(change_requests)")
    existing = {row[1] for row in cursor.fetchall()}

    migrations = [
        ("urgency", "TEXT NOT NULL DEFAULT 'normal'"),
        ("preferred_alternative", "TEXT NOT NULL DEFAULT ''"),
        ("coordinator_note", "TEXT NOT NULL DEFAULT ''"),
        ("admin_response", "TEXT NOT NULL DEFAULT ''"),
    ]

    for col_name, col_def in migrations:
        if col_name not in existing:
            conn.execute(f"ALTER TABLE change_requests ADD COLUMN {col_name} {col_def}")

    # Fix status: rename 'open' → 'pending' for consistency
    conn.execute("UPDATE change_requests SET status = 'pending' WHERE status = 'open'")

    # timetable_entries.reason explains why an unplaced session could not be scheduled.
    entry_cols = {row[1] for row in conn.execute("PRAGMA table_info(timetable_entries)").fetchall()}
    if "reason" not in entry_cols:
        conn.execute("ALTER TABLE timetable_entries ADD COLUMN reason TEXT NOT NULL DEFAULT ''")

    conn.commit()
