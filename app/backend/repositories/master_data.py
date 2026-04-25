from __future__ import annotations

import sqlite3

from ..database import rows_to_dicts


def get_master_data(conn: sqlite3.Connection) -> dict:
    return {
        "users": rows_to_dicts(conn.execute("SELECT * FROM users ORDER BY role, name")),
        "teachers": rows_to_dicts(conn.execute("SELECT * FROM teachers ORDER BY name")),
        "rooms": rows_to_dicts(conn.execute("SELECT * FROM rooms ORDER BY building, code")),
        "sections": rows_to_dicts(conn.execute("SELECT * FROM sections ORDER BY department, name")),
        "courses": rows_to_dicts(
            conn.execute(
                """
                SELECT c.*, t.name AS teacher_name, s.name AS section_name, s.size AS section_size
                FROM courses c
                JOIN teachers t ON t.id = c.teacher_id
                JOIN sections s ON s.id = c.section_id
                ORDER BY c.code
                """
            )
        ),
        "timeslots": rows_to_dicts(conn.execute("SELECT * FROM timeslots ORDER BY sort_order")),
        "holidays": rows_to_dicts(conn.execute("SELECT * FROM holidays ORDER BY day")),
        "preferences": rows_to_dicts(conn.execute("SELECT * FROM preferences ORDER BY id")),
    }


def get_solver_problem(conn: sqlite3.Connection) -> dict:
    return {
        "teachers": rows_to_dicts(conn.execute("SELECT * FROM teachers")),
        "rooms": rows_to_dicts(conn.execute("SELECT * FROM rooms")),
        "sections": rows_to_dicts(conn.execute("SELECT * FROM sections")),
        "courses": rows_to_dicts(
            conn.execute(
                """
                SELECT c.*, t.name AS teacher_name, t.max_daily_load, s.name AS section_name, s.size AS section_size
                FROM courses c
                JOIN teachers t ON t.id = c.teacher_id
                JOIN sections s ON s.id = c.section_id
                """
            )
        ),
        "timeslots": rows_to_dicts(conn.execute("SELECT * FROM timeslots ORDER BY sort_order")),
        "holidays": rows_to_dicts(conn.execute("SELECT * FROM holidays")),
        "availability": rows_to_dicts(conn.execute("SELECT * FROM teacher_availability")),
        "preferences": rows_to_dicts(conn.execute("SELECT * FROM preferences")),
    }
