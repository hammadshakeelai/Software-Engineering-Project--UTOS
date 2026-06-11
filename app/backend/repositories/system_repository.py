from __future__ import annotations

import json
import sqlite3

from ..database import rows_to_dicts


def notify_user(conn: sqlite3.Connection, user_id: int, category: str, title: str, message: str = "") -> None:
    conn.execute(
        "INSERT INTO notifications (user_id, category, title, message) VALUES (?, ?, ?, ?)",
        (user_id, category, title, message),
    )


def notify_roles(conn: sqlite3.Connection, roles: list[str], category: str, title: str, message: str = "") -> int:
    placeholders = ",".join("?" for _ in roles)
    users = conn.execute(f"SELECT id FROM users WHERE role IN ({placeholders})", roles).fetchall()
    for user in users:
        notify_user(conn, user["id"], category, title, message)
    return len(users)


def get_notifications(conn: sqlite3.Connection, user_id: int, limit: int = 50) -> list[dict]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
    )


def mark_notification_read(conn: sqlite3.Connection, notification_id: int) -> bool:
    cursor = conn.execute("UPDATE notifications SET read = 1 WHERE id = ?", (notification_id,))
    conn.commit()
    return cursor.rowcount > 0


def log_audit(
    conn: sqlite3.Connection,
    actor_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    old_value: dict | str = "",
    new_value: dict | str = "",
) -> None:
    def _serialize(value: dict | str) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, default=str)

    conn.execute(
        """INSERT INTO audit_log (actor_id, action, entity_type, entity_id, old_value, new_value)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (actor_id, action, entity_type, entity_id, _serialize(old_value), _serialize(new_value)),
    )


def get_audit_log(conn: sqlite3.Connection, limit: int = 100) -> list[dict]:
    return rows_to_dicts(
        conn.execute(
            """
            SELECT a.*, u.name AS actor_name, u.role AS actor_role
            FROM audit_log a
            LEFT JOIN users u ON u.id = a.actor_id
            ORDER BY a.id DESC
            LIMIT ?
            """,
            (limit,),
        )
    )
