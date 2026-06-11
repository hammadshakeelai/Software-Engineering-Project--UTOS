"""Quick smoke test of new/changed UTOS endpoints against a throwaway server."""
import json
import os
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.backend.database as database

tmp = tempfile.mkdtemp()
database.DB_PATH = Path(tmp) / "smoke.sqlite"

from http.server import ThreadingHTTPServer

from app.backend.database import initialize_database
from app.backend.server import RequestHandler

initialize_database()
server = ThreadingHTTPServer(("127.0.0.1", 0), RequestHandler)
port = server.server_address[1]
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
BASE = f"http://127.0.0.1:{port}"


def call(path, method="GET", data=None, expect=200):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={"Content-Type": "application/json", "X-User-Id": "1"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as err:
        status = err.code
        payload = json.loads(err.read().decode() or "{}")
    assert status == expect, f"{method} {path}: expected {expect}, got {status}: {payload}"
    return payload


checks = []

def check(name, fn):
    try:
        fn()
        checks.append((name, "OK"))
    except AssertionError as err:
        checks.append((name, f"FAIL: {err}"))


check("health", lambda: call("/api/health"))
check("generate", lambda: call("/api/timetable/generate", "POST"))
check("versions list", lambda: (lambda v: 0)(call("/api/timetable/versions")["versions"]))
check("publish ok", lambda: call("/api/timetable/1/publish", "PUT"))
check("publish missing -> 404", lambda: call("/api/timetable/999/publish", "PUT", expect=404))
check("lock missing -> 404", lambda: call("/api/timetable/entry/99999/lock", "PUT", expect=404))
check("post teacher empty -> 400", lambda: call("/api/master-data/teachers", "POST", {}, expect=400))
check("post room minimal -> 201", lambda: call("/api/master-data/rooms", "POST", {"code": "T-1", "building": "T", "capacity": 20}, expect=201))
check("delete health -> 405", lambda: call("/api/health", "DELETE", expect=405))
check("post holiday", lambda: call("/api/master-data/holidays", "POST", {"name": "Test", "day": "Thursday"}, expect=201))
check("delete holiday", lambda: call("/api/master-data/holidays/2", "DELETE"))
check("update preference", lambda: call("/api/master-data/preferences/1", "PUT", {"enabled": True, "weight": 3}))
check("pref weight 99 -> 400", lambda: call("/api/master-data/preferences/1", "PUT", {"enabled": True, "weight": 99}, expect=400))
check("availability get", lambda: call("/api/teacher-availability?teacher_id=1"))
check("availability set", lambda: call("/api/teacher-availability/1", "PUT", {"unavailable_slot_ids": [1, 2]}))
check("notifications for coordinator", lambda: (lambda n: (_ for _ in ()).throw(AssertionError("no notifications")) if not n["notifications"] else None)(call("/api/notifications?user_id=2")))
check("reoptimize", lambda: (lambda p: (_ for _ in ()).throw(AssertionError("no disruption")) if "disruption" not in p else None)(call("/api/timetable/reoptimize", "POST")))
check("compare 1 vs 2", lambda: call("/api/timetable/compare?a=1&b=2"))
check("compare missing -> 404", lambda: call("/api/timetable/compare?a=1&b=999", expect=404))
check("audit log populated", lambda: (lambda a: (_ for _ in ()).throw(AssertionError("empty audit")) if not a["auditLog"] else None)(call("/api/audit-log")))
check("version by id", lambda: call("/api/timetable/version/1"))
def _bad_json():
    req = urllib.request.Request(
        BASE + "/api/master-data/teachers", data=b"{not json", method="POST",
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
    except urllib.error.HTTPError as err:
        status = err.code
    assert status == 400, f"expected 400, got {status}"

check("delete teacher in use -> 409", lambda: call("/api/master-data/teachers/1", "DELETE", expect=409))
check("bad json -> 400", _bad_json)

server.shutdown()

failed = 0
for name, status in checks:
    print(f"{status:60s} {name}" if status != "OK" else f"OK    {name}")
    if status != "OK":
        failed += 1
print(f"\n{len(checks) - failed}/{len(checks)} passed")
sys.exit(1 if failed else 0)
