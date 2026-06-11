"""End-to-end check against the live dev server (frontend-equivalent requests)."""
import json
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"


def call(path, method="GET", data=None, actor=None, raw=False):
    headers = {"Content-Type": "application/json"}
    if actor:
        headers["X-User-Id"] = str(actor)
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode()
            return resp.status, body if raw else json.loads(body)
    except urllib.error.HTTPError as err:
        body = err.read().decode()
        return err.code, body if raw else json.loads(body or "{}")


results = []

def check(name, ok):
    results.append((name, ok))
    print(("OK   " if ok else "FAIL ") + name)


# Static shell + scripts served
status, html = call("/", raw=True)
check("index.html served", status == 200 and "toastContainer" in html and "notifPanel" in html)
status, js = call("/scripts/render.js", raw=True)
check("render.js served with edit support", status == 200 and "enterEditMode" in js)

# Bootstrap exposes published timetable separately
status, boot = call("/api/bootstrap")
check("bootstrap has publishedTimetable key", "publishedTimetable" in boot)
published = boot["publishedTimetable"]
check("published version is status=published", published is None or published["status"] == "published")

# Users for login cards
status, users = call("/api/users")
roles = {u["role"] for u in users["users"]}
check("all five login roles present", {"administrator", "coordinator", "teacher", "student", "facility_manager"} <= roles)
admin = next(u["id"] for u in users["users"] if u["role"] == "administrator")
student = next(u["id"] for u in users["users"] if u["role"] == "student")
teacher_user = next(u for u in users["users"] if u["role"] == "teacher")

# Admin edit flow (same values -> harmless write) + audit trail
teachers = call("/api/master-data")[1]["teachers"]
t0 = teachers[0]
status, _ = call(f"/api/master-data/teachers/{t0['id']}", "PUT",
                 {"name": t0["name"], "department": t0["department"], "max_daily_load": t0["max_daily_load"]},
                 actor=admin)
check("admin can update teacher (edit flow)", status == 200)
status, log = call("/api/audit-log")
check("audit log records the update with actor", status == 200 and any(
    item["action"] == "update" and item["entity_type"] == "teacher" and item["actor_id"] == admin
    for item in log["auditLog"]))

# Role enforcement live
status, _ = call("/api/timetable/generate", "POST", actor=student)
check("student blocked from generate (403)", status == 403)
status, _ = call("/api/master-data/teachers", "POST", {"name": "x", "department": "y"}, actor=student)
check("student blocked from master data (403)", status == 403)

# Student notification feed (publish happened in earlier session)
status, notif = call(f"/api/notifications?user_id={student}")
check("student notifications endpoint live", status == 200 and "unread" in notif)

# Teacher's published-view source has entries for them (if published exists)
if published:
    mine = [e for e in published["entries"]
            if e["teacher_id"] == teacher_user.get("teacher_id") and e["status"] == "placed"]
    check("published version contains teacher's classes", len(mine) > 0)

# Versions + compare endpoints
status, versions = call("/api/timetable/versions")
check("versions listed", status == 200 and len(versions["versions"]) >= 1)
if len(versions["versions"]) >= 2:
    a, b = versions["versions"][1]["id"], versions["versions"][0]["id"]
    status, diff = call(f"/api/timetable/compare?a={a}&b={b}")
    check("compare works", status == 200 and "totals" in diff)

failed = [name for name, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} passed")
raise SystemExit(1 if failed else 0)
