"""Stress-seed the running UTOS dev server with a large, deliberately tough dataset.

Adds (via the public API, as the admin actor):
- 25 teachers (one overloaded: max 1 class/day, six courses; one barely available)
- 18 rooms in 4 buildings (lecture/lab/auditorium mix)
- 13 sections, one of them larger than every room (must end up unplaced)
- ~55 courses incl. lab- and auditorium-required ones
- an extra Wednesday holiday (leaves only Mon/Tue/Thu schedulable)
- user accounts for every new teacher and 3 students per section (direct DB)

Then: generate -> lock a few entries -> re-optimize -> publish, printing metrics.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8765"
DB = Path(__file__).resolve().parents[1] / "app" / "data" / "utos.sqlite"
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


def main():
    status, _ = call("/api/health")
    assert status == 200, "server not running on :8765"

    first_names = ["Imran", "Sana", "Tariq", "Nadia", "Faisal", "Hira", "Usman", "Mahnoor",
                   "Kamran", "Rabia", "Junaid", "Amna", "Shahid", "Iqra", "Adnan", "Lubna",
                   "Waqar", "Mehwish", "Salman", "Bushra", "Asad", "Kiran", "Fahad", "Sadia", "Zubair"]
    departments = ["Computer Science", "Artificial Intelligence", "Software Engineering", "Data Science"]

    teacher_ids = []
    for i, name in enumerate(first_names):
        max_load = 1 if i == 0 else (2 if i % 5 == 0 else 4)  # i==0 => Dr. Overload
        status, resp = call("/api/master-data/teachers", "POST", {
            "name": f"Dr. {name} Stress", "department": departments[i % 4],
            "max_daily_load": max_load})
        assert status == 201, resp
        teacher_ids.append(resp["id"])

    buildings = [("North", 1), ("South", 2), ("East", 3), ("West", 0)]
    room_ids = []
    for i in range(18):
        bldg, floor = buildings[i % 4]
        room_type = "lab" if i % 5 == 4 else ("auditorium" if i in (8, 16) else "lecture")
        capacity = 100 if room_type == "auditorium" else (40 if room_type == "lab" else 30 + (i % 6) * 12)
        status, resp = call("/api/master-data/rooms", "POST", {
            "code": f"ST-{i + 100}", "building": bldg, "floor": floor,
            "capacity": capacity, "room_type": room_type})
        assert status == 201, resp
        room_ids.append(resp["id"])

    section_ids = []
    for i in range(12):
        size = 28 + (i * 7) % 55
        status, resp = call("/api/master-data/sections", "POST", {
            "name": f"STR-{i + 1}{'AB'[i % 2]}", "department": departments[i % 4], "size": size})
        assert status == 201, resp
        section_ids.append(resp["id"])
    # The impossible section: bigger than every room on campus.
    status, resp = call("/api/master-data/sections", "POST", {
        "name": "MEGA-1A", "department": "Computer Science", "size": 150})
    assert status == 201, resp
    mega_section = resp["id"]

    course_ids = []
    course_no = 0
    for s_index, section_id in enumerate(section_ids):
        for c in range(4):
            course_no += 1
            teacher_id = teacher_ids[(s_index * 4 + c + 1) % len(teacher_ids)]
            room_type = "lab" if c == 3 else ("auditorium" if course_no % 17 == 0 else "lecture")
            status, resp = call("/api/master-data/courses", "POST", {
                "code": f"STR-{course_no:03d}", "title": f"Stress Course {course_no}",
                "teacher_id": teacher_id, "section_id": section_id,
                "weekly_sessions": 1 + (course_no % 2), "required_room_type": room_type})
            assert status == 201, resp
            course_ids.append(resp["id"])

    # Dr. Overload (max 1/day): six 2-session courses => 12 sessions, only 3 workdays.
    for c in range(6):
        course_no += 1
        status, resp = call("/api/master-data/courses", "POST", {
            "code": f"OVR-{c + 1:02d}", "title": f"Overload Course {c + 1}",
            "teacher_id": teacher_ids[0], "section_id": section_ids[c % len(section_ids)],
            "weekly_sessions": 2, "required_room_type": "lecture"})
        assert status == 201, resp

    # Courses for the impossible MEGA section.
    for c in range(2):
        course_no += 1
        status, resp = call("/api/master-data/courses", "POST", {
            "code": f"MEG-{c + 1:02d}", "title": f"Mega Course {c + 1}",
            "teacher_id": teacher_ids[5 + c], "section_id": mega_section,
            "weekly_sessions": 2, "required_room_type": "lecture"})
        assert status == 201, resp

    # Teacher 2 is only available Monday morning (slots fetched from master data).
    status, master = call("/api/master-data")
    monday_morning = [t["id"] for t in master["timeslots"] if not (t["day"] == "Monday" and t["is_morning"])]
    status, resp = call(f"/api/teacher-availability/{teacher_ids[1]}", "PUT",
                        {"unavailable_slot_ids": monday_morning})
    assert status == 200, resp

    # Extra holiday: Wednesday off (Friday is already blocked by the original seed).
    status, resp = call("/api/master-data/holidays", "POST", {"name": "Stress Wednesday", "day": "Wednesday"})
    assert status in (201, 409), resp

    # User accounts so every teacher and several students per section can log in.
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    created_users = 0
    for i, teacher_id in enumerate(teacher_ids):
        try:
            conn.execute(
                "INSERT INTO users (name, email, role, teacher_id, section_id) VALUES (?, ?, 'teacher', ?, NULL)",
                (f"Dr. {first_names[i]} Stress", f"stress.teacher{i}@utos.local", teacher_id))
            created_users += 1
        except sqlite3.IntegrityError:
            pass
    for s_index, section_id in enumerate(section_ids + [mega_section]):
        for n in range(3):
            try:
                conn.execute(
                    "INSERT INTO users (name, email, role, teacher_id, section_id) VALUES (?, ?, 'student', NULL, ?)",
                    (f"Student {s_index + 1}-{n + 1}", f"stress.student{s_index}_{n}@utos.local", section_id))
                created_users += 1
            except sqlite3.IntegrityError:
                pass
    conn.commit()
    conn.close()

    print(f"Seeded: {len(teacher_ids)} teachers, {len(room_ids)} rooms, "
          f"{len(section_ids) + 1} sections, {course_no} courses, {created_users} user accounts")

    # ---- Stress run: generate -> lock -> reoptimize -> publish ----
    t0 = time.time()
    status, generated = call("/api/timetable/generate", "POST")
    elapsed = time.time() - t0
    assert status == 200, generated
    metrics = generated["result"]["metrics"]
    print(f"\nGENERATE took {elapsed:.1f}s -> version {generated['versionId']}")
    print(f"  score={metrics['score']} unplaced={metrics['unplaced_count']} "
          f"soft_penalty={metrics['soft_penalty']} nodes={metrics['search_nodes']}")
    print(f"  warnings: {generated['result']['warnings']}")

    placed = [e for e in generated["latestTimetable"]["entries"] if e["status"] == "placed"]
    unplaced = [e for e in generated["latestTimetable"]["entries"] if e["status"] == "unplaced"]
    mega_unplaced = [e for e in unplaced if e["course_code"].startswith("MEG-")]
    print(f"  placed={len(placed)} unplaced={len(unplaced)} (MEGA section unplaced: {len(mega_unplaced)}/4)")

    # Hard-constraint audit of the placed result.
    seen = {}
    clashes = 0
    for e in placed:
        for key in (("T", e["teacher_id"], e["timeslot_id"]), ("R", e["room_id"], e["timeslot_id"]),
                    ("S", e["section_id"], e["timeslot_id"])):
            if key in seen:
                clashes += 1
            seen[key] = e["event_uid"]
    cap_violations = sum(1 for e in placed if e["section_size"] > e["room_capacity"])
    holiday_violations = sum(1 for e in placed if e["day"] in ("Wednesday", "Friday"))
    print(f"  clashes={clashes} capacity_violations={cap_violations} holiday_violations={holiday_violations}")

    lock_ids = [e["id"] for e in placed[:5]]
    for entry_id in lock_ids:
        status, resp = call(f"/api/timetable/entry/{entry_id}/lock", "PUT")
        assert status == 200, resp

    t0 = time.time()
    status, repaired = call("/api/timetable/reoptimize", "POST")
    elapsed = time.time() - t0
    assert status == 200, repaired
    print(f"\nREOPTIMIZE took {elapsed:.1f}s -> version {repaired['versionId']}")
    print(f"  disruption: {repaired['disruption']}")
    locked_kept = [e for e in repaired["latestTimetable"]["entries"] if e["locked"]]
    print(f"  locked entries kept: {len(locked_kept)}/5")

    status, resp = call(f"/api/timetable/{repaired['versionId']}/publish", "PUT")
    assert status == 200, resp
    print(f"\nPUBLISH ok, notified {resp['notified']} users")

    failures = []
    if clashes or cap_violations or holiday_violations:
        failures.append("hard constraint violated")
    if len(mega_unplaced) != 4:
        failures.append("MEGA section should be fully unplaced")
    if len(locked_kept) != 5:
        failures.append("locked entries lost in repair")
    print("\nSTRESS RESULT:", "PASS" if not failures else f"FAIL: {failures}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
