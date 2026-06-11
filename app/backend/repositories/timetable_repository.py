from __future__ import annotations

import sqlite3
from datetime import datetime

from ..database import rows_to_dicts


def save_timetable_result(conn: sqlite3.Connection, result: dict, name_prefix: str = "Generated draft") -> int:
    metrics = result["metrics"]
    version_name = f"{name_prefix} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'placed')
            """,
            (
                version_id,
                entry["course_id"],
                entry["teacher_id"],
                entry["section_id"],
                entry["room_id"],
                entry["timeslot_id"],
                entry["event_uid"],
                1 if entry.get("locked") else 0,
            ),
        )
    for entry in result["unplaced"]:
        conn.execute(
            """
            INSERT INTO timetable_entries
                (version_id, course_id, teacher_id, section_id, room_id, timeslot_id, event_uid, locked, status, reason)
            VALUES (?, ?, ?, ?, NULL, NULL, ?, 0, 'unplaced', ?)
            """,
            (
                version_id,
                entry["course_id"],
                entry["teacher_id"],
                entry["section_id"],
                entry["event_uid"],
                entry.get("reason", ""),
            ),
        )
    return version_id


ENTRY_QUERY = """
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
"""


def get_version(conn: sqlite3.Connection, version_id: int) -> dict | None:
    version = conn.execute(
        "SELECT * FROM timetable_versions WHERE id = ?", (version_id,)
    ).fetchone()
    if not version:
        return None
    version_dict = dict(version)
    version_dict["entries"] = rows_to_dicts(conn.execute(ENTRY_QUERY, (version_id,)))
    return version_dict


def get_latest_version(conn: sqlite3.Connection) -> dict | None:
    version = conn.execute(
        "SELECT * FROM timetable_versions ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not version:
        return None
    return get_version(conn, int(version["id"]))


def get_published_version(conn: sqlite3.Connection) -> dict | None:
    version = conn.execute(
        "SELECT id FROM timetable_versions WHERE status = 'published' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if not version:
        return None
    return get_version(conn, int(version["id"]))


def get_versions(conn: sqlite3.Connection) -> list[dict]:
    return rows_to_dicts(
        conn.execute(
            """
            SELECT v.*, COUNT(e.id) AS entry_count
            FROM timetable_versions v
            LEFT JOIN timetable_entries e ON e.version_id = v.id
            GROUP BY v.id
            ORDER BY v.id DESC
            """
        )
    )


def compare_versions(conn: sqlite3.Connection, version_a: int, version_b: int) -> dict | None:
    if not get_version(conn, version_a) or not get_version(conn, version_b):
        return None
    entries_a = {e["event_uid"]: e for e in rows_to_dicts(conn.execute(ENTRY_QUERY, (version_a,)))}
    entries_b = {e["event_uid"]: e for e in rows_to_dicts(conn.execute(ENTRY_QUERY, (version_b,)))}

    added = [entries_b[uid] for uid in entries_b.keys() - entries_a.keys()]
    removed = [entries_a[uid] for uid in entries_a.keys() - entries_b.keys()]
    changed = []
    unchanged = 0
    for uid in entries_a.keys() & entries_b.keys():
        before, after = entries_a[uid], entries_b[uid]
        if (before["room_id"], before["timeslot_id"], before["status"]) != (
            after["room_id"],
            after["timeslot_id"],
            after["status"],
        ):
            changed.append({"event_uid": uid, "before": before, "after": after})
        else:
            unchanged += 1
    return {
        "version_a": version_a,
        "version_b": version_b,
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged_count": unchanged,
        "totals": {"added": len(added), "removed": len(removed), "changed": len(changed)},
    }


def get_reports(conn: sqlite3.Connection, version_id: int | None = None) -> dict:
    if version_id is None:
        latest = conn.execute("SELECT id FROM timetable_versions ORDER BY id DESC LIMIT 1").fetchone()
        version_id = int(latest["id"]) if latest else None
    if version_id is None:
        return {"room_utilization": [], "teacher_load": [], "section_gaps": []}

    total_slots = conn.execute(
        """
        SELECT COUNT(*) FROM timeslots
        WHERE day NOT IN (SELECT day FROM holidays)
        """
    ).fetchone()[0] or 1

    room_utilization = rows_to_dicts(
        conn.execute(
            """
            SELECT
                r.code,
                r.building,
                r.capacity,
                COUNT(e.id) AS used_slots,
                CAST(ROUND(COUNT(e.id) * 100.0 / ?) AS INTEGER) AS utilization_pct,
                COALESCE(MAX(s.size), 0) AS largest_section
            FROM rooms r
            LEFT JOIN timetable_entries e
                ON e.room_id = r.id
                AND e.version_id = ?
                AND e.status = 'placed'
            LEFT JOIN sections s ON s.id = e.section_id
            GROUP BY r.id
            ORDER BY used_slots DESC, r.code
            """,
            (total_slots, version_id),
        )
    )
    for room in room_utilization:
        if room["used_slots"] == 0:
            room["status"] = "free"
        elif room["utilization_pct"] >= 80:
            room["status"] = "peak"
        else:
            room["status"] = "normal"
        room["capacity_warning"] = room["largest_section"] > room["capacity"]

    teacher_load = rows_to_dicts(
        conn.execute(
            """
            SELECT
                t.id,
                t.name,
                t.department,
                t.max_daily_load,
                (SELECT COUNT(*) FROM timetable_entries e
                 WHERE e.teacher_id = t.id AND e.version_id = ? AND e.status = 'placed') AS assigned_sessions,
                COALESCE((
                    SELECT MAX(cnt) FROM (
                        SELECT COUNT(*) AS cnt
                        FROM timetable_entries e2
                        JOIN timeslots ts ON ts.id = e2.timeslot_id
                        WHERE e2.teacher_id = t.id AND e2.version_id = ? AND e2.status = 'placed'
                        GROUP BY ts.day
                    )
                ), 0) AS busiest_day_load
            FROM teachers t
            ORDER BY assigned_sessions DESC, t.name
            """,
            (version_id, version_id),
        )
    )
    for teacher in teacher_load:
        teacher["overloaded"] = teacher["busiest_day_load"] > teacher["max_daily_load"]

    section_gaps = rows_to_dicts(
        conn.execute(
            """
            SELECT
                s.name AS section_name,
                ts.day,
                MAX(ts.sort_order) - MIN(ts.sort_order) + 1 - COUNT(*) AS gap_periods
            FROM timetable_entries e
            JOIN sections s ON s.id = e.section_id
            JOIN timeslots ts ON ts.id = e.timeslot_id
            WHERE e.version_id = ? AND e.status = 'placed'
            GROUP BY s.id, ts.day
            HAVING gap_periods > 0
            ORDER BY s.name, ts.day
            """,
            (version_id,),
        )
    )
    return {
        "room_utilization": room_utilization,
        "teacher_load": teacher_load,
        "section_gaps": section_gaps,
    }


def lock_entry(conn: sqlite3.Connection, entry_id: int) -> bool:
    cursor = conn.execute("UPDATE timetable_entries SET locked = 1 WHERE id = ?", (entry_id,))
    conn.commit()
    return cursor.rowcount > 0


def unlock_entry(conn: sqlite3.Connection, entry_id: int) -> bool:
    cursor = conn.execute("UPDATE timetable_entries SET locked = 0 WHERE id = ?", (entry_id,))
    conn.commit()
    return cursor.rowcount > 0


def publish_version(conn: sqlite3.Connection, version_id: int) -> bool:
    exists = conn.execute(
        "SELECT id FROM timetable_versions WHERE id = ?", (version_id,)
    ).fetchone()
    if not exists:
        return False
    conn.execute(
        "UPDATE timetable_versions SET status = 'archived' WHERE status = 'published' AND id != ?",
        (version_id,),
    )
    conn.execute("UPDATE timetable_versions SET status = 'published' WHERE id = ?", (version_id,))
    conn.commit()
    return True


def insert_change_request(
    conn: sqlite3.Connection,
    requester_id: int,
    target_type: str,
    target_id: int,
    reason: str,
    urgency: str = "normal",
    preferred_alternative: str = "",
) -> int:
    cursor = conn.execute(
        """INSERT INTO change_requests
           (requester_id, target_type, target_id, reason, urgency, preferred_alternative, status)
           VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
        (requester_id, target_type, target_id, reason, urgency, preferred_alternative),
    )
    conn.commit()
    return cursor.lastrowid


def get_change_requests(conn: sqlite3.Connection) -> list:
    return rows_to_dicts(
        conn.execute(
            """
            SELECT cr.*, u.name AS requester_name, u.role AS requester_role
            FROM change_requests cr
            JOIN users u ON u.id = cr.requester_id
            ORDER BY
                CASE cr.urgency WHEN 'urgent' THEN 0 ELSE 1 END,
                cr.created_at DESC
            """
        )
    )


def get_change_request(conn: sqlite3.Connection, request_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM change_requests WHERE id = ?", (request_id,)).fetchone()
    return dict(row) if row else None


def update_change_request_status(conn: sqlite3.Connection, request_id: int, status: str, admin_response: str = "") -> bool:
    cursor = conn.execute(
        "UPDATE change_requests SET status = ?, admin_response = ? WHERE id = ?",
        (status, admin_response, request_id),
    )
    conn.commit()
    return cursor.rowcount > 0


def add_coordinator_note(conn: sqlite3.Connection, request_id: int, note: str) -> bool:
    cursor = conn.execute(
        "UPDATE change_requests SET coordinator_note = ? WHERE id = ?",
        (note, request_id),
    )
    conn.commit()
    return cursor.rowcount > 0
