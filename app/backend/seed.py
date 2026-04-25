from __future__ import annotations

import sqlite3


def _count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])


def seed_database(conn: sqlite3.Connection) -> None:
    if _count(conn, "teachers") > 0:
        return

    conn.executemany(
        "INSERT INTO users(name, email, role) VALUES (?, ?, ?)",
        [
            ("Timetable Admin", "admin@utos.local", "administrator"),
            ("Department Coordinator", "coordinator@utos.local", "coordinator"),
            ("Facility Manager", "facilities@utos.local", "facility_manager"),
            ("System Administrator", "sysadmin@utos.local", "system_admin"),
        ],
    )

    conn.executemany(
        "INSERT INTO teachers(name, department, max_daily_load) VALUES (?, ?, ?)",
        [
            ("Dr. Ayesha Khan", "Computer Science", 4),
            ("Dr. Bilal Ahmed", "Computer Science", 3),
            ("Prof. Sara Malik", "Computer Science", 4),
            ("Dr. Hamza Noor", "Artificial Intelligence", 3),
            ("Ms. Zainab Ali", "Software Engineering", 4),
        ],
    )

    conn.executemany(
        "INSERT INTO rooms(code, building, floor, capacity, room_type, features) VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("A-101", "Alpha", 1, 45, "lecture", "projector,whiteboard"),
            ("A-204", "Alpha", 2, 60, "lecture", "projector,smart-board"),
            ("B-110", "Beta", 1, 60, "lab", "computers,projector"),
            ("B-210", "Beta", 2, 50, "lecture", "projector"),
            ("C-301", "Core", 3, 80, "auditorium", "projector,sound"),
        ],
    )

    conn.executemany(
        "INSERT INTO sections(name, department, size) VALUES (?, ?, ?)",
        [
            ("BSAI-4A", "Artificial Intelligence", 42),
            ("BSAI-4B", "Artificial Intelligence", 48),
            ("BSSE-6A", "Software Engineering", 35),
            ("BSCS-2A", "Computer Science", 55),
        ],
    )

    conn.executemany(
        """
        INSERT INTO courses(code, title, teacher_id, section_id, weekly_sessions, required_room_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            ("SE-301", "Software Engineering", 5, 2, 2, "lecture"),
            ("AI-220", "Artificial Intelligence", 4, 1, 2, "lecture"),
            ("DB-210", "Database Systems", 1, 4, 2, "lab"),
            ("OS-240", "Operating Systems", 2, 4, 2, "lecture"),
            ("ML-330", "Machine Learning", 3, 1, 2, "lab"),
            ("HCI-310", "Human Computer Interaction", 5, 3, 2, "lecture"),
            ("DSA-120", "Data Structures", 1, 2, 2, "lecture"),
            ("QA-360", "Software Quality Assurance", 2, 3, 1, "lecture"),
        ],
    )

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    periods = [
        ("08:30", "10:00", 1, 1, 0),
        ("10:00", "11:30", 2, 1, 0),
        ("11:30", "13:00", 3, 0, 0),
        ("14:00", "15:30", 4, 0, 0),
        ("15:30", "17:00", 5, 0, 1),
    ]
    slots = []
    order = 1
    for day in days:
        for start, end, day_order, is_morning, is_last in periods:
            slots.append((day, start, end, order, is_morning, is_last))
            order += 1
    conn.executemany(
        """
        INSERT INTO timeslots(day, start_time, end_time, sort_order, is_morning, is_last_slot)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        slots,
    )

    conn.executemany(
        "INSERT INTO holidays(name, day) VALUES (?, ?)",
        [
            ("Department seminar day", "Friday"),
        ],
    )

    friday_slots = conn.execute("SELECT id FROM timeslots WHERE day = 'Friday'").fetchall()
    unavailable = []
    for row in friday_slots:
        unavailable.append((2, row["id"], 0))
    late_slots = conn.execute("SELECT id FROM timeslots WHERE start_time = '15:30'").fetchall()
    for row in late_slots:
        unavailable.append((4, row["id"], 0))
    conn.executemany(
        """
        INSERT INTO teacher_availability(teacher_id, timeslot_id, is_available)
        VALUES (?, ?, ?)
        """,
        unavailable,
    )

    conn.executemany(
        "INSERT INTO preferences(key, label, enabled, weight, value) VALUES (?, ?, ?, ?, ?)",
        [
            ("morning_preference", "Prefer morning classes", 1, 2, ""),
            ("early_ending", "Reduce late-day classes", 1, 2, ""),
            ("room_proximity", "Prefer nearby rooms for same teacher", 1, 1, ""),
            ("energy_saving", "Compact building usage", 1, 1, ""),
            ("traffic_reduction", "Avoid final daily slot", 1, 3, ""),
        ],
    )
