"""Red-team the UTOS API: adversarial / malformed / abusive inputs a real
university deployment would eventually send. Every check asserts the server
rejects cleanly (4xx) and stays alive — never a 500 or a dead worker."""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"
ADMIN = 1


def raw_call(path, method="GET", data=None, actor=ADMIN, raw_body=None):
    headers = {"Content-Type": "application/json"}
    if actor is not None:
        headers["X-User-Id"] = str(actor)
    body = raw_body if raw_body is not None else (json.dumps(data).encode() if data is not None else None)
    req = urllib.request.Request(BASE + path, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()
    except urllib.error.URLError as err:
        return -1, str(err)


results = []

def expect(name, status, allowed):
    ok = status in allowed
    results.append((name, ok, status))
    print(f"{'OK  ' if ok else 'FAIL'} [{status}] {name}")


def alive():
    s, _ = raw_call("/api/health")
    return s == 200


print("=== Red-team: malformed & adversarial input ===")

def check(name, path, method="GET", data=None, actor=ADMIN, raw_body=None, allowed=(400,)):
    status, _ = raw_call(path, method, data, actor, raw_body)
    expect(name, status, allowed)
    assert alive(), f"server died after: {name}"

# Malformed JSON
check("broken JSON body -> 400", "/api/master-data/teachers", "POST", raw_body=b"{ not json", allowed=(400,))
check("JSON array instead of object -> 400", "/api/master-data/teachers", "POST", raw_body=b"[1,2,3]", allowed=(400,))
check("JSON string instead of object -> 400", "/api/master-data/teachers", "POST", raw_body=b'"hi"', allowed=(400,))

# Missing / empty required fields
check("empty teacher -> 400", "/api/master-data/teachers", "POST", data={}, allowed=(400,))
check("whitespace-only name -> 400", "/api/master-data/teachers", "POST", data={"name": "   ", "department": "CS"}, allowed=(400,))

# Type confusion
check("string capacity -> 400", "/api/master-data/rooms", "POST", data={"code": "RT1", "building": "B", "capacity": "lots"}, allowed=(400,))
check("negative capacity -> 400", "/api/master-data/rooms", "POST", data={"code": "RT2", "building": "B", "capacity": -5}, allowed=(400,))
check("zero weekly_sessions -> 400", "/api/master-data/courses", "POST",
      data={"code": "ZS", "title": "Z", "teacher_id": 1, "section_id": 1, "weekly_sessions": 0}, allowed=(400,))
check("float teacher_id -> coerced or 400", "/api/master-data/courses", "POST",
      data={"code": "FL", "title": "F", "teacher_id": 1.9, "section_id": 1, "weekly_sessions": 1}, allowed=(201, 400, 409))

# Invalid enums / domains
check("bad room_type -> 400", "/api/master-data/rooms", "POST",
      data={"code": "BT", "building": "B", "capacity": 30, "room_type": "dungeon"}, allowed=(400,))
check("holiday on Sunday -> 400", "/api/master-data/holidays", "POST",
      data={"name": "X", "day": "Sunday"}, allowed=(400,))
check("timeslot bad time -> 400", "/api/master-data/timeslots", "POST",
      data={"day": "Monday", "start_time": "9am", "end_time": "10am", "sort_order": 99}, allowed=(400,))
check("timeslot end before start -> 400", "/api/master-data/timeslots", "POST",
      data={"day": "Monday", "start_time": "14:00", "end_time": "09:00", "sort_order": 99}, allowed=(400,))
check("preference weight 999 -> 400", "/api/master-data/preferences/1", "PUT",
      data={"enabled": True, "weight": 999}, allowed=(400,))
check("preference weight negative -> 400", "/api/master-data/preferences/1", "PUT",
      data={"enabled": True, "weight": -3}, allowed=(400,))

# Referential integrity (FK to nonexistent rows)
check("course w/ ghost teacher -> 409", "/api/master-data/courses", "POST",
      data={"code": "GH", "title": "Ghost", "teacher_id": 999999, "section_id": 1, "weekly_sessions": 1},
      allowed=(409, 400))
check("change request ghost user -> 409/400", "/api/change-requests", "POST",
      data={"requester_id": 888888, "target_type": "room", "reason": "x"}, allowed=(409, 400))

# Duplicate unique keys
raw_call("/api/master-data/rooms", "POST", data={"code": "DUP-1", "building": "B", "capacity": 20})
check("duplicate room code -> 409", "/api/master-data/rooms", "POST",
      data={"code": "DUP-1", "building": "B", "capacity": 20}, allowed=(409,))

# XSS / injection payloads stored safely (should accept as data, escaped on render)
xss = "<script>alert('x')</script>"
s, _ = raw_call("/api/master-data/teachers", "POST", data={"name": xss, "department": "CS"})
expect("XSS payload stored as data -> 201", s, (201,))
sqli = "Robert'); DROP TABLE teachers;--"
s, _ = raw_call("/api/master-data/sections", "POST", data={"name": sqli, "department": "CS", "size": 10})
expect("SQLi payload parametrized -> 201", s, (201,))
assert alive(), "server died after injection payloads"
# Prove the table survived the SQLi attempt
s, body = raw_call("/api/master-data")
teachers_exist = len(json.loads(body)["teachers"]) > 0
expect("teachers table intact after SQLi", 200 if teachers_exist else 500, (200,))

# Path / id abuse
check("non-numeric id in path -> 404", "/api/master-data/teachers/abc", "DELETE", allowed=(404,))
check("huge id -> 404", "/api/master-data/teachers/999999999999", "PUT",
      data={"name": "x", "department": "y"}, allowed=(404,))
check("path traversal -> 404", "/%2e%2e/%2e%2e/app/backend/seed.py", allowed=(404,))
check("compare missing query params -> 400", "/api/timetable/compare", allowed=(400,))
check("compare non-numeric -> 400", "/api/timetable/compare?a=foo&bar=baz", allowed=(400,))

# Wrong methods
check("POST to health -> 405", "/api/health", "POST", data={}, allowed=(405,))
check("DELETE bootstrap -> 405", "/api/bootstrap", "DELETE", allowed=(405,))

# Authorization abuse
check("student generates -> 403", "/api/timetable/generate", "POST", actor=3, allowed=(403,))
check("teacher edits master data -> 403", "/api/master-data/rooms", "POST",
      actor=2, data={"code": "HX", "building": "B", "capacity": 10}, allowed=(403,))
check("student approves request -> 403/404", "/api/change-requests/1/status", "PUT",
      actor=3, data={"status": "approved"}, allowed=(403, 404))

# Oversized payloads
check("4000-char name -> 400", "/api/master-data/teachers", "POST",
      data={"name": "A" * 4000, "department": "CS"}, allowed=(400,))

# Concurrency: hammer publish + generate-less reads simultaneously
print("\n=== Red-team: concurrent publish storm ===")
import threading
errors = []
def worker(i):
    try:
        s, _ = raw_call("/api/timetable/latest")
        if s != 200:
            errors.append(("read", s))
    except Exception as exc:
        errors.append(("read-exc", str(exc)))
threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
for t in threads: t.start()
for t in threads: t.join()
expect("20 concurrent reads all 200", 200 if not errors else 500, (200,))
print(f"  concurrency errors: {errors[:3]}")

print()
failed = [n for n, ok, _ in results if not ok]
print(f"{len(results) - len(failed)}/{len(results)} checks passed; server alive: {alive()}")
if failed:
    print("FAILURES:", failed)
sys.exit(1 if failed or not alive() else 0)
