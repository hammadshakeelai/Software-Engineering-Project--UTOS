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
from app.backend.repositories.master_data import get_master_data
from app.backend.repositories.timetable_repository import get_latest_version, get_reports
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
        if parsed.path == "/api/timetable/latest":
            with connect() as conn:
                latest = get_latest_version(conn)
                self._json({"latestTimetable": latest, "reports": get_reports(conn, latest["id"] if latest else None)})
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/timetable/generate":
            with connect() as conn:
                self._json(generate_timetable(conn))
            return
        self._json({"error": "Not found"}, status=404)

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
