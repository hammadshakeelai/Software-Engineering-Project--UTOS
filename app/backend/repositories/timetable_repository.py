from __future__ import annotations

import sqlite3
from datetime import datetime

from ..database import rows_to_dicts


def save_timetable_result(conn: sqlite3.Connection, result: dict) -> int:
    metrics = result["metrics"]
    version_name = f"Generated draft {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    cursor = conn.execute(
        """
        INSERT INTO timetable_versions
            (name, status, score, hard_conflicts, soft_penalty, unplaced_count, distance_to_feasibility)
        VALUES (?, 'draft', ?, ?, ?, ?, ?)
        """,
        (
            version_name,
            metrics["score"],
            metrics["hard_conflicts"],
            metrics["soft_penalty"],
            metrics["unplaced_count"],
            metrics["distance_to_feasibility"],
        ),
    )
    version_id = int(cursor.lastrowid)
    for entry in result["entries"]:
        conn.execute(
            """
            INSERT INTO timetable_entries
                (version_id, course_id, teacher_id, section_id, room_id, timeslot_id, event_uid, locked, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'placed')
            """,
            (
                version_id,
                entry["course_id"],
                entry["teacher_id"],
                entry["section_id"],
                entry["room_id"],
                entry["timeslot_id"],
                entry["event_uid"],
            ),
        )
    for entry in result["unplaced"]:
        conn.execute(
            """
            INSERT INTO timetable_entries
                (version_id, course_id, teacher_id, section_id, room_id, timeslot_id, event_uid, locked, status)
            VALUES (?, ?, ?, ?, NULL, NULL, ?, 0, 'unplaced')
            """,
            (
                version_id,
                entry["course_id"],
                entry["teacher_id"],
                entry["section_id"],
                entry["event_uid"],
            ),
        )
    return version_id


def get_latest_version(conn: sqlite3.Connection) -> dict | None:
    version = conn.execute(
        "SELECT * FROM timetable_versions ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not version:
        return None
    version_dict = dict(version)
    version_id = version_dict["id"]
    version_dict["entries"] = rows_to_dicts(
        conn.execute(
            """
            SELECT
                e.*,
                c.code AS course_code,
                c.title AS course_title,
                t.name AS teacher_name,
                s.name AS section_name,
                s.size AS section_size,
                r.code AS room_code,
                r.building AS room_building,
                r.capacity AS room_capacity,
                ts.day,
                ts.start_time,
                ts.end_time,
                ts.sort_order,
                ts.is_morning,
                ts.is_last_slot
            FROM timetable_entries e
            JOIN courses c ON c.id = e.course_id
            JOIN teachers t ON t.id = e.teacher_id
            JOIN sections s ON s.id = e.section_id
            LEFT JOIN rooms r ON r.id = e.room_id
            LEFT JOIN timeslots ts ON ts.id = e.timeslot_id
            WHERE e.version_id = ?
            ORDER BY COALESCE(ts.sort_order, 999), c.code
            """,
            (version_id,),
        )
    )
    return version_dict


def get_reports(conn: sqlite3.Connection, version_id: int | None = None) -> dict:
    if version_id is None:
        latest = conn.execute("SELECT id FROM timetable_versions ORDER BY id DESC LIMIT 1").fetchone()
        version_id = int(latest["id"]) if latest else None
    if version_id is None:
        return {"room_utilization": [], "teacher_load": []}

    room_utilization = rows_to_dicts(
        conn.execute(
            """
            SELECT
                r.code,
                r.building,
                r.capacity,
                COUNT(e.id) AS used_slots
            FROM rooms r
            LEFT JOIN timetable_entries e
                ON e.room_id = r.id
                AND e.version_id = ?
                AND e.status = 'placed'
            GROUP BY r.id
            ORDER BY used_slots DESC, r.code
            """,
            (version_id,),
        )
    )
    teacher_load = rows_to_dicts(
        conn.execute(
            """
            SELECT
                t.name,
                t.department,
                COUNT(e.id) AS assigned_sessions
            FROM teachers t
            LEFT JOIN timetable_entries e
                ON e.teacher_id = t.id
                AND e.version_id = ?
                AND e.status = 'placed'
            GROUP BY t.id
            ORDER BY assigned_sessions DESC, t.name
            """,
            (version_id,),
        )
    )
    return {"room_utilization": room_utilization, "teacher_load": teacher_load}
