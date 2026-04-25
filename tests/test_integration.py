from __future__ import annotations

import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from contextlib import contextmanager
from http.server import ThreadingHTTPServer
from pathlib import Path

from app.backend import database
from app.backend.repositories.timetable_repository import get_latest_version, get_reports
from app.backend.server import RequestHandler
from app.backend.services.bootstrap_service import get_bootstrap_payload
from app.backend.services.timetable_service import generate_timetable


@contextmanager
def isolated_database():
    original_path = database.DB_PATH
    with tempfile.TemporaryDirectory() as temp_dir:
        database.DB_PATH = Path(temp_dir) / "utos-test.sqlite"
        database.initialize_database()
        try:
            yield
        finally:
            database.DB_PATH = original_path


class IntegrationTests(unittest.TestCase):
    def test_bootstrap_seed_data_counts(self) -> None:
        with isolated_database(), database.connect() as conn:
            payload = get_bootstrap_payload(conn)

        self.assertEqual(len(payload["masterData"]["teachers"]), 5)
        self.assertEqual(len(payload["masterData"]["rooms"]), 5)
        self.assertEqual(len(payload["masterData"]["sections"]), 4)
        self.assertEqual(len(payload["masterData"]["courses"]), 8)
        self.assertIsNone(payload["latestTimetable"])

    def test_generate_persists_latest_version_and_reports(self) -> None:
        with isolated_database(), database.connect() as conn:
            generated = generate_timetable(conn)
            latest = get_latest_version(conn)
            reports = get_reports(conn, generated["versionId"])

        self.assertIsNotNone(latest)
        self.assertEqual(generated["versionId"], latest["id"])
        self.assertEqual(latest["unplaced_count"], 0)
        self.assertEqual(len([entry for entry in latest["entries"] if entry["status"] == "placed"]), 15)
        self.assertEqual(sum(row["used_slots"] for row in reports["room_utilization"]), 15)
        self.assertEqual(sum(row["assigned_sessions"] for row in reports["teacher_load"]), 15)

    def test_generated_timetable_satisfies_seed_hard_constraints(self) -> None:
        with isolated_database(), database.connect() as conn:
            generate_timetable(conn)
            latest = get_latest_version(conn)

        placed = [entry for entry in latest["entries"] if entry["status"] == "placed"]
        teacher_slots = {(entry["teacher_id"], entry["timeslot_id"]) for entry in placed}
        section_slots = {(entry["section_id"], entry["timeslot_id"]) for entry in placed}
        room_slots = {(entry["room_id"], entry["timeslot_id"]) for entry in placed}

        self.assertEqual(len(teacher_slots), len(placed))
        self.assertEqual(len(section_slots), len(placed))
        self.assertEqual(len(room_slots), len(placed))
        self.assertTrue(all(entry["day"] != "Friday" for entry in placed))
        self.assertTrue(all(entry["room_capacity"] >= entry["section_size"] for entry in placed))
        self.assertTrue(
            all(entry["room_code"] == "B-110" for entry in placed if entry["course_code"] in {"DB-210", "ML-330"})
        )

    def test_http_api_static_assets_and_path_traversal_guard(self) -> None:
        with isolated_database():
            server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base_url = f"http://127.0.0.1:{server.server_port}"
            try:
                health = read_json(f"{base_url}/api/health")
                index = read_text(f"{base_url}/")
                generated = read_json(f"{base_url}/api/timetable/generate", method="POST")

                self.assertEqual(health["service"], "utos-backend")
                self.assertIn("Schedule Control Center", index)
                self.assertEqual(generated["latestTimetable"]["unplaced_count"], 0)
                self.assertEqual(generated["latestTimetable"]["score"], 96)

                with self.assertRaises(urllib.error.HTTPError) as error:
                    read_text(f"{base_url}/%2e%2e/backend/schema.sql")
                self.assertEqual(error.exception.code, 404)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


def read_text(url: str, method: str = "GET") -> str:
    request = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(request, timeout=5) as response:
        return response.read().decode("utf-8")


def read_json(url: str, method: str = "GET") -> dict:
    return json.loads(read_text(url, method))


if __name__ == "__main__":
    unittest.main()
