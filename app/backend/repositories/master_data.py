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


def insert_teacher(conn: sqlite3.Connection, name: str, department: str, max_daily_load: int = 4) -> int:
    cursor = conn.execute(
        "INSERT INTO teachers (name, department, max_daily_load) VALUES (?, ?, ?)",
        (name, department, max_daily_load)
    )
    conn.commit()
    return cursor.lastrowid


def update_teacher(conn: sqlite3.Connection, teacher_id: int, name: str, department: str, max_daily_load: int) -> None:
    conn.execute(
        "UPDATE teachers SET name = ?, department = ?, max_daily_load = ? WHERE id = ?",
        (name, department, max_daily_load, teacher_id)
    )
    conn.commit()


def delete_teacher(conn: sqlite3.Connection, teacher_id: int) -> None:
    conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
    conn.commit()


def insert_room(conn: sqlite3.Connection, code: str, building: str, floor: int, capacity: int, room_type: str, features: str = "") -> int:
    cursor = conn.execute(
        "INSERT INTO rooms (code, building, floor, capacity, room_type, features) VALUES (?, ?, ?, ?, ?, ?)",
        (code, building, floor, capacity, room_type, features)
    )
    conn.commit()
    return cursor.lastrowid


def update_room(conn: sqlite3.Connection, room_id: int, code: str, building: str, floor: int, capacity: int, room_type: str, features: str = "") -> None:
    conn.execute(
        "UPDATE rooms SET code = ?, building = ?, floor = ?, capacity = ?, room_type = ?, features = ? WHERE id = ?",
        (code, building, floor, capacity, room_type, features, room_id)
    )
    conn.commit()


def delete_room(conn: sqlite3.Connection, room_id: int) -> None:
    conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
    conn.commit()


def insert_section(conn: sqlite3.Connection, name: str, department: str, size: int) -> int:
    cursor = conn.execute(
        "INSERT INTO sections (name, department, size) VALUES (?, ?, ?)",
        (name, department, size)
    )
    conn.commit()
    return cursor.lastrowid


def update_section(conn: sqlite3.Connection, section_id: int, name: str, department: str, size: int) -> None:
    conn.execute(
        "UPDATE sections SET name = ?, department = ?, size = ? WHERE id = ?",
        (name, department, size, section_id)
    )
    conn.commit()


def delete_section(conn: sqlite3.Connection, section_id: int) -> None:
    conn.execute("DELETE FROM sections WHERE id = ?", (section_id,))
    conn.commit()


def insert_course(conn: sqlite3.Connection, code: str, title: str, teacher_id: int, section_id: int, weekly_sessions: int, required_room_type: str) -> int:
    cursor = conn.execute(
        "INSERT INTO courses (code, title, teacher_id, section_id, weekly_sessions, required_room_type) VALUES (?, ?, ?, ?, ?, ?)",
        (code, title, teacher_id, section_id, weekly_sessions, required_room_type)
    )
    conn.commit()
    return cursor.lastrowid


def update_course(conn: sqlite3.Connection, course_id: int, code: str, title: str, teacher_id: int, section_id: int, weekly_sessions: int, required_room_type: str) -> None:
    conn.execute(
        "UPDATE courses SET code = ?, title = ?, teacher_id = ?, section_id = ?, weekly_sessions = ?, required_room_type = ? WHERE id = ?",
        (code, title, teacher_id, section_id, weekly_sessions, required_room_type, course_id)
    )
    conn.commit()


def delete_course(conn: sqlite3.Connection, course_id: int) -> None:
    conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    conn.commit()
