# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

### Running the Application

From the repository root:

```bash
python -m app.backend.server
```

Then open `http://127.0.0.1:8000` in your browser.

The app runs on port 8000 by default. To use a different port, set the `UTOS_PORT` environment variable:

```bash
UTOS_PORT=9000 python -m app.backend.server
```

### Running Tests

```bash
python -B -m unittest discover -v
```

Run a specific test file:

```bash
python -m unittest tests.test_solver -v
```

## Project Overview

**UTOS** (University Timetable Optimization and Management System) is a web-based timetable scheduling system for academic departments. It manages teachers, courses, rooms, sections, and timeslots; generates conflict-free timetables via a pluggable solver; and supports role-based access for five different actor types.

### Key Features

- **5 Actor Roles**: Timetable Administrator, Department Coordinator, Teacher, Student, Facility Manager — each with different views and permissions
- **Master Data Management**: CRUD operations for teachers, rooms, courses, sections, timeslots, holidays
- **Constraint System**: Hard constraints (no double-booking, capacity checks) and soft preferences (morning classes, building compaction)
- **Timetable Generation**: Constructive/backtracking solver (designed to be swappable with OR-Tools CP-SAT later)
- **Role-Based Access Control**: Login screen with localStorage session persistence; views and forms gated by user role
- **Change Request Workflow**: Users can request modifications; administrators approve/reject/implement

## Architecture

The system is a 4-layer architecture:

```
┌─────────────────────────────────────┐
│  Frontend (HTML/CSS/JavaScript)     │ ← Vanilla JS, modular scripts
├─────────────────────────────────────┤
│  Backend API (Python HTTP Server)   │ ← ThreadingHTTPServer, JSON REST
├─────────────────────────────────────┤
│  Repositories & Services            │ ← Data access, business logic
├─────────────────────────────────────┤
│  Database (SQLite)                  │ ← Master data, timetable versions
└─────────────────────────────────────┘
```

### Backend (`app/backend/`)

- **server.py**: HTTP request handler. Implements `do_GET`, `do_POST`, `do_PUT`, `do_DELETE`. Routes requests to repositories. Uses path parsing (`split("/")`) to extract IDs from URLs.
- **database.py**: SQLite connection factory with row factories and pragma setup. Auto-creates `app/data/utos.sqlite` on first run.
- **schema.sql**: Database schema with 11 tables (users, teachers, rooms, courses, sections, timeslots, holidays, teacher_availability, preferences, timetable_versions, timetable_entries, change_requests).
- **seed.py**: Initial database population with sample users (5 roles), teachers, rooms, sections, courses, timeslots, preferences.

#### Repositories (`app/backend/repositories/`)

- **master_data.py**: Read/write operations for teachers, rooms, courses, sections. Functions: `get_master_data()`, `insert_teacher()`, `update_teacher()`, `delete_teacher()`, etc. All write operations call `conn.commit()`.
- **timetable_repository.py**: Timetable and change-request operations. Functions: `get_latest_version()`, `lock_entry()`, `unlock_entry()`, `publish_version()`, `insert_change_request()`, `get_change_requests()`, `update_change_request_status()`.

#### Services (`app/backend/services/`)

- **bootstrap_service.py**: Returns the initial payload with master data, latest timetable, and reports.
- **timetable_service.py**: Calls the solver and persists the result to the database.

#### Solver (`app/backend/algorithms/timetable_solver.py`)

Constructive/backtracking algorithm. Takes a `solver_problem` dict with teachers, courses, rooms, sections, timeslots, constraints, and preferences; returns timetable entries with a score and conflict report. **Design goal**: swappable with OR-Tools CP-SAT without changing the API.

### Frontend (`app/frontend/`)

Vanilla HTML/CSS/JavaScript. No frameworks or build tools.

- **index.html**: Single page with app shell. Login screen hidden by default. Sections for master data, timetable, change requests, and reports are shown/hidden by role.
- **scripts/state.js**: Global state object with current user, master data, timetable, change requests. Functions: `login()`, `logout()`, `loadUserFromStorage()`, `setBootstrap()`, `setGenerated()`, `setChangeRequests()`.
- **scripts/main.js**: App initialization and event handlers. Loads users for login, handles login/logout, loads timetable data, binds UI event listeners.
- **scripts/api.js**: HTTP client. Methods for all backend endpoints: `getUsers()`, `bootstrap()`, `generateTimetable()`, `addTeacher()`, `updateTeacher()`, `deleteTeacher()`, `lockEntry()`, `unlockEntry()`, `submitChangeRequest()`, `updateChangeRequestStatus()`, `publishTimetable()`.
- **scripts/render.js**: View rendering. Functions: `renderLoginScreen()`, `renderNav()`, `renderAll()`, `renderTimetable()`, `renderChangeRequests()`, and role-specific views (`renderTeacherView()`, `renderStudentView()`, `renderFacilityManagerView()`). Role checks use `state.currentUser?.role`.
- **styles/**: CSS for login screen, forms, timetable grid, change-request cards, locked badges, buttons.

## API Endpoints

### Authentication & Data
- `GET /api/health` — server status
- `GET /api/bootstrap` — initial payload (master data, timetable, reports)
- `GET /api/users` — user list for login picker
- `GET /api/master-data` — all master data
- `GET /api/timetable/latest` — latest timetable version with reports

### Master Data CRUD
- `POST /api/master-data/{teachers,rooms,sections,courses}` — create (returns 201 with ID)
- `PUT /api/master-data/{teachers,rooms,sections,courses}/{id}` — update
- `DELETE /api/master-data/{teachers,rooms,sections,courses}/{id}` — delete

### Timetable Operations
- `POST /api/timetable/generate` — run solver, create new version
- `POST /api/timetable/reoptimize` — repair latest draft preserving locked entries; returns disruption summary
- `PUT /api/timetable/{id}/publish` — publish version, archive previous published, notify users (fixed; regression-tested)
- `PUT /api/timetable/entry/{id}/lock` — lock a timetable entry (admin only)
- `PUT /api/timetable/entry/{id}/unlock` — unlock a timetable entry (admin only)
- `GET /api/timetable/versions` — list all versions with metrics
- `GET /api/timetable/version/{id}` — one version with entries
- `GET /api/timetable/compare?a={id}&b={id}` — diff two versions (added/removed/changed)

### Change Requests
- `GET /api/change-requests` — list all change requests
- `POST /api/change-requests` — submit a change request (notifies admins/coordinators)
- `PUT /api/change-requests/{id}/status` — approve/reject/implement (notifies requester)
- `PUT /api/change-requests/{id}/note` — coordinator recommendation

### Master Data Extras
- `POST/DELETE /api/master-data/holidays[/{id}]` — holiday management
- `POST/DELETE /api/master-data/timeslots[/{id}]` — timeslot management (delete blocked with 409 if in use)
- `PUT /api/master-data/preferences/{id}` — enable/disable + weight (0–10) for soft preferences
- `GET /api/teacher-availability?teacher_id={id}` / `PUT /api/teacher-availability/{id}` — availability editor

### System
- `GET /api/notifications?user_id={id}` / `PUT /api/notifications/{id}/read` — in-app notifications
- `GET /api/audit-log` — audit trail (actor, action, entity, old/new values)
- Write endpoints accept an `X-User-Id` header identifying the acting user for audit logging.
- Validation: missing/invalid fields → 400, unknown IDs → 404, method not allowed → 405, in-use deletes → 409.

## Database Schema

**Key tables:**

- `users(id, name, email, role, teacher_id, section_id)` — 5 roles: administrator, coordinator, teacher, student, facility_manager. `teacher_id` and `section_id` link users to their role-specific data.
- `teachers(id, name, department, max_daily_load)` — instructors
- `rooms(id, code, building, floor, capacity, room_type, features)` — classrooms
- `sections(id, name, department, size)` — student cohorts
- `courses(id, code, title, teacher_id, section_id, weekly_sessions, required_room_type)` — classes to schedule
- `timeslots(id, day, start_time, end_time, sort_order, is_morning, is_last_slot)` — weekly schedule grid
- `timetable_versions(id, name, status, score, hard_conflicts, soft_penalty, unplaced_count, distance_to_feasibility, created_at)` — generated timetables (draft, published, archived)
- `timetable_entries(id, version_id, course_id, teacher_id, section_id, room_id, timeslot_id, event_uid, locked, status)` — scheduled classes (placed or unplaced)
- `change_requests(id, requester_id, target_type, target_id, reason, status, created_at)` — modification proposals
- `holidays(id, name, day)` — blocked days
- `teacher_availability(teacher_id, timeslot_id, is_available)` — instructor constraints
- `preferences(key, label, enabled, weight, value)` — soft-constraint toggles

## Common Development Tasks

### Adding a New Master Data Type (e.g., "Buildings")

1. **Schema**: Add table to `schema.sql` (e.g., `buildings(id, name, location)`)
2. **Seed**: Add sample rows to `seed.py`
3. **Repository**: Add `get_buildings()`, `insert_building()`, `update_building()`, `delete_building()` to `master_data.py`
4. **Server**: Add routes in `server.py` (POST, PUT, DELETE `/api/master-data/buildings`; extract from path_parts)
5. **API**: Add `addBuilding()`, `updateBuilding()`, `deleteBuilding()` to `api.js`
6. **State**: Add `buildings: []` to state in `state.js`
7. **Render**: Add table/list rendering in `render.js`

### Changing a Role's Permissions

Permissions are enforced at the **render level** (UI) and **logic level** (backend). To restrict a role:

1. In `render.js`: Add role check in the relevant render function:
   ```javascript
   if (state.currentUser?.role !== "administrator") {
     return; // don't render this section
   }
   ```
2. In `server.py`: Add role check before executing the operation (optional; UI gating is primary).

### Modifying the Solver

The solver in `timetable_solver.py` is designed to be pluggable. The interface is:

```python
def solve(solver_problem: dict) -> dict
```

Where `solver_problem` has keys: `teachers`, `rooms`, `courses`, `sections`, `timeslots`, `holidays`, `availability`, `preferences`.

It returns a dict with `entries` (list of assignments), `score`, `conflicts`, `unplaced`.

To integrate a new solver (e.g., OR-Tools CP-SAT):
1. Create a new file (e.g., `app/backend/algorithms/ortools_solver.py`)
2. Implement `solve(solver_problem: dict) -> dict` with the same signature
3. Update `timetable_service.py` to import and call the new solver

### Testing

- Unit tests in `tests/test_solver.py` — solver algorithm correctness
- Integration tests in `tests/test_integration.py` — end-to-end flows

Run tests frequently during development.

## Known Issues

### Publish Endpoint Crash — FIXED
The historical `PUT /api/timetable/{id}/publish` crash ("Empty reply from server") is fixed: every handler now runs inside a dispatch wrapper that converts exceptions to JSON error responses instead of killing the worker thread. Covered by `tests/test_srs_features.py::PublishTests::test_publish_repeated_requests_never_crash_server`.

## Key Design Decisions

1. **No External Dependencies**: Backend uses only Python stdlib (http.server, sqlite3, json). Reduces deployment friction.
2. **Swappable Solver**: Solver is isolated in `algorithms/` with a clean input/output contract. Allows future optimization upgrades.
3. **Frontend Modularity**: Scripts are small and loosely coupled. No framework; easy to read and modify.
4. **Role-Based UI**: Access control is primarily UI-gated (render-level checks). The backend does not enforce authorization; assume the frontend is trusted.
5. **localStorage Sessions**: User role is persisted across page reloads in `state.currentUser`. No server-side session management yet.

## File Organization

```
app/
├── backend/
│   ├── algorithms/
│   │   ├── __init__.py
│   │   └── timetable_solver.py        ← Solver logic (swappable)
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── master_data.py              ← Master data CRUD
│   │   └── timetable_repository.py     ← Timetable & change requests
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bootstrap_service.py        ← Initial payload
│   │   └── timetable_service.py        ← Solver orchestration
│   ├── __init__.py
│   ├── database.py                     ← DB connection & setup
│   ├── schema.sql                      ← Schema definition
│   ├── seed.py                         ← Sample data
│   └── server.py                       ← HTTP handler & routing
├── frontend/
│   ├── index.html                      ← Single page
│   ├── scripts/
│   │   ├── api.js                      ← HTTP client
│   │   ├── main.js                     ← App initialization
│   │   ├── render.js                   ← View rendering (role-aware)
│   │   └── state.js                    ← Global state
│   └── styles/
│       └── components.css               ← Styles
├── __init__.py
└── README.md                           ← Quick start for the app
tests/
├── __init__.py
├── test_integration.py                 ← End-to-end tests
└── test_solver.py                      ← Solver algorithm tests
docs/
└── SRS.md                              ← Software requirements spec
```

## Notes for Future Work

- **Publish Endpoint**: Debug and fix the server crash. May require profiling or reworking request handling in `do_PUT()`.
- **Authentication**: Current login is frontend-only (no password). Add server-side session tokens if security is needed.
- **Form Validation**: Add client-side (frontend) and server-side (backend) validation for all POST/PUT requests.
- **Soft Constraints**: The preferences table is seeded but the solver doesn't currently use all of them. Implement full soft-constraint scoring.
- **Reports**: Facility Manager reports are stubbed; implement room utilization, teacher load, and capacity analysis.
- **Error Handling**: Wrap API calls with try-catch; display user-friendly error messages in the UI.

## Implementation Status (June 2026)

All MVP priorities from the original action plan are implemented and covered by tests
(`tests/test_srs_features.py` plus the existing suites — run `python -B -m unittest discover`):

- [x] **Publish** — fixed, archives previous published version, notifies users, regression-tested
- [x] **Role-filtered views** — teachers/students see only the **published** version (`state.publishedTimetable`), filtered to their identity
- [x] **Master data CRUD UI** — add/edit/delete for teachers, rooms, sections, courses; add/delete for holidays and timeslots
- [x] **Teacher availability editor** — per-teacher per-slot checkbox grid (`renderAvailabilityEditor`)
- [x] **Preference configuration** — enable/disable + weight 0–10 per soft preference
- [x] **Change request → re-optimization** — approve, then "Re-generate with this change" (marks request implemented)
- [x] **Lock/unlock** — grid buttons; locked entries survive re-optimization (solver `_preassign_locked`)
- [x] **Versions & comparison** — version list with publish buttons; side-by-side diff (added/removed/changed)
- [x] **Notifications** — bell + unread badge; events: generate, publish, request submit/decision
- [x] **Audit log** — every write audited (actor via `X-User-Id`); admin viewer in Reports
- [x] **Reports** — utilization % with peak/free flags, teacher busiest-day vs limit, section gap analysis
- [x] **Validation & robustness** — 400/403/404/405/409 status codes; toasts for all errors; in-use deletes blocked
- [x] **Role enforcement (backend)** — requests carrying `X-User-Id` are checked against role permissions (403); header-less requests are treated as trusted (tests/scripts)
- [x] **Export/print** — client-side CSV export + print stylesheet

### Hardening & Realism (June 2026)
- **Backend role enforcement (403):** write requests carrying `X-User-Id` are checked against role permissions; header-less requests stay trusted (tests/scripts).
- **Input validation:** room types, weekdays, HH:MM time format + ordering, and string length are validated server-side (400 on violation). Malformed JSON, type confusion, SQLi, and XSS payloads are all handled safely (parametrized queries; UI escapes on render).
- **Unplaced-session reasons:** the solver explains *why* each session is unplaced (no room of type, no room large enough, teacher unavailable, or contention). Stored on `timetable_entries.reason` and shown in the UI's unplaced list.
- **Concurrency:** SQLite `busy_timeout=5000` so threaded requests wait rather than failing with "database is locked".
- **Multi-account login:** the login screen lists every account per role with a searchable picker, so each teacher/student signs in as themselves (FR-09).
- **Room delete guard:** rooms used by saved timetables can't be deleted (409), matching the timeslot guard.

### Test & seed tooling (`tools/`)
- `university_seed.py` — loads a realistic, *solvable* Faculty of Computing dataset (14 teachers, 14 rooms, 8 sections, 32 courses) that generates conflict-free with score ~92; creates teacher + student login accounts; publishes. Run against the live dev server on :8765.
- `stress_seed.py` — deliberately *infeasible* load (oversized sections, overloaded teachers) to prove the solver degrades gracefully and never violates a hard constraint.
- `redteam.py` — 33 adversarial API checks (malformed input, injection, auth bypass, concurrency); all must return 4xx and keep the server alive.
- `smoke_api.py` / `e2e_check.py` — quick endpoint and frontend-asset checks.

### Remaining / Future (Phase 2)
- [ ] **Real authentication** — server-side sessions, password hashing (login is picker-based)
- [ ] **OR-Tools CP-SAT solver** — drop-in replacement via `algorithms/ortools_solver.py`
- [ ] **Exam timetabling module** — UC16–UC20 from the SRS (rooms, student hierarchy, exam courses, exam solver, invigilation)
- [ ] **Academic calendar with real dates** — semester boundaries (current model is weekly day-based)
- [ ] **Multi-department support** — scope beyond single department
