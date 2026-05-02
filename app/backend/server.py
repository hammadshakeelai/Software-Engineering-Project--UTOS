from __future__ import annotations

import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.backend.database import connect, initialize_database
from app.backend.repositories.master_data import (
    get_master_data,
    insert_teacher,
    update_teacher,
    delete_teacher,
    insert_room,
    update_room,
    delete_room,
    insert_section,
    update_section,
    delete_section,
    insert_course,
    update_course,
    delete_course,
)
from app.backend.repositories.timetable_repository import (
    get_latest_version,
    get_reports,
    lock_entry,
    unlock_entry,
    publish_version,
    insert_change_request,
    get_change_requests,
    update_change_request_status,
    add_coordinator_note,
)
from app.backend.services.bootstrap_service import get_bootstrap_payload
from app.backend.services.timetable_service import generate_timetable


HOST = "127.0.0.1"
PORT = int(os.environ.get("UTOS_PORT", "8000"))
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "UTOS/0.1"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._json({"ok": True, "service": "utos-backend"})
            return
        if parsed.path == "/api/bootstrap":
            with connect() as conn:
                self._json(get_bootstrap_payload(conn))
            return
        if parsed.path == "/api/master-data":
            with connect() as conn:
                self._json(get_master_data(conn))
            return
        if parsed.path == "/api/users":
            with connect() as conn:
                self._json({"users": get_master_data(conn)["users"]})
            return
        if parsed.path == "/api/timetable/latest":
            with connect() as conn:
                latest = get_latest_version(conn)
                self._json({"latestTimetable": latest, "reports": get_reports(conn, latest["id"] if latest else None)})
            return
        if parsed.path == "/api/change-requests":
            with connect() as conn:
                self._json({"changeRequests": get_change_requests(conn)})
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/timetable/generate":
            with connect() as conn:
                self._json(generate_timetable(conn))
            return

        body = self._read_body()

        if parsed.path == "/api/master-data/teachers":
            with connect() as conn:
                teacher_id = insert_teacher(conn, body["name"], body["department"], body.get("max_daily_load", 4))
                self._json({"id": teacher_id, "success": True}, status=201)
            return
        if parsed.path == "/api/master-data/rooms":
            with connect() as conn:
                room_id = insert_room(conn, body["code"], body["building"], body["floor"], body["capacity"], body["room_type"], body.get("features", ""))
                self._json({"id": room_id, "success": True}, status=201)
            return
        if parsed.path == "/api/master-data/sections":
            with connect() as conn:
                section_id = insert_section(conn, body["name"], body["department"], body["size"])
                self._json({"id": section_id, "success": True}, status=201)
            return
        if parsed.path == "/api/master-data/courses":
            with connect() as conn:
                course_id = insert_course(conn, body["code"], body["title"], body["teacher_id"], body["section_id"], body["weekly_sessions"], body["required_room_type"])
                self._json({"id": course_id, "success": True}, status=201)
            return
        if parsed.path == "/api/change-requests":
            with connect() as conn:
                request_id = insert_change_request(
                    conn,
                    body["requester_id"],
                    body["target_type"],
                    body.get("target_id", 0),
                    body["reason"],
                    body.get("urgency", "normal"),
                    body.get("preferred_alternative", ""),
                )
                self._json({"id": request_id, "success": True}, status=201)
            return

        self._json({"error": "Not found"}, status=404)

    def do_PUT(self) -> None:
        try:
            parsed = urlparse(self.path)
            path_parts = parsed.path.split("/")

            if "/timetable/" in parsed.path and "/publish" in parsed.path:
                version_id = int(path_parts[3])
                with connect() as conn:
                    publish_version(conn, version_id)
                self._json({"success": True})
                return

            if "/entry/" in parsed.path and "/lock" in parsed.path:
                entry_id = int(path_parts[4])
                with connect() as conn:
                    lock_entry(conn, entry_id)
                self._json({"success": True})
                return

            if "/entry/" in parsed.path and "/unlock" in parsed.path:
                entry_id = int(path_parts[4])
                with connect() as conn:
                    unlock_entry(conn, entry_id)
                self._json({"success": True})
                return

            body = self._read_body()

            if len(path_parts) >= 5 and path_parts[3] == "teachers":
                teacher_id = int(path_parts[4])
                with connect() as conn:
                    update_teacher(conn, teacher_id, body["name"], body["department"], body.get("max_daily_load", 4))
                self._json({"success": True})
                return

            if len(path_parts) >= 5 and path_parts[3] == "rooms":
                room_id = int(path_parts[4])
                with connect() as conn:
                    update_room(conn, room_id, body["code"], body["building"], body["floor"], body["capacity"], body["room_type"], body.get("features", ""))
                self._json({"success": True})
                return

            if len(path_parts) >= 5 and path_parts[3] == "sections":
                section_id = int(path_parts[4])
                with connect() as conn:
                    update_section(conn, section_id, body["name"], body["department"], body["size"])
                self._json({"success": True})
                return

            if len(path_parts) >= 5 and path_parts[3] == "courses":
                course_id = int(path_parts[4])
                with connect() as conn:
                    update_course(conn, course_id, body["code"], body["title"], body["teacher_id"], body["section_id"], body["weekly_sessions"], body["required_room_type"])
                self._json({"success": True})
                return

            if "/change-requests/" in parsed.path and "/status" in parsed.path:
                request_id = int(path_parts[3])
                with connect() as conn:
                    update_change_request_status(conn, request_id, body["status"], body.get("admin_response", ""))
                self._json({"success": True})
                return

            if "/change-requests/" in parsed.path and "/note" in parsed.path:
                request_id = int(path_parts[3])
                with connect() as conn:
                    add_coordinator_note(conn, request_id, body["note"])
                self._json({"success": True})
                return

            self._json({"error": "Not found"}, status=404)
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                self._json({"error": f"Internal error: {str(e)}"}, status=500)
            except:
                pass

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        path_parts = parsed.path.split("/")

        if len(path_parts) >= 5 and path_parts[3] == "teachers" and path_parts[4].isdigit():
            teacher_id = int(path_parts[4])
            with connect() as conn:
                delete_teacher(conn, teacher_id)
                self._json({"success": True})
            return
        if len(path_parts) >= 5 and path_parts[3] == "rooms" and path_parts[4].isdigit():
            room_id = int(path_parts[4])
            with connect() as conn:
                delete_room(conn, room_id)
                self._json({"success": True})
            return
        if len(path_parts) >= 5 and path_parts[3] == "sections" and path_parts[4].isdigit():
            section_id = int(path_parts[4])
            with connect() as conn:
                delete_section(conn, section_id)
                self._json({"success": True})
            return
        if len(path_parts) >= 5 and path_parts[3] == "courses" and path_parts[4].isdigit():
            course_id = int(path_parts[4])
            with connect() as conn:
                delete_course(conn, course_id)
                self._json({"success": True})
            return

        self._json({"error": "Not found"}, status=404)

    def _read_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        return json.loads(body)

    def _serve_static(self, raw_path: str) -> None:
        path = unquote(raw_path)
        if path in {"", "/"}:
            path = "/index.html"
        target = (FRONTEND_DIR / path.lstrip("/")).resolve()
        frontend_root = FRONTEND_DIR.resolve()
        if not target.is_file() or not target.is_relative_to(frontend_root):
            self._json({"error": "Not found"}, status=404)
            return
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))


def main() -> None:
    initialize_database()
    server = ThreadingHTTPServer((HOST, PORT), RequestHandler)
    print(f"UTOS running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UTOS server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
