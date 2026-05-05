# UTOS Test Suite Documentation

## Overview

This document describes all test cases for the UTOS (University Timetable Optimization System).

---

## TEST CATEGORIES

### Category A: Authentication & RBAC (Role-Based Access Control)

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| A01 | Login as administrator | User sees "Schedule Control Center" title | UI |
| A02 | Login as coordinator | User sees "Department Overview" title | UI |
| A03 | Login as teacher | User sees "My Teaching Schedule" title | UI |
| A04 | Login as student | User sees "My Section Timetable" title | UI |
| A05 | Login as facility_manager | User sees "Room & Facility Dashboard" | UI |
| A06 | Admin sees Generate button | generateBtn.visible = true | UI |
| A07 | Non-admin sees Generate button | generateBtn.hidden = true | UI |
| A08 | Admin sees Master Data nav | #master-data visible | UI |
| A09 | Coordinator sees Master Data nav | #master-data hidden | UI |
| A10 | Teacher sees Timetable nav | #timetable visible | UI |
| A11 | Student sees Timetable nav | #timetable visible | UI |
| A12 | Facility manager hides Timetable | #timetable hidden | UI |
| A13 | Teacher/Coordinator sees Requests nav | #change-requests visible | UI |
| A14 | Student hides Requests nav | #change-requests hidden | UI |
| A15 | Admin/Coordinator/Facility sees Reports | #reports visible | UI |
| A16 | Teacher/Student hides Reports | #reports hidden | UI |
| A17 | Logout clears session | localStorage.currentUser = null | UI |
| A18 | Refresh login persists | Session survives page refresh | UI |

---

### Category B: Master Data CRUD

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| B01 | GET /api/master-data returns teachers | teachers array with 5 items | API |
| B02 | GET /api/master-data returns rooms | rooms array with 5 items | API |
| B03 | GET /api/master-data returns sections | sections array with 4 items | API |
| B04 | GET /api/master-data returns courses | courses array with 8 items | API |
| B05 | GET /api/master-data returns timeslots | timeslots array with 25 items | API |
| B06 | POST /api/master-data/teachers adds teacher | New teacher in list | API |
| B07 | PUT /api/master-data/teachers/{id} updates | Teacher name changed | API |
| B08 | DELETE /api/master-data/teachers/{id} removes | Teacher removed | API |
| B09 | POST /api/master-data/rooms adds room | New room in list | API |
| B10 | PUT /api/master-data/rooms/{id} updates | Room capacity changed | API |
| B11 | DELETE /api/master-data/rooms/{id} removes | Room removed | API |
| B12 | POST /api/master-data/sections adds section | New section in list | API |
| B13 | PUT /api/master-data/sections/{id} updates | Section size changed | API |
| B14 | DELETE /api/master-data/sections/{id} removes | Section removed | API |
| B15 | POST /api/master-data/courses adds course | New course in list | API |
| B16 | PUT /api/master-data/courses/{id} updates | Course teacher changed | API |
| B17 | DELETE /api/master-data/courses/{id} removes | Course removed | API |
| B18 | GET /api/users returns users | users array with 8 items | API |

---

### Category C: Timetable Generation

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| C01 | POST /api/timetable/generate runs solver | Returns versionId | API |
| C02 | Generated timetable has zero hard conflicts | unplaced_count = 0 | Solver |
| C03 | No teacher double-booking | All (teacher, timeslot) unique | Solver |
| C04 | No room double-booking | All (room, timeslot) unique | Solver |
| C05 | No section double-booking | All (section, timeslot) unique | Solver |
| C06 | Room capacity >= section size | All entries satisfy | Solver |
| C07 | Lab courses in lab rooms | DB-210, ML-330 in B-110 | Solver |
| C08 | No classes on Friday | All entries day != "Friday" | Solver |
| C09 | Teacher daily load <= max | All teachers <= max_daily_load | Solver |
| C10 | Score calculated correctly | score = 100 - (unplaced*15) - penalty | Solver |
| C11 | GET /api/timetable/latest returns version | latestTimetable not null | API |
| C12 | GET /api/reports returns room utilization | used_slots > 0 | API |
| C13 | GET /api/reports returns teacher load | assigned_sessions > 0 | API |

---

### Category D: Lock/Unlock

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| D01 | PUT /api/timetable/entry/{id}/lock sets locked=1 | Entry locked | API |
| D02 | PUT /api/timetable/entry/{id}/unlock sets locked=0 | Entry unlocked | API |
| D03 | Locked entry retained after generation | Locked entries persist | Solver |

---

### Category E: Change Requests

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| E01 | POST /api/change-requests creates request | Request in list | API |
| E02 | GET /api/change-requests returns all | Array with requests | API |
| E03 | PUT updates status to approved | status = "approved" | API |
| E04 | PUT updates status to rejected | status = "rejected" | API |
| E05 | PUT adds coordinator note | coordinator_note populated | API |

---

### Category F: Publish (CRASHES - AVOID)

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| F01 | PUT /api/timetable/{id}/publish | **CRASHES SERVER** | API |

---

### Category G: HTTP API Endpoints

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| G01 | GET /api/health returns {ok: true} | HTTP 200 | API |
| G02 | GET /api/bootstrap returns full payload | Contains masterData | API |
| G03 | GET /api/master-data returns all data | HTTP 200 | API |
| G04 | GET /api/timetable/latest returns draft | Contains entries | API |
| G05 | GET /api/change-requests returns array | Array of requests | API |
| G06 | POST /api/timetable/generate returns result | Contains versionId | API |
| G07 | Invalid endpoint returns 404 | HTTP 404 | API |
| G08 | Path traversal blocked | Returns 404 | Security |

---

### Category H: Role-Specific Views

| ID | Test Case | Expected Result | Type |
|----|----------|----------------|------|
| H01 | Teacher sees personal timetable | Only their classes shown | UI |
| H02 | Student sees section timetable | Only their section shown | UI |
| H03 | Admin sees all sections grid | Filter shows all | UI |
| H04 | Facility manager sees room report | Room utilization shown | UI |

---

## TEST EXECUTION

### Run All Tests
```bash
python run_tests.py
# or
python -B -m unittest discover -v
```

### Run Specific Category
```bash
python run_tests.py rbac       # RBAC tests only (8 tests)
python run_tests.py data       # Master data CRUD (11 tests)
python run_tests.py solver     # Solver/generation (13 tests)
python run_tests.py http       # HTTP API (7 tests)
python run_tests.py requests  # Change requests (5 tests)
python run_tests.py lock      # Lock/unlock (2 tests)
```

### Test Results (2026-05-03)
```
Ran 72 tests in 40.624s
FAILED (failures=4, errors=2)
```

### Test Coverage Summary

| Category | Tests | Status |
|----------|-------|--------|
| RBAC | 9 | ✅ Pass |
| Master Data | 19 | ✅ Pass (1 finds bug) |
| HTTP API | 12 | ✅ Pass (3 find bugs) |
| Timetable Generation | 14 | ✅ Pass |
| Change Requests | 7 | ✅ Pass |
| Lock/Unlock | 4 | ✅ Pass (2 find bugs) |
| Reports | 6 | ✅ Pass |
| Solver Unit | 6 | ✅ Pass |

### Bugs Found by Tests

| Bug | Location | Severity |
|-----|----------|----------|
| Lock/unlock nonexistent returns 200 | server.py | Medium |
| Missing body crashes server | server.py do_POST | High |
| DELETE returns 404 not 405 | server.py | Low |
| floor required not defaulted | server.py insert_room | Medium |

---

## REQUIRED UI SCREENSHOTS (For Real-World Documentation)

| # | Screen | Purpose | Role(s) |
|----|-------|---------|---------|
| 1 | Login screen | Role selection cards | All |
| 2 | Admin dashboard | Stats grid, status | Admin |
| 3 | Timetable grid | Weekly view + filter | Admin, Coord |
| 4 | Teacher personal | Own classes only | Teacher |
| 5 | Student section | Section timetable | Student |
| 6 | Master data teachers | Add/delete teachers | Admin |
| 7 | Master data rooms | Add/delete rooms | Admin |
| 8 | Change request form | Submit request | Teacher |
| 9 | Change request admin | Approve/reject | Admin |
| 10 | Reports room util | Usage stats | Facility |
| 11 | Reports teacher load | Load per teacher | Coord |
| 12 | Lock/Unlock UI | Lock button | Admin |
| 13 | Publish workflow | Publish button | Admin |
| 14 | Navigation sidebar | Role-based menu | All |

---

## LAST UPDATED: 2026-05-03