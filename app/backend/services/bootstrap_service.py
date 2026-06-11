from __future__ import annotations

import sqlite3

from ..repositories.master_data import get_master_data
from ..repositories.timetable_repository import get_latest_version, get_published_version, get_reports


def get_bootstrap_payload(conn: sqlite3.Connection) -> dict:
    latest = get_latest_version(conn)
    return {
        "masterData": get_master_data(conn),
        "latestTimetable": latest,
        "publishedTimetable": get_published_version(conn),
        "reports": get_reports(conn, latest["id"] if latest else None),
    }
