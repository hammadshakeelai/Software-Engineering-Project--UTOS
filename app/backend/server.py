from __future__ import annotations

import json
import mimetypes
import os
import re
import sqlite3
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.backend.database import connect, initialize_database
from app.backend.repositories.master_data import (
    delete_course,
    delete_holiday,
    delete_room,
    delete_section,
    delete_teacher,
    delete_timeslot,
    get_master_data,
    get_teacher_availability,
    insert_course,
    insert_holiday,
    insert_room,
    insert_section,
    insert_teacher,
    insert_timeslot,
    set_teacher_availability,
    update_course,
    update_preference,
    update_room,
    update_section,
    update_teacher,
)
from app.backend.repositories.system_repository import (
    get_audit_log,
    get_notifications,
    log_audit,
    mark_notification_read,
    notify_roles,
    notify_user,
)
from app.backend.repositories.timetable_repository import (
    add_coordinator_note,
    compare_versions,
    get_change_request,
    get_change_requests,
    get_latest_version,
    get_reports,
    get_version,
    get_versions,
    insert_change_request,
    lock_entry,
    publish_version,
    unlock_entry,
    update_change_request_status,
)
from app.backend.services.bootstrap_service import get_bootstrap_payload
from app.backend.services.timetable_service import generate_timetable, reoptimize_timetable


HOST = "127.0.0.1"
PORT = int(os.environ.get("UTOS_PORT", "8000"))
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

# API paths that only support GET; other methods on them return 405.
GET_ONLY_PATHS = {
    "/api/health",
    "/api/bootstrap",
    "/api/master-data",
    "/api/users",
    "/api/timetable/latest",
    "/api/timetable/versions",
    "/api/timetable/compare",
    "/api/notifications",
    "/api/audit-log",
}


ADMIN_ROLES = {"administrator", "system_admin"}
REVIEWER_ROLES = ADMIN_ROLES | {"coordinator"}
REQUESTER_ROLES = REVIEWER_ROLES | {"teacher"}

# The frontend grid renders Monday-Friday; other days would silently vanish.
VALID_DAYS = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}
VALID_ROOM_TYPES = {"lecture", "lab", "auditorium"}
TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class ApiError(Exception):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "UTOS/0.2"

    # ------------------------------------------------------------------ GET

    def do_GET(self) -> None:
        self._dispatch(self._route_get)

    def _route_get(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        parts = [part for part in path.split("/") if part]

        if path == "/api/health":
            self._json({"ok": True, "service": "utos-backend"})
        elif path == "/api/bootstrap":
            with connect() as conn:
                self._json(get_bootstrap_payload(conn))
        elif path == "/api/master-data":
            with connect() as conn:
                self._json(get_master_data(conn))
        elif path == "/api/users":
            with connect() as conn:
                self._json({"users": get_master_data(conn)["users"]})
        elif path == "/api/timetable/latest":
            with connect() as conn:
                latest = get_latest_version(conn)
                self._json({"latestTimetable": latest, "reports": get_reports(conn, latest["id"] if latest else None)})
        elif path == "/api/timetable/versions":
            with connect() as conn:
                self._json({"versions": get_versions(conn)})
        elif path == "/api/timetable/compare":
            version_a = self._int_param(query, "a")
            version_b = self._int_param(query, "b")
            with connect() as conn:
                diff = compare_versions(conn, version_a, version_b)
            if diff is None:
                raise ApiError(404, "One or both versions do not exist")
            self._json(diff)
        elif len(parts) == 4 and parts[:3] == ["api", "timetable", "version"] and parts[3].isdigit():
            with connect() as conn:
                version = get_version(conn, int(parts[3]))
            if version is None:
                raise ApiError(404, "Version not found")
            self._json(version)
        elif path == "/api/change-requests":
            with connect() as conn:
                self._json({"changeRequests": get_change_requests(conn)})
        elif path == "/api/notifications":
            user_id = self._int_param(query, "user_id")
            with connect() as conn:
                items = get_notifications(conn, user_id)
            self._json({"notifications": items, "unread": sum(1 for item in items if not item["read"])})
        elif path == "/api/audit-log":
            with connect() as conn:
                self._json({"auditLog": get_audit_log(conn)})
        elif path == "/api/teacher-availability":
            teacher_id = self._int_param(query, "teacher_id")
            with connect() as conn:
                self._json({"availability": get_teacher_availability(conn, teacher_id)})
        elif path.startswith("/api/"):
            raise ApiError(404, "Not found")
        else:
            self._serve_static(path)

    # ----------------------------------------------------------------- POST

    def do_POST(self) -> None:
        self._dispatch(self._route_post)

    def _route_post(self) -> None:
        path = urlparse(self.path).path
        self._reject_get_only(path)

        if path.startswith(("/api/timetable/", "/api/master-data/")):
            self._require_role(ADMIN_ROLES)
        elif path == "/api/change-requests":
            self._require_role(REQUESTER_ROLES)

        if path == "/api/timetable/generate":
            with connect() as conn:
                payload = generate_timetable(conn)
                log_audit(conn, self._actor_id(), "generate", "timetable_version", payload["versionId"])
                notify_roles(conn, ["coordinator"], "generation",
                             "Timetable draft generated",
                             f"Version {payload['versionId']} is ready for review.")
                conn.commit()
            self._json(payload)
            return
        if path == "/api/timetable/reoptimize":
            with connect() as conn:
                payload = reoptimize_timetable(conn)
                log_audit(conn, self._actor_id(), "reoptimize", "timetable_version", payload["versionId"],
                          new_value=payload.get("disruption", {}))
                notify_roles(conn, ["coordinator"], "generation",
                             "Timetable re-optimized",
                             f"Version {payload['versionId']} repaired with minimum disruption.")
                conn.commit()
            self._json(payload)
            return

        body = self._read_body()

        if path == "/api/master-data/teachers":
            name = self._require_str(body, "name")
            department = self._require_str(body, "department")
            max_daily_load = self._require_int(body, "max_daily_load", default=4, minimum=1)
            with connect() as conn:
                teacher_id = insert_teacher(conn, name, department, max_daily_load)
                log_audit(conn, self._actor_id(), "create", "teacher", teacher_id, new_value=body)
                conn.commit()
            self._json({"id": teacher_id, "success": True}, status=201)
        elif path == "/api/master-data/rooms":
            code = self._require_str(body, "code")
            building = self._require_str(body, "building")
            capacity = self._require_int(body, "capacity", minimum=1)
            floor = self._require_int(body, "floor", default=0, minimum=0)
            room_type = self._require_room_type(body, "room_type")
            with connect() as conn:
                room_id = insert_room(conn, code, building, floor, capacity, room_type, str(body.get("features", "")))
                log_audit(conn, self._actor_id(), "create", "room", room_id, new_value=body)
                conn.commit()
            self._json({"id": room_id, "success": True}, status=201)
        elif path == "/api/master-data/sections":
            name = self._require_str(body, "name")
            department = self._require_str(body, "department")
            size = self._require_int(body, "size", minimum=1)
            with connect() as conn:
                section_id = insert_section(conn, name, department, size)
                log_audit(conn, self._actor_id(), "create", "section", section_id, new_value=body)
                conn.commit()
            self._json({"id": section_id, "success": True}, status=201)
        elif path == "/api/master-data/courses":
            code = self._require_str(body, "code")
            title = self._require_str(body, "title")
            teacher_id = self._require_int(body, "teacher_id", minimum=1)
            section_id = self._require_int(body, "section_id", minimum=1)
            weekly_sessions = self._require_int(body, "weekly_sessions", default=2, minimum=1)
            room_type = self._require_room_type(body, "required_room_type")
            with connect() as conn:
                course_id = insert_course(conn, code, title, teacher_id, section_id, weekly_sessions, room_type)
                log_audit(conn, self._actor_id(), "create", "course", course_id, new_value=body)
                conn.commit()
            self._json({"id": course_id, "success": True}, status=201)
        elif path == "/api/master-data/holidays":
            name = self._require_str(body, "name")
            day = self._require_day(body)
            with connect() as conn:
                holiday_id = insert_holiday(conn, name, day)
                log_audit(conn, self._actor_id(), "create", "holiday", holiday_id, new_value=body)
                conn.commit()
            self._json({"id": holiday_id, "success": True}, status=201)
        elif path == "/api/master-data/timeslots":
            day = self._require_day(body)
            start_time = self._require_time(body, "start_time")
            end_time = self._require_time(body, "end_time")
            if end_time <= start_time:
                raise ApiError(400, "end_time must be after start_time")
            sort_order = self._require_int(body, "sort_order", minimum=1)
            with connect() as conn:
                timeslot_id = insert_timeslot(
                    conn, day, start_time, end_time, sort_order,
                    self._require_int(body, "is_morning", default=0, minimum=0),
                    self._require_int(body, "is_last_slot", default=0, minimum=0),
                )
                log_audit(conn, self._actor_id(), "create", "timeslot", timeslot_id, new_value=body)
                conn.commit()
            self._json({"id": timeslot_id, "success": True}, status=201)
        elif path == "/api/change-requests":
            requester_id = self._require_int(body, "requester_id", minimum=1)
            target_type = self._require_str(body, "target_type")
            reason = self._require_str(body, "reason")
            with connect() as conn:
                request_id = insert_change_request(
                    conn,
                    requester_id,
                    target_type,
                    int(body.get("target_id") or 0),
                    reason,
                    str(body.get("urgency", "normal")),
                    str(body.get("preferred_alternative", "")),
                )
                log_audit(conn, requester_id, "create", "change_request", request_id, new_value=body)
                notify_roles(conn, ["administrator", "coordinator"], "change_request",
                             "New change request",
                             f"Request #{request_id}: {reason[:120]}")
                conn.commit()
            self._json({"id": request_id, "success": True}, status=201)
        else:
            raise ApiError(404, "Not found")

    # ------------------------------------------------------------------ PUT

    def do_PUT(self) -> None:
        self._dispatch(self._route_put)

    def _route_put(self) -> None:
        path = urlparse(self.path).path
        self._reject_get_only(path)
        parts = [part for part in path.split("/") if part]

        if path.startswith(("/api/timetable/", "/api/master-data/", "/api/teacher-availability/")):
            self._require_role(ADMIN_ROLES)

        if len(parts) == 4 and parts[:2] == ["api", "timetable"] and parts[2].isdigit() and parts[3] == "publish":
            version_id = int(parts[2])
            with connect() as conn:
                if not publish_version(conn, version_id):
                    raise ApiError(404, "Version not found")
                log_audit(conn, self._actor_id(), "publish", "timetable_version", version_id)
                notified = notify_roles(conn, ["teacher", "student", "coordinator"], "publish",
                                        "Timetable published",
                                        f"Version {version_id} is now the official timetable.")
                conn.commit()
            self._json({"success": True, "versionId": version_id, "notified": notified})
            return

        if len(parts) == 5 and parts[:3] == ["api", "timetable", "entry"] and parts[3].isdigit() and parts[4] in {"lock", "unlock"}:
            entry_id = int(parts[3])
            action = parts[4]
            with connect() as conn:
                changed = lock_entry(conn, entry_id) if action == "lock" else unlock_entry(conn, entry_id)
                if not changed:
                    raise ApiError(404, "Timetable entry not found")
                log_audit(conn, self._actor_id(), action, "timetable_entry", entry_id)
                conn.commit()
            self._json({"success": True})
            return

        if len(parts) == 4 and parts[:2] == ["api", "notifications"] and parts[2].isdigit() and parts[3] == "read":
            with connect() as conn:
                if not mark_notification_read(conn, int(parts[2])):
                    raise ApiError(404, "Notification not found")
            self._json({"success": True})
            return

        body = self._read_body()

        if len(parts) == 4 and parts[:2] == ["api", "master-data"] and parts[3].isdigit():
            self._update_master_data(parts[2], int(parts[3]), body)
            return

        if len(parts) == 3 and parts[:2] == ["api", "teacher-availability"] and parts[2].isdigit():
            teacher_id = int(parts[2])
            unavailable = body.get("unavailable_slot_ids")
            if not isinstance(unavailable, list):
                raise ApiError(400, "unavailable_slot_ids must be a list of timeslot ids")
            with connect() as conn:
                set_teacher_availability(conn, teacher_id, [int(slot) for slot in unavailable])
                log_audit(conn, self._actor_id(), "update", "teacher_availability", teacher_id, new_value=body)
                conn.commit()
            self._json({"success": True})
            return

        if len(parts) == 4 and parts[:2] == ["api", "change-requests"] and parts[2].isdigit():
            request_id = int(parts[2])
            self._require_role(ADMIN_ROLES if parts[3] == "status" else REVIEWER_ROLES)
            with connect() as conn:
                request = get_change_request(conn, request_id)
                if request is None:
                    raise ApiError(404, "Change request not found")
                if parts[3] == "status":
                    status = self._require_str(body, "status")
                    if status not in {"pending", "approved", "rejected", "implemented"}:
                        raise ApiError(400, "Invalid status")
                    update_change_request_status(conn, request_id, status, str(body.get("admin_response", "")))
                    log_audit(conn, self._actor_id(), status, "change_request", request_id,
                              old_value=request["status"], new_value=status)
                    if request["requester_id"]:
                        notify_user(conn, request["requester_id"], "change_request",
                                    f"Change request {status}",
                                    str(body.get("admin_response", "")) or f"Your request #{request_id} was {status}.")
                    conn.commit()
                elif parts[3] == "note":
                    add_coordinator_note(conn, request_id, self._require_str(body, "note"))
                    log_audit(conn, self._actor_id(), "note", "change_request", request_id, new_value=body)
                    conn.commit()
                else:
                    raise ApiError(404, "Not found")
            self._json({"success": True})
            return

        raise ApiError(404, "Not found")

    def _update_master_data(self, category: str, item_id: int, body: dict) -> None:
        with connect() as conn:
            if category == "teachers":
                self._ensure_exists(conn, "teachers", item_id)
                update_teacher(conn, item_id, self._require_str(body, "name"),
                               self._require_str(body, "department"),
                               self._require_int(body, "max_daily_load", default=4, minimum=1))
            elif category == "rooms":
                self._ensure_exists(conn, "rooms", item_id)
                update_room(conn, item_id, self._require_str(body, "code"),
                            self._require_str(body, "building"),
                            self._require_int(body, "floor", default=0, minimum=0),
                            self._require_int(body, "capacity", minimum=1),
                            self._require_room_type(body, "room_type"), str(body.get("features", "")))
            elif category == "sections":
                self._ensure_exists(conn, "sections", item_id)
                update_section(conn, item_id, self._require_str(body, "name"),
                               self._require_str(body, "department"),
                               self._require_int(body, "size", minimum=1))
            elif category == "courses":
                self._ensure_exists(conn, "courses", item_id)
                update_course(conn, item_id, self._require_str(body, "code"),
                              self._require_str(body, "title"),
                              self._require_int(body, "teacher_id", minimum=1),
                              self._require_int(body, "section_id", minimum=1),
                              self._require_int(body, "weekly_sessions", default=2, minimum=1),
                              self._require_room_type(body, "required_room_type"))
            elif category == "preferences":
                enabled = 1 if body.get("enabled") else 0
                weight = self._require_int(body, "weight", minimum=0)
                if weight > 10:
                    raise ApiError(400, "Preference weight must be between 0 and 10")
                if not update_preference(conn, item_id, enabled, weight):
                    raise ApiError(404, "Preference not found")
            else:
                raise ApiError(404, "Not found")
            log_audit(conn, self._actor_id(), "update", category.rstrip("s"), item_id, new_value=body)
            conn.commit()
        self._json({"success": True})

    # --------------------------------------------------------------- DELETE

    def do_DELETE(self) -> None:
        self._dispatch(self._route_delete)

    def _route_delete(self) -> None:
        path = urlparse(self.path).path
        self._reject_get_only(path)
        self._require_role(ADMIN_ROLES)
        parts = [part for part in path.split("/") if part]

        if len(parts) != 4 or parts[:2] != ["api", "master-data"] or not parts[3].isdigit():
            raise ApiError(404, "Not found")

        category, item_id = parts[2], int(parts[3])
        deleters = {
            "teachers": delete_teacher,
            "rooms": delete_room,
            "sections": delete_section,
            "courses": delete_course,
            "holidays": delete_holiday,
            "timeslots": delete_timeslot,
        }
        if category not in deleters:
            raise ApiError(404, "Not found")
        with connect() as conn:
            if category in {"teachers", "rooms", "sections", "courses"}:
                self._ensure_exists(conn, category, item_id)
            try:
                result = deleters[category](conn, item_id)
            except ValueError as error:
                raise ApiError(409, str(error))
            if result is False:
                raise ApiError(404, f"{category[:-1]} not found")
            log_audit(conn, self._actor_id(), "delete", category.rstrip("s"), item_id)
            conn.commit()
        self._json({"success": True})

    # -------------------------------------------------------------- helpers

    def _dispatch(self, route) -> None:
        try:
            route()
        except ApiError as error:
            self._json({"error": str(error)}, status=error.status)
        except json.JSONDecodeError:
            self._json({"error": "Request body is not valid JSON"}, status=400)
        except sqlite3.IntegrityError as error:
            self._json({"error": f"Record is in use or violates a constraint: {error}"}, status=409)
        except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
            pass
        except Exception as error:  # last-resort guard so the worker thread never dies silently
            import traceback

            traceback.print_exc()
            try:
                self._json({"error": f"Internal error: {error}"}, status=500)
            except OSError:
                pass

    def _reject_get_only(self, path: str) -> None:
        if path in GET_ONLY_PATHS or (path == "/api/change-requests" and self.command == "DELETE"):
            raise ApiError(405, f"{self.command} is not allowed on {path}")

    def _ensure_exists(self, conn: sqlite3.Connection, table: str, item_id: int) -> None:
        row = conn.execute(f"SELECT id FROM {table} WHERE id = ?", (item_id,)).fetchone()
        if row is None:
            raise ApiError(404, f"{table[:-1]} {item_id} not found")

    def _actor_id(self) -> int | None:
        header = self.headers.get("X-User-Id", "")
        return int(header) if header.isdigit() else None

    def _require_role(self, allowed: set[str]) -> None:
        """Reject identified actors whose role is not in `allowed` (FR-00.5).

        Requests without an X-User-Id header are treated as trusted internal
        clients (test harnesses, scripts); the shipped frontend always sends it.
        """
        actor = self._actor_id()
        if actor is None:
            return
        with connect() as conn:
            row = conn.execute("SELECT role FROM users WHERE id = ?", (actor,)).fetchone()
        if row is not None and row["role"] not in allowed:
            raise ApiError(403, f"Role '{row['role']}' is not allowed to perform this action")

    def _int_param(self, query: dict, name: str) -> int:
        values = query.get(name, [])
        if not values or not values[0].lstrip("-").isdigit():
            raise ApiError(400, f"Query parameter '{name}' must be an integer")
        return int(values[0])

    @staticmethod
    def _require_str(body: dict, field: str, max_len: int = 200) -> str:
        value = str(body.get(field, "") or "").strip()
        if not value:
            raise ApiError(400, f"Field '{field}' is required")
        if len(value) > max_len:
            raise ApiError(400, f"Field '{field}' must be at most {max_len} characters")
        return value

    @staticmethod
    def _require_day(body: dict, field: str = "day") -> str:
        value = str(body.get(field, "") or "").strip().capitalize()
        if value not in VALID_DAYS:
            raise ApiError(400, f"Field '{field}' must be one of: {', '.join(sorted(VALID_DAYS))}")
        return value

    @staticmethod
    def _require_time(body: dict, field: str) -> str:
        value = str(body.get(field, "") or "").strip()
        if not TIME_PATTERN.match(value):
            raise ApiError(400, f"Field '{field}' must be a time in HH:MM format")
        return value

    @staticmethod
    def _require_room_type(body: dict, field: str, default: str = "lecture") -> str:
        value = str(body.get(field, default) or default).strip().lower()
        if value not in VALID_ROOM_TYPES:
            raise ApiError(400, f"Field '{field}' must be one of: {', '.join(sorted(VALID_ROOM_TYPES))}")
        return value

    @staticmethod
    def _require_int(body: dict, field: str, default: int | None = None, minimum: int | None = None) -> int:
        raw = body.get(field, default)
        if raw is None:
            raise ApiError(400, f"Field '{field}' is required")
        try:
            value = int(raw)
        except (TypeError, ValueError):
            raise ApiError(400, f"Field '{field}' must be an integer")
        if minimum is not None and value < minimum:
            raise ApiError(400, f"Field '{field}' must be at least {minimum}")
        return value

    def _read_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
        parsed = json.loads(body)
        if not isinstance(parsed, dict):
            raise ApiError(400, "Request body must be a JSON object")
        return parsed

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
