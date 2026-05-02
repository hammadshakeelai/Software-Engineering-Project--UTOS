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
- `PUT /api/timetable/{id}/publish` — mark version as published ⚠️ **Known Issue**: causes server crash; avoid using
- `PUT /api/timetable/entry/{id}/lock` — lock a timetable entry (admin only)
- `PUT /api/timetable/entry/{id}/unlock` — unlock a timetable entry (admin only)

### Change Requests
- `GET /api/change-requests` — list all change requests
- `POST /api/change-requests` — submit a change request
- `PUT /api/change-requests/{id}/status` — approve/reject/implement

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

### Publish Endpoint Crash
The `PUT /api/timetable/{id}/publish` endpoint causes the server to crash with "Empty reply from server". The issue is intermittent and the root cause is unclear (possibly threading or request handling). **Workaround**: do not use the publish feature; mark timetables as published via direct database updates if needed. This is tracked as a TODO.

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

## Action Plan — What Remains To Be Built

### Priority 1: Fix Broken Features
- [ ] **Fix publish endpoint crash** (`PUT /api/timetable/{id}/publish`) — debug `do_PUT` in `server.py`, likely a missing response or threading issue
- [ ] **Student timetable filtering** — `renderTimetable()` in `render.js` must filter `timetable_entries` by `state.currentUser.section_id` when role is `student`
- [ ] **Course CRUD forms** — Master Data section shows teachers/rooms but no course add/delete UI yet. Add inline form like teachers/rooms

### Priority 2: Missing CRUD Forms (Admin)
- [ ] **Section management form** — add/edit/delete sections from Master Data
- [ ] **Timeslot management** — currently seed-only; admin should be able to add/edit periods
- [ ] **Holiday management** — add/remove holiday days from UI
- [ ] **Teacher availability editor** — per-teacher, per-slot toggle grid

### Priority 3: Constraint Configuration UI
- [ ] **Preference toggle screen** — checkboxes + weight sliders for all 5 preferences (morning, early ending, proximity, energy, traffic)
- [ ] The data exists in `preferences` table; UI just needs to read/write via `PUT /api/master-data/preferences/{id}`

### Priority 4: Workflow Completion
- [ ] **Change request → re-optimization** — when admin approves a change request, offer a "Re-generate with this change" button
- [ ] **Lock/unlock UI** — timetable grid cells should show lock icons; clicking toggles lock via existing API
- [ ] **Version comparison** — show diff between two timetable versions (before/after re-generation)

### Priority 5: Reports Enhancement
- [ ] **Room utilization report** — already partially built; add capacity warnings, peak load periods, free room identification
- [ ] **Teacher load report** — show daily load per teacher, balance metrics
- [ ] **Student gap analysis** — count free periods between classes per section

### Priority 6: Polish & UX
- [ ] **Form validation** — client-side required fields, server-side input sanitization on all POST/PUT
- [ ] **Error toasts** — show user-friendly error messages instead of silent console.error
- [ ] **Loading states** — spinner/skeleton during API calls (generate timetable can take seconds)
- [ ] **Responsive design** — sidebar collapse on mobile
- [ ] **Export/print** — generate PDF or CSV of timetable grid

### Priority 7: Future / Out of Scope for MVP
- [ ] **Real authentication** — server-side sessions, password hashing
- [ ] **OR-Tools CP-SAT solver** — replace backtracking solver via `algorithms/ortools_solver.py`
- [ ] **Academic calendar management** — semester dates, term boundaries
- [ ] **Audit logging** — track who changed what and when
- [ ] **Multi-department support** — scope beyond single department

### File-Specific Notes
| What to change | Where |
|----------------|-------|
| Student timetable filter | `render.js` → `renderTimetable()` |
| Course/section/holiday CRUD | `render.js` → `renderMasterData()` |
| Preference toggles | New section in `render.js`, new PUT route in `server.py` |
| Lock/unlock icons | `render.js` → timetable grid cells |
| Fix publish crash | `server.py` → `do_PUT` handler for `/api/timetable/{id}/publish` |
| Re-optimize after change | `render.js` + `api.js` + `timetable_service.py` |
| Error toasts | `render.js` → add toast container + helper |
| Export PDF/CSV | New `export.js` module |
