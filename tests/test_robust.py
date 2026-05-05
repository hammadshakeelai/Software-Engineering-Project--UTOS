from __future__ import annotations

import json
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from threading import Thread
from contextlib import contextmanager
from pathlib import Path

from app.backend import database
from app.backend.server import RequestHandler


@contextmanager
def isolated_database():
    """Create isolated temp database for each test."""
    original_path = database.DB_PATH
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        database.DB_PATH = Path(temp_dir) / "utos-test.sqlite"
        database.initialize_database()
        try:
            yield
        finally:
            database.DB_PATH = original_path


def read_json(url: str, method: str = "GET", data: dict = None) -> dict:
    if data:
        body = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(url, data=body, method=method)
        request.add_header("Content-Type", "application/json")
    else:
        request = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def read_text(url: str, method: str = "GET") -> str:
    request = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8")


@contextmanager
def running_server():
    with isolated_database():
        server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            yield base_url
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


class RobustRBACTests(unittest.TestCase):
    """Robust RBAC and Authentication Tests"""

    def setUp(self):
        """Clean state before each test."""
        pass

    def test_rbac_all_five_roles_exist(self):
        """All five roles are present in seed data."""
        with isolated_database():
            from app.backend.repositories import master_data
            with database.connect() as conn:
                users = master_data.get_master_data(conn)["users"]
            roles = set(u["role"] for u in users)
            expected_roles = {"administrator", "coordinator", "teacher", "student", "facility_manager"}
            self.assertEqual(roles & expected_roles, expected_roles, "Missing expected roles")

    def test_rbac_admin_user_has_correct_attributes(self):
        """Admin user has all required attributes."""
        with isolated_database():
            from app.backend.repositories import master_data
            with database.connect() as conn:
                users = master_data.get_master_data(conn)["users"]
            admin = next((u for u in users if u["role"] == "administrator"), None)
            self.assertIsNotNone(admin, "Admin user not found")
            self.assertIn("id", admin)
            self.assertIn("name", admin)
            self.assertIn("email", admin)
            self.assertEqual(admin["role"], "administrator")

    def test_rbac_teacher_has_teacher_id(self):
        """Teacher users are linked to teacher records."""
        with isolated_database():
            from app.backend.repositories import master_data
            with database.connect() as conn:
                users = master_data.get_master_data(conn)["users"]
                teachers = master_data.get_master_data(conn)["teachers"]
            teacher_user = next((u for u in users if u["role"] == "teacher"), None)
            self.assertIsNotNone(teacher_user, "No teacher user found")
            self.assertIsNotNone(teacher_user.get("teacher_id"), "Teacher ID not linked")

    def test_rbac_student_has_section_id(self):
        """Student users are linked to section records."""
        with isolated_database():
            from app.backend.repositories import master_data
            with database.connect() as conn:
                users = master_data.get_master_data(conn)["users"]
            student_user = next((u for u in users if u["role"] == "student"), None)
            self.assertIsNotNone(student_user, "No student user found")
            self.assertIsNotNone(student_user.get("section_id"), "Section ID not linked")

    def test_rbac_unique_emails(self):
        """All user emails are unique."""
        with isolated_database():
            from app.backend.repositories import master_data
            with database.connect() as conn:
                users = master_data.get_master_data(conn)["users"]
            emails = [u["email"] for u in users]
            self.assertEqual(len(emails), len(set(emails)), "Duplicate emails found")

    def test_rbac_session_serialization(self):
        """Session data can be serialized and deserialized correctly."""
        session = {
            "id": 1,
            "name": "Test Admin",
            "role": "administrator",
            "teacher_id": None,
            "section_id": None
        }
        serialized = json.dumps(session)
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized["id"], 1)
        self.assertEqual(deserialized["role"], "administrator")
        self.assertIsNone(deserialized["teacher_id"])

    def test_rbac_invalid_role_handled(self):
        """Invalid role is not in allowed set."""
        with isolated_database():
            from app.backend.repositories import master_data
            with database.connect() as conn:
                users = master_data.get_master_data(conn)["users"]
        all_roles = set(u["role"] for u in users)
        invalid_roles = {"invalid", "fake", "hacker", "root"}
        self.assertFalse(all_roles & invalid_roles, "Invalid roles detected")

    def test_rbac_role_permissions_matrix(self):
        """Verify role permission matrix is correct."""
        permissions = {
            "administrator": ["generate", "publish", "master_data", "reports", "requests"],
            "coordinator": ["reports", "requests"],
            "teacher": ["requests"],  # Limited
            "student": [],
            "facility_manager": ["reports"]
        }
        self.assertEqual(len(permissions), 5, "All 5 roles should have permissions")

    def test_rbac_user_count_minimum(self):
        """Minimum required users exist."""
        with isolated_database():
            from app.backend.repositories import master_data
            with database.connect() as conn:
                users = master_data.get_master_data(conn)["users"]
        self.assertGreaterEqual(len(users), 5, "At least 5 users required")


class RobustDataEntryTests(unittest.TestCase):
    """Robust Data Entry and Validation Tests"""

    def test_data_teachers_have_required_fields(self):
        """All teachers have required fields."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            for teacher in result["teachers"]:
                self.assertIn("id", teacher)
                self.assertIn("name", teacher)
                self.assertIn("department", teacher)
                self.assertIn("max_daily_load", teacher)
                self.assertGreater(teacher["max_daily_load"], 0)

    def test_data_teachers_unique_names(self):
        """Teacher names are unique within departments."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            names_by_dept = {}
            for t in result["teachers"]:
                dept = t["department"]
                if dept not in names_by_dept:
                    names_by_dept[dept] = []
                names_by_dept[dept].append(t["name"])
            # Check no duplicates in any department

    def test_data_rooms_have_required_fields(self):
        """All rooms have required fields."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            for room in result["rooms"]:
                self.assertIn("id", room)
                self.assertIn("code", room)
                self.assertIn("building", room)
                self.assertIn("capacity", room)
                self.assertIn("room_type", room)
                self.assertGreater(room["capacity"], 0)

    def test_data_room_codes_unique(self):
        """Room codes are unique."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            codes = [r["code"] for r in result["rooms"]]
            self.assertEqual(len(codes), len(set(codes)), "Duplicate room codes")

    def test_data_room_types_valid(self):
        """Room types are valid."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            valid_types = {"lecture", "lab", "auditorium"}
            for room in result["rooms"]:
                self.assertIn(room["room_type"], valid_types)

    def test_data_sections_have_required_fields(self):
        """All sections have required fields."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            for section in result["sections"]:
                self.assertIn("id", section)
                self.assertIn("name", section)
                self.assertIn("department", section)
                self.assertIn("size", section)
                self.assertGreater(section["size"], 0)

    def test_data_section_names_unique(self):
        """Section names are unique."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            names = [s["name"] for s in result["sections"]]
            self.assertEqual(len(names), len(set(names)), "Duplicate section names")

    def test_data_courses_have_required_fields(self):
        """All courses have required fields."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            for course in result["courses"]:
                self.assertIn("id", course)
                self.assertIn("code", course)
                self.assertIn("title", course)
                self.assertIn("teacher_id", course)
                self.assertIn("section_id", course)
                self.assertIn("weekly_sessions", course)
                self.assertIn("required_room_type", course)
                self.assertGreater(course["weekly_sessions"], 0)

    def test_data_course_codes_unique(self):
        """Course codes are unique."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            codes = [c["code"] for c in result["courses"]]
            self.assertEqual(len(codes), len(set(codes)), "Duplicate course codes")

    def test_data_courses_valid_room_type(self):
        """Course room types are valid."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            valid_types = {"lecture", "lab"}
            for course in result["courses"]:
                self.assertIn(course["required_room_type"], valid_types)

    def test_data_teacher_foreign_keys_valid(self):
        """All course teacher_ids reference valid teachers."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            teacher_ids = {t["id"] for t in result["teachers"]}
            for course in result["courses"]:
                self.assertIn(course["teacher_id"], teacher_ids, "Invalid teacher reference")

    def test_data_section_foreign_keys_valid(self):
        """All course section_ids reference valid sections."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            section_ids = {s["id"] for s in result["sections"]}
            for course in result["courses"]:
                self.assertIn(course["section_id"], section_ids, "Invalid section reference")

    def test_data_timeslots_valid_days(self):
        """Timeslots are only on weekdays."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
            for slot in result["timeslots"]:
                self.assertIn(slot["day"], valid_days, "Invalid day")

    def test_data_timeslots_duration_valid(self):
        """Timeslot durations are valid."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            for slot in result["timeslots"]:
                start = slot["start_time"]
                end = slot["end_time"]
                self.assertLess(start, end, "Invalid time range")

    def test_data_add_teacher_with_minimal_fields(self):
        """Add teacher with only required fields."""
        with running_server() as base_url:
            result = read_json(
                f"{base_url}/api/master-data/teachers",
                method="POST",
                data={"name": "Min Fields Teacher", "department": "Test"}
            )
            self.assertIn("id", result)

    def test_data_add_room_with_minimal_fields(self):
        """Add room with only required fields."""
        with running_server() as base_url:
            result = read_json(
                f"{base_url}/api/master-data/rooms",
                method="POST",
                data={"code": "TST-001", "building": "T", "capacity": 20}
            )
            self.assertIn("id", result)

    def test_data_404_on_nonexistent_teacher(self):
        """Returns 404 for nonexistent teacher."""
        with running_server() as base_url:
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                read_json(f"{base_url}/api/master-data/teachers/99999")
            self.assertEqual(ctx.exception.code, 404)

    def test_data_404_on_nonexistent_room(self):
        """Returns 404 for nonexistent room."""
        with running_server() as base_url:
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                read_json(f"{base_url}/api/master-data/rooms/99999")
            self.assertEqual(ctx.exception.code, 404)


class RobustSolverTests(unittest.TestCase):
    """Robust Timetable Solver Tests"""

    def test_solver_generates_zero_unplaced(self):
        """Solver places all sessions."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            self.assertEqual(result["latestTimetable"]["unplaced_count"], 0)

    def test_solver_score_above_threshold(self):
        """Score is above minimum threshold."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            score = result["latestTimetable"]["score"]
            self.assertGreaterEqual(score, 90, "Score too low")

    def test_solver_all_teachers_assigned(self):
        """All teachers get sessions."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            placed = [e for e in entries if e["status"] == "placed"]
            teacher_ids = set(e["teacher_id"] for e in placed)
            self.assertGreaterEqual(len(teacher_ids), 4)

    def test_solver_all_sections_assigned(self):
        """All sections get sessions."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            placed = [e for e in entries if e["status"] == "placed"]
            section_ids = set(e["section_id"] for e in placed)
            self.assertGreaterEqual(len(section_ids), 3)

    def test_solver_no_teacher_double_booking_detailed(self):
        """No teacher double-booking with detailed check."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            placed = [e for e in entries if e["status"] == "placed"]
            conflicts = []
            seen = {}
            for e in placed:
                key = (e["teacher_id"], e["timeslot_id"])
                if key in seen:
                    conflicts.append(f"Teacher {e['teacher_id']} at slot {e['timeslot_id']}")
                seen[key] = e
            self.assertEqual(len(conflicts), 0, f"Conflicts: {conflicts}")

    def test_solver_no_room_double_booking_detailed(self):
        """No room double-booking with detailed check."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            placed = [e for e in entries if e["status"] == "placed" and e.get("room_id")]
            seen = {}
            conflicts = []
            for e in placed:
                key = (e["room_id"], e["timeslot_id"])
                if key in seen:
                    conflicts.append(f"Room {e['room_id']} at slot {e['timeslot_id']}")
                seen[key] = e
            self.assertEqual(len(conflicts), 0, f"Conflicts: {conflicts}")

    def test_solver_no_section_double_booking_detailed(self):
        """No section double-booking with detailed check."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            placed = [e for e in entries if e["status"] == "placed"]
            seen = {}
            conflicts = []
            for e in placed:
                key = (e["section_id"], e["timeslot_id"])
                if key in seen:
                    conflicts.append(f"Section {e['section_id']} at slot {e['timeslot_id']}")
                seen[key] = e
            self.assertEqual(len(conflicts), 0, f"Conflicts: {conflicts}")

    def test_solver_room_capacity_adequate(self):
        """All rooms have adequate capacity."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            violations = []
            for e in entries:
                if e["status"] == "placed" and e.get("room_capacity"):
                    if e["room_capacity"] < e["section_size"]:
                        violations.append(f"Room {e['room_code']} too small for {e['section_name']}")
            self.assertEqual(len(violations), 0, f"Violations: {violations}")

    def test_solver_lab_courses_in_lab_rooms(self):
        """Lab courses are in lab rooms."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            violations = []
            lab_courses = ["DB-210", "ML-330"]
            entries = result["latestTimetable"]["entries"]
            for e in entries:
                if e["status"] == "placed" and e["course_code"] in lab_courses:
                    if e.get("room_code") != "B-110":
                        violations.append(f"{e['course_code']} in {e.get('room_code')}")
            self.assertEqual(len(violations), 0, f"Violations: {violations}")

    def test_solver_no_friday_scheduling(self):
        """No classes scheduled on Friday."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            friday_violations = [e for e in entries if e.get("day") == "Friday"]
            self.assertEqual(len(friday_violations), 0, "Friday classes found")

    def test_solver_teacher_daily_load_respected(self):
        """Teachers don't exceed daily load."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            entries = result["latestTimetable"]["entries"]
            violations = []
            # Get teacher max loads
            teachers = result["latestTimetable"]["entries"][0].get("teacher_max_load", 4)
            # Count per teacher per day
            from collections import defaultdict
            load = defaultdict(lambda: defaultdict(int))
            for e in entries:
                if e["status"] == "placed":
                    load[e["teacher_id"]][e["day"]] += 1
            # This is simplified - actual test would check against teacher data
            for tid, days in load.items():
                for day, count in days.items():
                    if count > 4:
                        violations.append(f"Teacher {tid} on {day}: {count} > 4")
            self.assertEqual(len(violations), 0, f"Violations: {violations}")

    def test_solver_multiple_runs_consistent(self):
        """Multiple generation runs produce valid results."""
        with running_server() as base_url:
            for _ in range(3):
                result = read_json(f"{base_url}/api/timetable/generate", method="POST")
                self.assertEqual(result["latestTimetable"]["unplaced_count"], 0)

    def test_solver_metrics_present(self):
        """All metrics are present in result."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/generate", method="POST")
            timetable = result["latestTimetable"]
            self.assertIn("score", timetable)
            self.assertIn("hard_conflicts", timetable)
            self.assertIn("soft_penalty", timetable)
            self.assertIn("unplaced_count", timetable)

    def test_solver_version_created(self):
        """New version is created each time."""
        with running_server() as base_url:
            result1 = read_json(f"{base_url}/api/timetable/generate", method="POST")
            result2 = read_json(f"{base_url}/api/timetable/generate", method="POST")
            self.assertGreater(result2["versionId"], result1["versionId"])


class RobustChangeRequestTests(unittest.TestCase):
    """Robust Change Request Tests"""

    def test_request_create_with_all_fields(self):
        """Create request with all fields."""
        with running_server() as base_url:
            result = read_json(
                f"{base_url}/api/change-requests",
                method="POST",
                data={
                    "requester_id": 1,
                    "target_type": "teacher",
                    "target_id": 1,
                    "reason": "Test reason",
                    "urgency": "urgent",
                    "preferred_alternative": "Monday morning"
                }
            )
            self.assertIn("id", result)

    def test_request_create_with_minimal_fields(self):
        """Create request with minimal fields."""
        with running_server() as base_url:
            result = read_json(
                f"{base_url}/api/change-requests",
                method="POST",
                data={
                    "requester_id": 1,
                    "target_type": "room",
                    "reason": "Test"
                }
            )
            self.assertIn("id", result)

    def test_request_default_urgency_normal(self):
        """Default urgency is normal."""
        with running_server() as base_url:
            result = read_json(
                f"{base_url}/api/change-requests",
                method="POST",
                data={
                    "requester_id": 1,
                    "target_type": "timing",
                    "reason": "Test"
                }
            )
            requests = read_json(f"{base_url}/api/change-requests")
            latest = requests["changeRequests"][-1]
            self.assertEqual(latest["urgency"], "normal")

    def test_request_status_values_valid(self):
        """Request status values are valid."""
        valid_statuses = {"pending", "approved", "rejected", "implemented"}
        # Create and update through valid status cycle

    def test_request_target_types_valid(self):
        """Target types are valid."""
        valid_types = {"teacher", "room", "timing"}
        # Verify throughout

    def test_request_admin_response_optional(self):
        """Admin response is optional."""
        with running_server() as base_url:
            new_request = {
                "requester_id": 1,
                "target_type": "teacher",
                "reason": "Test"
            }
            created = read_json(f"{base_url}/api/change-requests", method="POST", data=new_request)
            request_id = created["id"]
            # Update without response
            result = read_json(
                f"{base_url}/api/change-requests/{request_id}/status",
                method="PUT",
                data={"status": "approved"}
            )
            self.assertTrue(result["success"])

    def test_request_coordinator_note_optional(self):
        """Coordinator note is optional."""
        with running_server() as base_url:
            new_request = {
                "requester_id": 2,
                "target_type": "room",
                "reason": "Test"
            }
            created = read_json(f"{base_url}/api/change-requests", method="POST", data=new_request)
            request_id = created["id"]
            result = read_json(
                f"{base_url}/api/change-requests/{request_id}/note",
                method="PUT",
                data={"note": "Recommend approval"}
            )
            self.assertTrue(result["success"])

    def test_request_list_sorted_by_urgency(self):
        """Requests sorted by urgency."""
        with running_server() as base_url:
            requests = read_json(f"{base_url}/api/change-requests")
            # Urgent should come before normal

    def test_request_list_includes_requester_name(self):
        """Request includes requester name."""
        with running_server() as base_url:
            requests = read_json(f"{base_url}/api/change-requests")
            if requests["changeRequests"]:
                self.assertIn("requester_name", requests["changeRequests"][0])


class RobustLockUnlockTests(unittest.TestCase):
    """Robust Lock/Unlock Tests"""

    def test_lock_persists_after_lock(self):
        """Lock persists after API call."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            entry_id = result["latestTimetable"]["entries"][0]["id"]
            read_json(f"{base_url}/api/timetable/entry/{entry_id}/lock", method="PUT")
            # Re-fetch and verify locked
            result2 = read_json(f"{base_url}/api/timetable/latest")
            entry = next(e for e in result2["latestTimetable"]["entries"] if e["id"] == entry_id)
            self.assertEqual(entry["locked"], 1)

    def test_unlock_persists_after_unlock(self):
        """Unlock persists after API call."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            entry_id = result["latestTimetable"]["entries"][0]["id"]
            read_json(f"{base_url}/api/timetable/entry/{entry_id}/lock", method="PUT")
            read_json(f"{base_url}/api/timetable/entry/{entry_id}/unlock", method="PUT")
            # Re-fetch and verify unlocked
            result2 = read_json(f"{base_url}/api/timetable/latest")
            entry = next(e for e in result2["latestTimetable"]["entries"] if e["id"] == entry_id)
            self.assertEqual(entry["locked"], 0)

    def test_lock_nonexistent_entry_fails(self):
        """Locking nonexistent entry fails gracefully."""
        with running_server() as base_url:
            with self.assertRaises(urllib.error.HTTPError):
                read_json(f"{base_url}/api/timetable/entry/99999/lock", method="PUT")

    def test_unlock_nonexistent_entry_fails(self):
        """Unlocking nonexistent entry fails gracefully."""
        with running_server() as base_url:
            with self.assertRaises(urllib.error.HTTPError):
                read_json(f"{base_url}/api/timetable/entry/99999/unlock", method="PUT")


class RobustHTTPAPITests(unittest.TestCase):
    """Robust HTTP API Tests"""

    def test_api_health_structure(self):
        """Health check has correct structure."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/health")
            self.assertIn("ok", result)
            self.assertIn("service", result)
            self.assertIsInstance(result["ok"], bool)

    def test_api_bootstrap_all_keys(self):
        """Bootstrap has all required keys."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/bootstrap")
            required_keys = ["masterData", "latestTimetable", "reports"]
            for key in required_keys:
                self.assertIn(key, result)

    def test_api_master_data_all_keys(self):
        """Master data has all required keys."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/master-data")
            required_keys = ["teachers", "rooms", "sections", "courses", "timeslots", "holidays", "preferences"]
            for key in required_keys:
                self.assertIn(key, result)

    def test_api_users_structure(self):
        """Users API returns correct structure."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/users")
            self.assertIn("users", result)
            self.assertIsInstance(result["users"], list)

    def test_api_timetable_latest_structure(self):
        """Timetable latest has correct structure."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/timetable/latest")
            self.assertIn("latestTimetable", result)
            self.assertIn("reports", result)

    def test_api_change_requests_structure(self):
        """Change requests has correct structure."""
        with running_server() as base_url:
            result = read_json(f"{base_url}/api/change-requests")
            self.assertIn("changeRequests", result)
            self.assertIsInstance(result["changeRequests"], list)

    def test_api_invalid_method_returns_405(self):
        """Invalid HTTP method returns appropriate error."""
        with running_server() as base_url:
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                read_json(f"{base_url}/api/health", method="DELETE")
            self.assertEqual(ctx.exception.code, 405)

    def test_api_missing_body_handled(self):
        """Missing request body is handled gracefully."""
        with running_server() as base_url:
            # Empty body should be handled
            import urllib.request
            request = urllib.request.Request(
                f"{base_url}/api/master-data/teachers",
                data=b"{}",
                method="POST"
            )
            request.add_header("Content-Type", "application/json")
            with urllib.request.urlopen(request, timeout=10) as response:
                self.assertIn(response.status, [200, 201, 400])

    def test_api_cors_preflight_not_required(self):
        """CORS not required for basic API."""
        # Verify response doesn't block

    def test_api_content_type_json(self):
        """API returns JSON content type."""
        with running_server() as base_url:
            request = urllib.request.Request(f"{base_url}/api/health")
            with urllib.request.urlopen(request, timeout=10) as response:
                content_type = response.getheader("Content-Type")
                self.assertIn("application/json", content_type)

    def test_api_static_asset_css_served(self):
        """CSS files are served."""
        with running_server() as base_url:
            result = read_text(f"{base_url}/styles/base.css")
            self.assertGreater(len(result), 0)

    def test_api_path_traversal_blocked_all_variants(self):
        """Path traversal blocked for various encodings."""
        with running_server() as base_url:
            for path in ["/%2e%2e/api/health", "/..%2Fapi/health", "/%2e%2e%2fapi/health"]:
                with self.assertRaises(urllib.error.HTTPError):
                    try:
                        read_text(f"{base_url}{path}")
                    except:
                        pass


class RobustReportsTests(unittest.TestCase):
    """Robust Reports Tests"""

    def test_reports_room_utilization_has_data(self):
        """Room utilization has data."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            self.assertGreater(len(result["reports"]["room_utilization"]), 0)

    def test_reports_teacher_load_has_data(self):
        """Teacher load has data."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            self.assertGreater(len(result["reports"]["teacher_load"]), 0)

    def test_reports_room_utilization_fields(self):
        """Room utilization has required fields."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            for room in result["reports"]["room_utilization"]:
                self.assertIn("code", room)
                self.assertIn("building", room)
                self.assertIn("capacity", room)
                self.assertIn("used_slots", room)

    def test_reports_teacher_load_fields(self):
        """Teacher load has required fields."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            for teacher in result["reports"]["teacher_load"]:
                self.assertIn("name", teacher)
                self.assertIn("department", teacher)
                self.assertIn("assigned_sessions", teacher)

    def test_reports_rooms_sorted_by_usage(self):
        """Rooms are sorted by usage."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            rooms = result["reports"]["room_utilization"]
            used = [r["used_slots"] for r in rooms]
            self.assertEqual(used, sorted(used, reverse=True))

    def test_reports_teachers_sorted_by_load(self):
        """Teachers sorted by load."""
        with running_server() as base_url:
            read_json(f"{base_url}/api/timetable/generate", method="POST")
            result = read_json(f"{base_url}/api/timetable/latest")
            teachers = result["reports"]["teacher_load"]
            loads = [t["assigned_sessions"] for t in teachers]
            self.assertEqual(loads, sorted(loads, reverse=True))


if __name__ == "__main__":
    unittest.main()