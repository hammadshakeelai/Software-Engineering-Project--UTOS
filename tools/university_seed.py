"""Realistic, *solvable* university dataset for UTOS.

Models a Faculty of Computing with 4 programs, 8 sections, 14 teachers,
14 rooms (incl. labs + an auditorium), 5 working days x 6 periods = 30 slots,
and ~36 course offerings (~64 weekly sessions). Sized so the solver can place
every session conflict-free — the goal is to prove all sections get a clean
schedule, the opposite of the deliberately-infeasible stress test.

Run against a FRESH database (delete app/data/utos.sqlite first) so it seeds.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"
ADMIN = 1


def call(path, method="GET", data=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={"Content-Type": "application/json", "X-User-Id": str(ADMIN)},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode() or "{}")


def must(status, resp, ok=(200, 201)):
    assert status in ok, f"unexpected {status}: {resp}"
    return resp


# --- Teachers (14) across 4 programs, generous daily load ---
TEACHERS = [
    ("Dr. Ayesha Khan", "Computer Science", 5),
    ("Dr. Bilal Ahmed", "Computer Science", 5),
    ("Prof. Sara Malik", "Computer Science", 5),
    ("Dr. Hamza Noor", "Artificial Intelligence", 5),
    ("Dr. Mariam Yusuf", "Artificial Intelligence", 5),
    ("Ms. Zainab Ali", "Software Engineering", 5),
    ("Mr. Omar Farooq", "Software Engineering", 5),
    ("Dr. Nida Aslam", "Data Science", 5),
    ("Dr. Kamran Shah", "Data Science", 5),
    ("Prof. Imran Qureshi", "Computer Science", 5),
    ("Dr. Fatima Raza", "Artificial Intelligence", 5),
    ("Mr. Usman Tariq", "Software Engineering", 5),
    ("Dr. Hina Baig", "Data Science", 5),
    ("Dr. Saad Mahmood", "Computer Science", 5),
]

# --- Rooms (14): lecture halls + labs + 1 auditorium ---
ROOMS = [
    ("LH-101", "Main", 1, 60, "lecture"),
    ("LH-102", "Main", 1, 60, "lecture"),
    ("LH-201", "Main", 2, 50, "lecture"),
    ("LH-202", "Main", 2, 50, "lecture"),
    ("LH-301", "Annex", 3, 45, "lecture"),
    ("LH-302", "Annex", 3, 45, "lecture"),
    ("LAB-1", "Tech", 1, 50, "lab"),   # large computer labs hold a full 2nd-year cohort
    ("LAB-2", "Tech", 1, 50, "lab"),
    ("LAB-3", "Tech", 2, 40, "lab"),
    ("LAB-4", "Tech", 2, 40, "lab"),
    ("SEM-1", "Annex", 1, 30, "lecture"),
    ("SEM-2", "Annex", 1, 30, "lecture"),
    ("AUD-1", "Main", 0, 120, "auditorium"),
    ("AUD-2", "Tech", 0, 100, "auditorium"),
]

# --- Sections (8): 2 per program, comfortable sizes ---
SECTIONS = [
    ("BSCS-2A", "Computer Science", 45),
    ("BSCS-4A", "Computer Science", 40),
    ("BSAI-2A", "Artificial Intelligence", 42),
    ("BSAI-4A", "Artificial Intelligence", 38),
    ("BSSE-2A", "Software Engineering", 40),
    ("BSSE-4A", "Software Engineering", 35),
    ("BSDS-2A", "Data Science", 38),
    ("BSDS-4A", "Data Science", 30),
]

# Course catalog: (code, title, teacher_index, section_index, weekly_sessions, room_type)
# Each section gets ~4-5 courses; lab courses require labs.
COURSES = [
    # BSCS-2A
    ("CS-201", "Data Structures", 0, 0, 2, "lecture"),
    ("CS-202", "OOP", 1, 0, 2, "lecture"),
    ("CS-203", "Digital Logic", 9, 0, 1, "lecture"),
    ("CS-204", "Programming Lab", 13, 0, 1, "lab"),
    # BSCS-4A
    ("CS-401", "Operating Systems", 2, 1, 2, "lecture"),
    ("CS-402", "Databases", 0, 1, 2, "lecture"),
    ("CS-403", "Networks", 1, 1, 1, "lecture"),
    ("CS-404", "DB Lab", 13, 1, 1, "lab"),
    # BSAI-2A
    ("AI-201", "Intro to AI", 3, 2, 2, "lecture"),
    ("AI-202", "Linear Algebra", 4, 2, 2, "lecture"),
    ("AI-203", "Python for AI", 10, 2, 1, "lab"),
    ("AI-204", "Discrete Math", 3, 2, 1, "lecture"),
    # BSAI-4A
    ("AI-401", "Machine Learning", 4, 3, 2, "lecture"),
    ("AI-402", "Deep Learning", 3, 3, 2, "lecture"),
    ("AI-403", "ML Lab", 10, 3, 1, "lab"),
    ("AI-404", "NLP", 4, 3, 1, "lecture"),
    # BSSE-2A
    ("SE-201", "Software Engineering", 5, 4, 2, "lecture"),
    ("SE-202", "Web Development", 6, 4, 2, "lab"),
    ("SE-203", "Requirements Eng", 11, 4, 1, "lecture"),
    ("SE-204", "HCI", 5, 4, 1, "lecture"),
    # BSSE-4A
    ("SE-401", "Software Architecture", 6, 5, 2, "lecture"),
    ("SE-402", "Quality Assurance", 5, 5, 2, "lecture"),
    ("SE-403", "DevOps Lab", 11, 5, 1, "lab"),
    ("SE-404", "Project Management", 6, 5, 1, "lecture"),
    # BSDS-2A
    ("DS-201", "Statistics", 7, 6, 2, "lecture"),
    ("DS-202", "Data Wrangling", 8, 6, 2, "lab"),
    ("DS-203", "Probability", 12, 6, 1, "lecture"),
    ("DS-204", "R Programming", 7, 6, 1, "lab"),
    # BSDS-4A
    ("DS-401", "Big Data", 8, 7, 2, "lecture"),
    ("DS-402", "Data Visualization", 12, 7, 2, "lecture"),
    ("DS-403", "Cloud Lab", 8, 7, 1, "lab"),
    ("DS-404", "Capstone Seminar", 7, 7, 1, "auditorium"),
]


def reset_master_data():
    """Clear seeded master data + timetables so this dataset loads cleanly.

    Done directly against SQLite (the API has no bulk-clear endpoint by design).
    Users/notifications/audit are preserved.
    """
    import sqlite3
    from pathlib import Path

    db = Path(__file__).resolve().parents[1] / "app" / "data" / "utos.sqlite"
    conn = sqlite3.connect(db)
    conn.execute("PRAGMA foreign_keys = OFF")
    for table in ("timetable_entries", "timetable_versions", "change_requests",
                  "teacher_availability", "courses", "sections", "rooms", "teachers", "holidays"):
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()


def create_user_accounts(teacher_ids, section_ids):
    """Create teacher + student login accounts directly (no user-CRUD API yet)."""
    import sqlite3
    from pathlib import Path

    db = Path(__file__).resolve().parents[1] / "app" / "data" / "utos.sqlite"
    conn = sqlite3.connect(db)
    # Remove orphaned (section-less) student users left by the master-data reset.
    conn.execute("DELETE FROM users WHERE role IN ('teacher', 'student')")
    created = 0
    for i, (name, _dept, _load) in enumerate(TEACHERS):
        try:
            conn.execute(
                "INSERT INTO users (name, email, role, teacher_id) VALUES (?, ?, 'teacher', ?)",
                (name, f"teacher{i}@univ.utos", teacher_ids[i]))
            created += 1
        except sqlite3.IntegrityError:
            pass
    for s_idx, (sec_name, _dept, _size) in enumerate(SECTIONS):
        for n in range(2):
            try:
                conn.execute(
                    "INSERT INTO users (name, email, role, section_id) VALUES (?, ?, 'student', ?)",
                    (f"{sec_name} Student {n + 1}", f"stu_{s_idx}_{n}@univ.utos", section_ids[s_idx]))
                created += 1
            except sqlite3.IntegrityError:
                pass
    conn.commit()
    conn.close()
    return created


def main():
    s, _ = call("/api/health")
    assert s == 200, "server not running on :8765"
    reset_master_data()

    teacher_ids, room_ids, section_ids = [], [], []
    for name, dept, load in TEACHERS:
        teacher_ids.append(must(*call("/api/master-data/teachers", "POST",
                                       {"name": name, "department": dept, "max_daily_load": load}))["id"])
    for code, bldg, floor, cap, rtype in ROOMS:
        room_ids.append(must(*call("/api/master-data/rooms", "POST",
                                    {"code": code, "building": bldg, "floor": floor,
                                     "capacity": cap, "room_type": rtype}))["id"])
    for name, dept, size in SECTIONS:
        section_ids.append(must(*call("/api/master-data/sections", "POST",
                                       {"name": name, "department": dept, "size": size}))["id"])
    for code, title, t_idx, s_idx, sessions, rtype in COURSES:
        must(*call("/api/master-data/courses", "POST", {
            "code": code, "title": title,
            "teacher_id": teacher_ids[t_idx], "section_id": section_ids[s_idx],
            "weekly_sessions": sessions, "required_room_type": rtype}))

    # Friday off — common in the region; leaves Mon-Thu (24 slots) for teaching.
    must(*call("/api/master-data/holidays", "POST", {"name": "Friday (non-teaching)", "day": "Friday"}), ok=(201, 409))

    # Login accounts: one user per teacher, two students per section, so every
    # role can sign in and see their own schedule (FR-09).
    created = create_user_accounts(teacher_ids, section_ids)
    print(f"Created {created} login accounts (teachers + 2 students/section)")

    total_sessions = sum(c[4] for c in COURSES)
    print(f"Seeded {len(TEACHERS)} teachers, {len(ROOMS)} rooms, {len(SECTIONS)} sections, "
          f"{len(COURSES)} courses ({total_sessions} weekly sessions)")

    # Generate and verify every section gets a conflict-free schedule.
    s, gen = call("/api/timetable/generate", "POST")
    must(s, gen)
    m = gen["result"]["metrics"]
    print(f"\nGenerated version {gen['versionId']}: score={m['score']} "
          f"unplaced={m['unplaced_count']} soft_penalty={m['soft_penalty']}")

    placed = [e for e in gen["latestTimetable"]["entries"] if e["status"] == "placed"]
    seen, clashes = {}, 0
    for e in placed:
        for key in (("T", e["teacher_id"], e["timeslot_id"]),
                    ("R", e["room_id"], e["timeslot_id"]),
                    ("S", e["section_id"], e["timeslot_id"])):
            if key in seen:
                clashes += 1
            seen[key] = e["event_uid"]
    cap_bad = sum(1 for e in placed if e["section_size"] > e["room_capacity"])
    holiday_bad = sum(1 for e in placed if e["day"] == "Friday")  # Friday is a holiday here

    by_section = {}
    for e in placed:
        by_section.setdefault(e["section_name"], 0)
        by_section[e["section_name"]] += 1
    print("\nPer-section placed sessions:")
    for name in sorted(by_section):
        print(f"  {name}: {by_section[name]}")

    sections_with_schedule = len(by_section)
    print(f"\nclashes={clashes} capacity_violations={cap_bad} friday_violations={holiday_bad}")
    print(f"sections with a schedule: {sections_with_schedule}/{len(SECTIONS)}")

    # Publish so teachers/students can see it.
    must(*call(f"/api/timetable/{gen['versionId']}/publish", "PUT"))
    print("Published.")

    ok = (clashes == 0 and cap_bad == 0 and holiday_bad == 0
          and sections_with_schedule == len(SECTIONS) and m["unplaced_count"] == 0)
    print("\nUNIVERSITY DATASET:", "PASS — all sections fully scheduled, zero conflicts" if ok
          else f"REVIEW — unplaced={m['unplaced_count']}, check above")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
