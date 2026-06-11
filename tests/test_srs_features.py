"""Tests for the SRS features: publish, re-optimize with locks, version
comparison, notifications, audit logging, validation, and richer reports."""
from __future__ import annotations

import json
import unittest
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from app.backend import database
from app.backend.server import RequestHandler


@contextmanager
def running_server():
    original_path = database.DB_PATH
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        database.DB_PATH = Path(temp_dir) / "utos-test.sqlite"
        database.initialize_database()
        server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            database.DB_PATH = original_path


def call(base_url: str, path: str, method: str = "GET", data: dict | None = None, actor: int | None = 1):
    headers = {"Content-Type": "application/json"}
    if actor is not None:
        headers["X-User-Id"] = str(actor)
    request = urllib.request.Request(
        base_url + path,
        data=json.dumps(data).encode("utf-8") if data is not None else None,
        method=method,
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def status_of(base_url: str, path: str, method: str = "GET", data: dict | None = None, actor: int | None = 1) -> int:
    try:
        status, _ = call(base_url, path, method, data, actor)
        return status
    except urllib.error.HTTPError as error:
        return error.code


def user_id_for_role(role: str) -> int:
    with database.connect() as conn:
        return conn.execute(
            "SELECT id FROM users WHERE role = ? LIMIT 1", (role,)
        ).fetchone()["id"]


class PublishTests(unittest.TestCase):
    def test_publish_marks_version_and_archives_previous(self):
        with running_server() as base:
            _, first = call(base, "/api/timetable/generate", "POST")
            _, second = call(base, "/api/timetable/generate", "POST")
            call(base, f"/api/timetable/{first['versionId']}/publish", "PUT")
            call(base, f"/api/timetable/{second['versionId']}/publish", "PUT")
            _, versions = call(base, "/api/timetable/versions")
            by_id = {v["id"]: v for v in versions["versions"]}
            self.assertEqual(by_id[first["versionId"]]["status"], "archived")
            self.assertEqual(by_id[second["versionId"]]["status"], "published")

    def test_publish_repeated_requests_never_crash_server(self):
        """Regression test for the historical publish crash (empty reply)."""
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            for _ in range(5):
                status, payload = call(base, f"/api/timetable/{generated['versionId']}/publish", "PUT")
                self.assertEqual(status, 200)
                self.assertTrue(payload["success"])
            status, _ = call(base, "/api/health")
            self.assertEqual(status, 200)

    def test_publish_missing_version_returns_404(self):
        with running_server() as base:
            self.assertEqual(status_of(base, "/api/timetable/9999/publish", "PUT"), 404)

    def test_publish_notifies_teachers_and_students(self):
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            _, result = call(base, f"/api/timetable/{generated['versionId']}/publish", "PUT")
            self.assertGreater(result["notified"], 0)
            with database.connect() as conn:
                teacher_user = conn.execute(
                    "SELECT id FROM users WHERE role = 'teacher' LIMIT 1"
                ).fetchone()
            _, notifications = call(base, f"/api/notifications?user_id={teacher_user['id']}")
            self.assertTrue(any(n["category"] == "publish" for n in notifications["notifications"]))


class ReoptimizeTests(unittest.TestCase):
    def test_locked_entries_survive_reoptimization(self):
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            placed = [e for e in generated["latestTimetable"]["entries"] if e["status"] == "placed"]
            target = placed[0]
            call(base, f"/api/timetable/entry/{target['id']}/lock", "PUT")

            _, repaired = call(base, "/api/timetable/reoptimize", "POST")
            kept = [
                e for e in repaired["latestTimetable"]["entries"]
                if e["event_uid"] == target["event_uid"]
            ]
            self.assertEqual(len(kept), 1)
            self.assertEqual(kept[0]["room_id"], target["room_id"])
            self.assertEqual(kept[0]["timeslot_id"], target["timeslot_id"])
            self.assertEqual(kept[0]["locked"], 1)
            self.assertGreaterEqual(repaired["disruption"]["locked_preserved"], 1)

    def test_reoptimize_reports_disruption_summary(self):
        with running_server() as base:
            call(base, "/api/timetable/generate", "POST")
            _, repaired = call(base, "/api/timetable/reoptimize", "POST")
            for key in ("changed", "added", "removed", "unchanged", "locked_preserved"):
                self.assertIn(key, repaired["disruption"])


class VersionCompareTests(unittest.TestCase):
    def test_compare_same_version_reports_no_changes(self):
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            vid = generated["versionId"]
            _, diff = call(base, f"/api/timetable/compare?a={vid}&b={vid}")
            self.assertEqual(diff["totals"], {"added": 0, "removed": 0, "changed": 0})

    def test_compare_missing_version_returns_404(self):
        with running_server() as base:
            call(base, "/api/timetable/generate", "POST")
            self.assertEqual(status_of(base, "/api/timetable/compare?a=1&b=999"), 404)


class NotificationTests(unittest.TestCase):
    def test_change_request_decision_notifies_requester(self):
        with running_server() as base:
            with database.connect() as conn:
                requester = conn.execute(
                    "SELECT id FROM users WHERE role = 'teacher' LIMIT 1"
                ).fetchone()["id"]
            _, created = call(base, "/api/change-requests", "POST", {
                "requester_id": requester,
                "target_type": "timing",
                "reason": "Clash with research meeting",
            })
            call(base, f"/api/change-requests/{created['id']}/status", "PUT",
                 {"status": "approved", "admin_response": "Approved for next run"})
            _, payload = call(base, f"/api/notifications?user_id={requester}")
            titles = [n["title"] for n in payload["notifications"]]
            self.assertTrue(any("approved" in t.lower() for t in titles))

    def test_mark_notification_read_decrements_unread(self):
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            call(base, f"/api/timetable/{generated['versionId']}/publish", "PUT")
            with database.connect() as conn:
                student = conn.execute(
                    "SELECT id FROM users WHERE role = 'student' LIMIT 1"
                ).fetchone()["id"]
            _, before = call(base, f"/api/notifications?user_id={student}")
            self.assertGreater(before["unread"], 0)
            call(base, f"/api/notifications/{before['notifications'][0]['id']}/read", "PUT")
            _, after = call(base, f"/api/notifications?user_id={student}")
            self.assertEqual(after["unread"], before["unread"] - 1)


class AuditLogTests(unittest.TestCase):
    def test_state_changes_are_audited_with_actor(self):
        with running_server() as base:
            call(base, "/api/master-data/teachers", "POST",
                 {"name": "Dr. Audit", "department": "CS"})
            _, generated = call(base, "/api/timetable/generate", "POST")
            call(base, f"/api/timetable/{generated['versionId']}/publish", "PUT")
            _, log = call(base, "/api/audit-log")
            actions = {(item["action"], item["entity_type"]) for item in log["auditLog"]}
            self.assertIn(("create", "teacher"), actions)
            self.assertIn(("generate", "timetable_version"), actions)
            self.assertIn(("publish", "timetable_version"), actions)
            self.assertTrue(all(item["actor_id"] == 1 for item in log["auditLog"]))


class ValidationTests(unittest.TestCase):
    def test_course_requires_all_fields(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/courses", "POST", {"code": "X-1"}), 400)

    def test_preference_weight_range_enforced(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/preferences/1", "PUT",
                          {"enabled": True, "weight": 11}), 400)
            self.assertEqual(
                status_of(base, "/api/master-data/preferences/1", "PUT",
                          {"enabled": True, "weight": 5}), 200)

    def test_used_timeslot_delete_conflicts(self):
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            used_slot = next(e["timeslot_id"] for e in generated["latestTimetable"]["entries"]
                             if e["status"] == "placed")
            self.assertEqual(
                status_of(base, f"/api/master-data/timeslots/{used_slot}", "DELETE"), 409)

    def test_get_only_paths_reject_other_methods(self):
        with running_server() as base:
            self.assertEqual(status_of(base, "/api/health", "POST"), 405)
            self.assertEqual(status_of(base, "/api/bootstrap", "DELETE"), 405)

    def test_update_missing_teacher_returns_404(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/teachers/9999", "PUT",
                          {"name": "Ghost", "department": "CS"}), 404)


class ReportTests(unittest.TestCase):
    def test_reports_include_utilization_and_gaps(self):
        with running_server() as base:
            call(base, "/api/timetable/generate", "POST")
            _, latest = call(base, "/api/timetable/latest")
            reports = latest["reports"]
            self.assertIn("section_gaps", reports)
            self.assertTrue(all("utilization_pct" in room for room in reports["room_utilization"]))
            self.assertTrue(all("busiest_day_load" in t for t in reports["teacher_load"]))


class AvailabilityTests(unittest.TestCase):
    def test_availability_round_trip(self):
        with running_server() as base:
            call(base, "/api/teacher-availability/1", "PUT", {"unavailable_slot_ids": [1, 2, 3]})
            _, payload = call(base, "/api/teacher-availability?teacher_id=1")
            unavailable = {a["timeslot_id"] for a in payload["availability"] if not a["is_available"]}
            self.assertEqual(unavailable, {1, 2, 3})


class PublishedViewTests(unittest.TestCase):
    def test_bootstrap_exposes_published_timetable_only_after_publish(self):
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            _, before = call(base, "/api/bootstrap")
            self.assertIsNone(before["publishedTimetable"])

            call(base, f"/api/timetable/{generated['versionId']}/publish", "PUT")
            _, after = call(base, "/api/bootstrap")
            self.assertIsNotNone(after["publishedTimetable"])
            self.assertEqual(after["publishedTimetable"]["id"], generated["versionId"])
            self.assertEqual(after["publishedTimetable"]["status"], "published")

    def test_published_stays_on_previous_version_while_new_draft_exists(self):
        with running_server() as base:
            _, first = call(base, "/api/timetable/generate", "POST")
            call(base, f"/api/timetable/{first['versionId']}/publish", "PUT")
            _, second = call(base, "/api/timetable/generate", "POST")
            _, payload = call(base, "/api/bootstrap")
            self.assertEqual(payload["publishedTimetable"]["id"], first["versionId"])
            self.assertEqual(payload["latestTimetable"]["id"], second["versionId"])


class RoleEnforcementTests(unittest.TestCase):
    def test_student_cannot_generate_or_edit_master_data(self):
        with running_server() as base:
            student = user_id_for_role("student")
            self.assertEqual(
                status_of(base, "/api/timetable/generate", "POST", actor=student), 403)
            self.assertEqual(
                status_of(base, "/api/master-data/teachers", "POST",
                          {"name": "X", "department": "Y"}, actor=student), 403)
            self.assertEqual(
                status_of(base, "/api/change-requests", "POST",
                          {"requester_id": student, "target_type": "timing", "reason": "x"},
                          actor=student), 403)

    def test_teacher_can_submit_change_request_but_not_decide(self):
        with running_server() as base:
            teacher = user_id_for_role("teacher")
            status, created = call(base, "/api/change-requests", "POST", {
                "requester_id": teacher, "target_type": "room", "reason": "Projector broken",
            }, actor=teacher)
            self.assertEqual(status, 201)
            self.assertEqual(
                status_of(base, f"/api/change-requests/{created['id']}/status", "PUT",
                          {"status": "approved"}, actor=teacher), 403)

    def test_requests_without_identity_header_stay_trusted(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/teachers", "POST",
                          {"name": "Header-less", "department": "CS"}, actor=None), 201)


class RoomDeleteGuardTests(unittest.TestCase):
    def test_room_used_by_timetable_cannot_be_deleted(self):
        with running_server() as base:
            _, generated = call(base, "/api/timetable/generate", "POST")
            used_room = next(e["room_id"] for e in generated["latestTimetable"]["entries"]
                             if e["status"] == "placed")
            self.assertEqual(
                status_of(base, f"/api/master-data/rooms/{used_room}", "DELETE"), 409)

    def test_unused_room_can_be_deleted(self):
        with running_server() as base:
            _, created = call(base, "/api/master-data/rooms", "POST",
                              {"code": "TMP-1", "building": "T", "capacity": 10})
            self.assertEqual(
                status_of(base, f"/api/master-data/rooms/{created['id']}", "DELETE"), 200)


class RoomTypeMatchingTests(unittest.TestCase):
    def test_required_room_type_is_honored_for_all_types(self):
        with running_server() as base:
            call(base, "/api/master-data/courses", "POST", {
                "code": "AUD-101", "title": "Auditorium Lecture",
                "teacher_id": 3, "section_id": 1,
                "weekly_sessions": 1, "required_room_type": "auditorium",
            })
            _, generated = call(base, "/api/timetable/generate", "POST")
            with database.connect() as conn:
                room_types = {row["id"]: row["room_type"]
                              for row in conn.execute("SELECT id, room_type FROM rooms")}
            aud_entries = [e for e in generated["latestTimetable"]["entries"]
                           if e["course_code"] == "AUD-101"]
            self.assertTrue(aud_entries)
            for entry in aud_entries:
                if entry["status"] == "placed":
                    self.assertEqual(room_types[entry["room_id"]], "auditorium",
                                     "auditorium-required course placed in wrong room type")


class InputValidationTests(unittest.TestCase):
    def test_invalid_room_type_rejected(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/rooms", "POST",
                          {"code": "RX", "building": "B", "capacity": 30, "room_type": "castle"}), 400)

    def test_holiday_must_be_a_weekday(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/holidays", "POST",
                          {"name": "X", "day": "Sunday"}), 400)

    def test_timeslot_time_format_and_order(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/timeslots", "POST",
                          {"day": "Monday", "start_time": "9am", "end_time": "10am", "sort_order": 99}), 400)
            self.assertEqual(
                status_of(base, "/api/master-data/timeslots", "POST",
                          {"day": "Monday", "start_time": "15:00", "end_time": "09:00", "sort_order": 99}), 400)

    def test_oversized_string_rejected(self):
        with running_server() as base:
            self.assertEqual(
                status_of(base, "/api/master-data/teachers", "POST",
                          {"name": "A" * 5000, "department": "CS"}), 400)

    def test_malformed_json_does_not_crash_server(self):
        with running_server() as base:
            req = urllib.request.Request(
                base + "/api/master-data/teachers", data=b"{ broken",
                method="POST", headers={"Content-Type": "application/json", "X-User-Id": "1"})
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    code = resp.status
            except urllib.error.HTTPError as err:
                code = err.code
            self.assertEqual(code, 400)
            # Server must still respond afterwards.
            self.assertEqual(status_of(base, "/api/health"), 200)


class UnplacedReasonTests(unittest.TestCase):
    def test_capacity_infeasible_session_reports_reason(self):
        with running_server() as base:
            # A lab section larger than any lab room -> structural infeasibility.
            _, room = call(base, "/api/master-data/rooms", "POST",
                           {"code": "TINY-LAB", "building": "T", "capacity": 10, "room_type": "lab"})
            _, teacher = call(base, "/api/master-data/teachers", "POST",
                              {"name": "Lab Tutor", "department": "CS"})
            _, section = call(base, "/api/master-data/sections", "POST",
                              {"name": "HUGE-LAB-SEC", "department": "CS", "size": 200})
            call(base, "/api/master-data/courses", "POST", {
                "code": "BIGLAB", "title": "Overflowing Lab",
                "teacher_id": teacher["id"], "section_id": section["id"],
                "weekly_sessions": 1, "required_room_type": "lab"})
            _, gen = call(base, "/api/timetable/generate", "POST")
            unplaced = [e for e in gen["latestTimetable"]["entries"]
                        if e["status"] == "unplaced" and e["course_code"] == "BIGLAB"]
            self.assertEqual(len(unplaced), 1)
            self.assertIn("large enough", unplaced[0]["reason"].lower())


if __name__ == "__main__":
    unittest.main()
