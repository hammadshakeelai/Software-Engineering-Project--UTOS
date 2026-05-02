# UTOS — Super Knowledge Base

> **University Timetable Optimization and Management System**
> Consolidated from: `docs/SRS.md`, `FInal Knowledge Base/deep-research-report.md`, `knowledge base/*.docx`, `REAL/questioning the customers.docx`, `temp/Assignment_1.3*.docx`, `temp/Assignment_2.3*.docx`, `New folder/UTOS_SE_Project_Document.docx`, `AGENTS.md`, `CHANGELOG.md`, `app/README.md`, and all source code in `app/`.
>
> **Date:** 2026-05-02 — **Version:** 2.0

---

## 1. What UTOS Actually Is

UTOS is a **web-based weekly class timetable generator** for a single university department. It lets an administrator enter teachers, rooms, courses, sections, and constraints, then generates a clash-free weekly schedule, reviews it, and publishes it for teachers and students.

### What Is Actually Built (the truth)

| Component | Reality |
|-----------|---------|
| **Backend** | Python 3 stdlib HTTP server (`http.server.BaseHTTPRequestHandler`). No frameworks. No pip packages. |
| **Database** | SQLite, auto-created at `app/data/utos.sqlite`. |
| **Frontend** | Vanilla HTML + CSS + JavaScript (ES modules). No build step. No React/Vue. |
| **Solver** | Custom constructive/backtracking heuristic in `app/backend/algorithms/timetable_solver.py`. Not OR-Tools. Not CP-SAT. |
| **Auth** | No real authentication. Frontend-only role selection via localStorage. No passwords, no tokens, no sessions. |
| **Deployment** | Local dev only. `python -m app.backend.server` → `http://127.0.0.1:8000`. |

### What Earlier Docs Described (aspirational — not built)

Several documents (`deep-research-report.md`, `UTOS_Complete_Final_Knowledge_Document.docx`, `Executive Summary.docx`) describe a system using **PostgreSQL, FastAPI, React/Vue, OR-Tools CP-SAT, Docker, CI/CD, audit logs, JWT auth**. None of that exists. Those documents are research plans and design proposals, not descriptions of the current codebase.

---

## 2. Project Identity

- **Full Name:** University Timetable Optimization and Management System
- **Short Name:** UTOS
- **Team Name:** Hakari Bankai (BSAI-4B)
- **Repository:** `SE-Hakari-Bankai`
- **Course:** Software Engineering
- **Scope:** One department, one semester, weekly class timetabling

---

## 3. How to Run

```bash
# Start server (from repo root)
python -m app.backend.server
# → http://127.0.0.1:8000
# Change port: set UTOS_PORT env var

# Run tests
python -B -m unittest discover -v

# Single test
python -m unittest tests.test_solver -v
```

No pip install needed. Python stdlib only.

---

## 4. Architecture (As Built)

```
SE-Hakari-Bankai/
├── app/
│   ├── backend/
│   │   ├── server.py              ← HTTP routing (GET/POST/PUT/DELETE)
│   │   ├── database.py            ← SQLite connection, init, migration
│   │   ├── schema.sql             ← Full CREATE TABLE statements
│   │   ├── seed.py                ← Demo data (5 teachers, 5 rooms, 4 sections, 8 courses)
│   │   ├── migrate.py             ← ALTER TABLE migrations for change_requests
│   │   ├── algorithms/
│   │   │   └── timetable_solver.py ← Backtracking solver
│   │   ├── repositories/
│   │   │   ├── master_data.py     ← CRUD for teachers, rooms, sections, courses
│   │   │   └── timetable_repository.py ← Versions, entries, reports, change requests
│   │   └── services/
│   │       ├── bootstrap_service.py ← Bundles all data for initial load
│   │       └── timetable_service.py ← Orchestrates solver + save
│   ├── frontend/
│   │   ├── index.html             ← Single-page app shell
│   │   ├── scripts/
│   │   │   ├── main.js            ← Entry point, event wiring, RBAC
│   │   │   ├── render.js          ← All UI rendering (login, timetable, CRUD, requests)
│   │   │   ├── api.js             ← Fetch wrappers for all API endpoints
│   │   │   └── state.js           ← Global state object + localStorage persistence
│   │   └── styles/
│   │       ├── base.css           ← Reset, typography, CSS variables
│   │       ├── layout.css         ← App shell grid, sidebar, workspace
│   │       ├── components.css     ← Buttons, forms, cards, request styles
│   │       └── login.css          ← Login screen glass-morphism
│   └── data/
│       └── utos.sqlite            ← Auto-created on first run
├── docs/
│   └── SRS.md                     ← Software Requirements Specification
├── tests/                         ← Unit tests
├── AGENTS.md                      ← Dev rules
└── CHANGELOG.md
```

---

## 5. Database Schema (Actual)

13 tables. SQLite. Created by `schema.sql`, seeded by `seed.py`, migrated by `migrate.py`.

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `users` | Login identities | id, name, email, role, teacher_id (FK), section_id (FK) |
| `teachers` | Teaching staff | id, name, department, max_daily_load |
| `rooms` | Physical rooms | id, code, building, floor, capacity, room_type, features |
| `sections` | Student groups | id, name, department, size |
| `courses` | What gets scheduled | id, code, title, teacher_id (FK), section_id (FK), weekly_sessions, required_room_type |
| `timeslots` | When classes can happen | id, day, start_time, end_time, sort_order, is_morning, is_last_slot |
| `holidays` | Blocked days | id, name, day |
| `teacher_availability` | Per-slot availability | id, teacher_id, timeslot_id, is_available |
| `preferences` | Soft constraint config | id, key, label, enabled, weight, value |

### Timetable Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `timetable_versions` | Generated drafts | id, name, status (draft/published/archived), score, hard_conflicts, soft_penalty, unplaced_count |
| `timetable_entries` | One class in the grid | id, version_id, course_id, teacher_id, section_id, room_id, timeslot_id, locked, status (placed/unplaced) |

### Workflow Table

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `change_requests` | Teacher/coordinator requests | id, requester_id, target_type, target_id, reason, urgency (normal/urgent), preferred_alternative, coordinator_note, admin_response, status (pending/approved/rejected/implemented), created_at |

### Seed Data

- **4 admin-level users:** Timetable Admin, Coordinator, Facility Manager, System Admin
- **5 teachers:** Dr. Ayesha Khan, Dr. Bilal Ahmed, Prof. Sara Malik, Dr. Hamza Noor, Ms. Zainab Ali
- **5 rooms:** A-101 (45), A-204 (60), B-110 lab (60), B-210 (50), C-301 auditorium (80)
- **4 sections:** BSAI-4A (42), BSAI-4B (48), BSSE-6A (35), BSCS-2A (55)
- **8 courses:** SE-301, AI-220, DB-210, OS-240, ML-330, HCI-310, DSA-120, QA-360
- **25 timeslots:** Mon–Fri × 5 periods (08:30–17:00)
- **1 holiday:** Friday (department seminar)
- **5 preferences:** morning, early ending, room proximity, energy saving, traffic reduction
- **2 teacher users + 2 student users** added after core data

---

## 6. API Endpoints (Actual)

### GET
| Path | Returns |
|------|---------|
| `/api/health` | `{ok: true}` |
| `/api/bootstrap` | All master data + latest timetable + reports |
| `/api/master-data` | Teachers, rooms, sections, courses, timeslots, holidays, preferences, users |
| `/api/users` | User list |
| `/api/timetable/latest` | Latest version with entries + reports |
| `/api/change-requests` | All change requests with requester info |

### POST
| Path | Body | Creates |
|------|------|---------|
| `/api/timetable/generate` | (none) | Runs solver, saves version |
| `/api/master-data/teachers` | name, department, max_daily_load | Teacher |
| `/api/master-data/rooms` | code, building, floor, capacity, room_type, features | Room |
| `/api/master-data/sections` | name, department, size | Section |
| `/api/master-data/courses` | code, title, teacher_id, section_id, weekly_sessions, required_room_type | Course |
| `/api/change-requests` | requester_id, target_type, target_id, reason, urgency, preferred_alternative | Change request |

### PUT
| Path | Body | Action |
|------|------|--------|
| `/api/master-data/teachers/{id}` | name, department, max_daily_load | Update teacher |
| `/api/master-data/rooms/{id}` | code, building, floor, capacity, room_type, features | Update room |
| `/api/master-data/sections/{id}` | name, department, size | Update section |
| `/api/master-data/courses/{id}` | code, title, teacher_id, section_id, weekly_sessions, required_room_type | Update course |
| `/api/timetable/entry/{id}/lock` | (none) | Lock entry |
| `/api/timetable/entry/{id}/unlock` | (none) | Unlock entry |
| `/api/timetable/{id}/publish` | (none) | ⚠️ **CRASHES SERVER** — known bug |
| `/api/change-requests/{id}/status` | status, admin_response | Approve/reject with response |
| `/api/change-requests/{id}/note` | note | Coordinator vouch |

### DELETE
| Path | Action |
|------|--------|
| `/api/master-data/teachers/{id}` | Delete teacher |
| `/api/master-data/rooms/{id}` | Delete room |
| `/api/master-data/sections/{id}` | Delete section |
| `/api/master-data/courses/{id}` | Delete course |

---

## 7. Role-Based Access Control (RBAC)

### Roles in the System

| Role | DB Value | What They Can Do |
|------|----------|------------------|
| **Timetable Admin** | `administrator` | Everything: CRUD master data, generate/publish timetable, lock/unlock entries, approve/reject requests |
| **Coordinator** | `coordinator` | View timetable, view reports, submit change requests, vouch/recommend on requests |
| **Teacher** | `teacher` | View timetable, submit change requests with urgency + preferred alternative |
| **Student** | `student` | View dashboard, view own section's timetable only |
| **Facility Manager** | `facility_manager` | View dashboard, view room utilization reports |

### RBAC is Frontend-Only

There is **no backend auth**. All API endpoints are open. The frontend hides UI elements based on `state.currentUser.role` stored in localStorage. This is adequate for a demo but not production-secure.

### Navigation Visibility

| Nav Link | Admin | Coordinator | Teacher | Student | Facility Mgr |
|----------|-------|-------------|---------|---------|--------------|
| Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ |
| Timetable | ✅ | ✅ | ✅ | ✅ | ❌ |
| Requests | ✅ | ✅ | ✅ | ❌ | ❌ |
| Master Data | ✅ | ❌ | ❌ | ❌ | ❌ |
| Reports | ✅ | ✅ | ❌ | ❌ | ✅ |
| Generate/Publish | ✅ | ❌ | ❌ | ❌ | ❌ |

---

## 8. Solver Algorithm (Actual)

**File:** `app/backend/algorithms/timetable_solver.py`
**Type:** Constructive heuristic with bounded backtracking
**NOT:** OR-Tools, CP-SAT, genetic, simulated annealing, ILP, or any external library

### How It Works

1. **Expand** each course into `weekly_sessions` event objects
2. **Sort** events by constrainedness: larger sections first, fewer available teacher slots first
3. **For each event**, rank feasible (room, timeslot) candidates by soft penalty score
4. **Assign** using bounded backtracking with hard constraint checks
5. **Report** placed entries + unplaced entries + quality metrics

### Hard Constraints Enforced
- No teacher assigned to two classes at the same timeslot
- No room double-booked
- No section double-booked
- Room capacity ≥ section size
- No classes on holiday days
- Respect teacher availability

### Soft Penalties Calculated
- Last-slot usage penalty
- Non-morning placement (when morning preference enabled)
- Late-day placement
- Building movement between consecutive classes

### Output Metrics
- `score`: overall quality score
- `hard_conflicts`: should be 0
- `soft_penalty`: weighted sum of preference violations
- `unplaced_count`: events that couldn't be placed
- `distance_to_feasibility`: how far from a complete solution

---

## 9. Change Request Workflow (As Built)

```
Teacher submits request
  → target_type (teacher/room/timing)
  → reason (free text)
  → urgency (normal/urgent)
  → preferred_alternative (optional text)
  → status = "pending"

Coordinator can add a vouch/recommendation note
  → coordinator_note field updated

Admin reviews with full context:
  → sees urgency badge, preferred alternative, coordinator note
  → approves or rejects with optional admin_response text
  → status → "approved" or "rejected"
```

---

## 10. Use Cases (from SRS + Assignments)

| ID | Use Case | Primary Actor | Status in Code |
|----|----------|---------------|----------------|
| UC-01 | Maintain Academic Calendar | Admin | Partial — holidays exist, no semester dates UI |
| UC-02 | Manage Master Data | Admin | ✅ Built — teachers, rooms CRUD forms |
| UC-03 | Configure Constraints & Preferences | Admin | Partial — preferences display, no toggle UI |
| UC-04 | Generate Timetable | Admin | ✅ Built — button triggers solver |
| UC-05 | Review Timetable Quality | Admin | ✅ Built — grid view, conflicts, reports |
| UC-06 | Request Timetable Change | Teacher/Coordinator | ✅ Built — semantic form with urgency |
| UC-07 | Re-optimize After Change | Admin | Partial — can regenerate, no delta optimization |
| UC-08 | Lock Manual Decisions | Admin | ✅ Built — lock/unlock per entry |
| UC-09 | Publish Timetable | Admin | ⚠️ Backend crashes — known bug |
| UC-10 | View Personal Timetable | Teacher/Student | Partial — grid shows all, student filtering planned |
| UC-11 | View Resource Reports | Admin/Facility Mgr | ✅ Built — room utilization + teacher load |
| UC-12 | Manage Users & Roles | System Admin | Not built — seed data only |

---

## 11. Process Model Selection

**Selected:** Incremental Process Model with prototyping as a supporting technique.

**Why Incremental:**
- Requirements evolve after seeing draft timetables
- System is modular (data → constraints → generation → review → publish)
- Each increment produces a testable, working piece
- Manageable overhead for academic project
- Supports staged documentation

**Planned Increments:**
1. Master data and resource setup
2. Constraints and policy configuration
3. Initial timetable generation MVP
4. Review, repair, and controlled re-optimization
5. Publication and operational reporting

**Rejected alternatives:** Waterfall (too rigid), Spiral (too heavy for semester), Agile/XP (good practices but not a formal lifecycle label for the report)

---

## 12. Constraint Catalogue

### Hard Constraints (must never violate)

| ID | Name | Logic |
|----|------|-------|
| C1 | Teacher Conflict | No teacher assigned to 2 classes in same timeslot |
| C2 | Room Conflict | No room used by 2 classes in same timeslot |
| C3 | Section Conflict | No section has 2 classes in same timeslot |
| C4 | Teacher Availability | Class not placed when teacher is unavailable |
| C5 | Holiday Block | No classes on holiday days |
| C6 | Room Capacity | Room capacity ≥ section size |

### Soft Constraints (preferences with penalties)

| ID | Name | Config | Implemented? |
|----|------|--------|-------------|
| C7 | Morning Preference | weight, on/off | ✅ |
| C8 | Early Ending | weight, on/off | ✅ |
| C9 | Room Proximity | weight, on/off | ✅ |
| C10 | Energy Saving (compact buildings) | weight, on/off | ✅ |
| C11 | Traffic Reduction (avoid last slot) | weight, on/off | ✅ |
| C12 | Room Stability | weight, on/off | Not built |
| C13 | Minimum Working Days | weight, on/off | Not built |
| C14 | Balanced Teacher Load | weight, on/off | Not built |

---

## 13. Known Issues & Limitations

1. **`PUT /api/timetable/{id}/publish` crashes the server** — do not use
2. **No real authentication** — anyone can call any API endpoint
3. **Solver is a basic heuristic** — not optimal, not CP-SAT
4. **Student view doesn't filter by section yet** — shows all sections
5. **No preference toggle UI** — preferences are display-only
6. **No course CRUD form in UI** — only teachers and rooms have add/delete forms
7. **Sections cannot be added/deleted from UI** — only via API
8. **No export/print** — planned for later increment
9. **Single department scope only**

---

## 14. Viva Q&A Reference

**Q: What process model did you use?**
A: Incremental. Each increment builds a working slice (data → constraints → solver → review → publish). Prototyping supports early validation but isn't the primary model.

**Q: What's a hard vs soft constraint?**
A: Hard = must never violate (teacher can't teach two classes at once). Soft = preference with a penalty score (prefer morning classes).

**Q: What solver do you use?**
A: A constructive heuristic with bounded backtracking. It sorts events by constrainedness, tries feasible slots, and backtracks if stuck. It is NOT OR-Tools or CP-SAT — those are planned for a future increment.

**Q: How is the data stored?**
A: SQLite database with 13 tables. Auto-created on first server start. Schema in `schema.sql`, seed data in `seed.py`.

**Q: How does RBAC work?**
A: Frontend-only. The user picks a role at login, stored in localStorage. The UI hides/shows navigation and sections based on role. There is no backend authentication.

**Q: What architecture pattern?**
A: Four-layer separation: Frontend (vanilla JS) → Backend API (Python stdlib HTTP) → Repository layer (SQL queries) → SQLite Database. The solver is a separate module behind a service interface.

**Q: Can the solver be replaced?**
A: Yes. The solver interface (`timetable_solver.py`) is called by `timetable_service.py`. Replacing the algorithm requires changing only the solver file, not the UI or API.

**Q: What does the change request workflow look like?**
A: Teacher submits a request with type, reason, urgency, and preferred alternative. Coordinator can add a recommendation note. Admin sees everything and approves/rejects with an optional response.

---

## 15. File Quick Reference

| File | What It Does | When to Edit |
|------|-------------|--------------|
| `app/backend/server.py` | All HTTP routing | Adding new API endpoints |
| `app/backend/schema.sql` | Database schema | Adding new tables/columns |
| `app/backend/seed.py` | Demo data | Adding test data |
| `app/backend/migrate.py` | Schema migrations | Adding columns to existing tables |
| `app/backend/algorithms/timetable_solver.py` | Scheduling algorithm | Improving the solver |
| `app/backend/repositories/master_data.py` | CRUD for teachers/rooms/sections/courses | Changing data access |
| `app/backend/repositories/timetable_repository.py` | Timetable versions, entries, change requests | Changing timetable logic |
| `app/frontend/index.html` | Page structure | Adding new sections |
| `app/frontend/scripts/render.js` | All UI rendering | Changing what users see |
| `app/frontend/scripts/main.js` | Event wiring, RBAC logic | Changing user interactions |
| `app/frontend/scripts/api.js` | API client | Adding new API calls |
| `app/frontend/scripts/state.js` | Global state | Adding new state fields |

---

## 16. Source Documents Index

| Document | Location | What It Contains |
|----------|----------|------------------|
| SRS | `docs/SRS.md` | Authoritative requirements (UC01–UC12, NFRs, data model) |
| Deep Research Report | `FInal Knowledge Base/deep-research-report.md` | Research plan, constraint catalogue, solver comparison, evaluation metrics — **aspirational, not implemented** |
| UTOS Final Knowledge Doc | `FInal Knowledge Base/UTOS_Complete_Final_Knowledge_Document.docx` | Same as deep research report in Word format |
| Process Model Assignment | `temp/Assignment_1.3_Process_Model_Selection_Final.docx` | Why Incremental was chosen over Waterfall/Spiral/Agile |
| High-Level Use Cases | `temp/Assignment_2.3_High_Level_Use_Cases_Final.docx` | UC01–UC08 detailed descriptions |
| Customer Questions | `REAL/questioning the customers.docx` | Stakeholder interview notes |
| FF.docx | `REAL/FF.docx` | Research plan with hypotheses, literature review, data model extensions |
| Combined Assignments | `temp/Combined_Assignments.docx` | Assignments 1+2 merged |
| CMM + Webservers | `CMM + webservers assignment 0.docx` | CMM levels + web server comparison (not UTOS-specific) |
| AGENTS.md | Root | Dev rules: no pip, use stdlib, known bugs, file conventions |
| CHANGELOG.md | Root | Login page fix history |


---

## 17. Solver Code Details (from actual `timetable_solver.py` — 290 lines)

**Class:** `TimetableSolver`
**Config:** `time_limit_seconds=5.0`, `max_nodes=30,000`

### Algorithm Steps (actual code)

1. **Expand events:** Each course generates `weekly_sessions` event objects with all metadata
2. **Sort by pressure:** Events sorted by `(available_slots_for_teacher, -section_size, -weekly_sessions, code)` — most constrained first
3. **Search with backtracking:** `_search(events, index)` recursively tries assignments
4. **Candidate generation:** For each event, tries every `(room, timeslot)` combination that passes hard feasibility
5. **Candidates sorted by:** `(soft_penalty, slot.sort_order, room.capacity)` — lowest penalty first
6. **Best-so-far tracking:** Keeps best solution found (most placed, then lowest penalty)
7. **Pruning:** Skips branches that can't beat current best
8. **Limits:** Stops at 30k nodes or 5 seconds, records partial result

### Hard Feasibility Checks (`_is_hard_feasible`)
- Holiday day → reject
- Teacher unavailable at slot → reject
- Room capacity < section size → reject
- Lab course in non-lab room → reject
- Teacher already at slot → reject
- Section already at slot → reject
- Room already at slot → reject
- Teacher exceeds max_daily_load → reject

### Soft Penalty Calculation (`_soft_penalty`)
- `morning_preference`: +weight if slot is NOT morning
- `traffic_reduction`: +weight if slot IS last slot of day
- `early_ending`: +weight × max(0, day_position - 2) for late slots
- `room_proximity`: +weight × (building_jump + floor_jump) from teacher's last room that day
- `energy_saving`: +weight if no other class in same building that day (new building activation)

### Output
```python
{
    "entries": [...],      # placed classes
    "unplaced": [...],     # couldn't be placed
    "warnings": [...],     # limit warnings
    "metrics": {
        "score": 0-100,
        "hard_conflicts": int,
        "soft_penalty": int,
        "unplaced_count": int,
        "distance_to_feasibility": int,  # sum of section sizes of unplaced
        "search_nodes": int
    }
}
```

---

## 18. System Modeling (from UTOS_SE_Project_Document.docx)

### DFD Level 0 — Context Diagram
Single process "UTOS". External entities: Admin, Coordinator, Teacher, Student, Facility Manager.
- Admin → System: master data, constraints, generate command
- System → Admin: timetable, conflict report
- Coordinator → System: department preferences, approval
- Teacher → System: availability, change requests
- System → Teacher: personal timetable
- Student → System: view request
- System → Student: section timetable
- Facility Manager → System: report request
- System → FM: room utilization reports

### DFD Level 1 — Six Processes, Four Data Stores
| Process | Name | Inputs | Outputs |
|---------|------|--------|---------|
| P1 | Manage Master Data | Admin input → D1 | Stored master data |
| P2 | Configure Constraints | Coordinator input → D2 | Stored constraints |
| P3 | Generate Timetable | D1 + D2 → solver | Draft → D3, conflict report → Admin |
| P4 | Handle Change Requests | Teacher requests → D4 | Updated timetable in D3 |
| P5 | Publish & View Timetable | D3 → Teacher/Student views | Personal/section timetables |
| P6 | Generate Reports | D1 + D3 → FM | Utilization reports |

**Data Stores:** D1 (Master Data), D2 (Constraints & Preferences), D3 (Timetable Versions), D4 (Change Requests)

### DFD Level 2 — Generate Timetable Decomposition
3.1 Validate Input → 3.2 Build Model → 3.3 Run Solver → 3.4 Score Conflicts → 3.5 Save Timetable

### Swimlane Diagram (3 lanes)
- **Admin lane:** Enter data → Define constraints → Trigger generation → Review conflicts → Publish
- **System lane:** Validate data → Run solver → Detect conflicts → Store timetable
- **Teacher/Student lane:** View published timetable → Submit change requests

### Architecture (as described in doc — NOT what's built)
The doc describes: React/Vue frontend, FastAPI backend, PostgreSQL, OR-Tools CP-SAT.
**Reality:** Vanilla JS, Python stdlib HTTP, SQLite, custom backtracking solver.

---

## 19. Evaluation Metrics (from UTOS_Complete_Final_Knowledge_Document.docx)

### Feasibility Metrics
- Hard violations count (should be 0)
- Teacher/room/section conflict counts
- Holiday violations, capacity violations
- Unplaced sessions count

### Quality Metrics
- Soft penalty score (weighted sum)
- Room utilization %
- Teacher load balance
- Student gap count
- Late class count
- Morning preference satisfaction
- Room proximity score
- Building movement score
- Energy compaction score

### Performance Metrics
- Generation runtime
- Conflict checking runtime
- Timetable loading time
- Number of sessions scheduled / rooms used / timeslots used

### Repair Metrics
- Number of changed entries after re-optimization
- Locked entries preserved
- Affected teachers/sections
- Distance from original timetable

---

## 20. Testing Plan (from UTOS_Complete_Final_Knowledge_Document.docx)

### Unit Tests
- Teacher/room/section conflict detection
- Room capacity check
- Holiday check, timeslot overlap
- Lock preservation, change request status

### Integration Tests
- Frontend form → backend
- Backend → database
- Backend → solver
- Solver result → database
- Publish → teacher/student view
- Change request → re-optimization

### System Tests
- Generate with small/medium/infeasible datasets
- Generate with holidays, unavailable teachers, limited rooms
- Generate with locked entries, after change requests

### Acceptance Tests
- Admin can maintain data, configure constraints, generate, review, publish
- Teacher can view timetable, request changes
- Student can view section timetable
- Facility Manager can view reports

---

## 21. UI Screen Plan (from UTOS_Complete_Final_Knowledge_Document.docx)

### Planned (25 screens)
Login, Dashboard, Teacher/Course/Room/Section/Timeslot management, Academic calendar, Holidays, Constraint config, Preference weights, Teacher availability, Generate timetable, Solver progress, Conflict report, Timetable grid, Manual edit, Lock/unlock, Change request form, Change request review, Version comparison, Publish, Teacher view, Student view, Room utilization report, Export, User management

### Actually Built (as of 2026-05-02)
Login, Dashboard, Timetable grid, Master Data (teachers + rooms CRUD), Reports (room util + teacher load), Change Requests (semantic form + coordinator vouch + admin response)

### Not Built Yet
Course/section/timeslot management forms, Academic calendar, Constraint toggle UI, Teacher availability editor, Solver progress, Manual edit/drag-drop, Version comparison, Export, User management

---

## 22. Risk Register (from UTOS_Complete_Final_Knowledge_Document.docx)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Incomplete input data | High | High | Add validation and warnings before generation |
| Solver too complex | Medium | High | Start with simple heuristic, improve later |
| Scope creep | High | Medium | Stick to incremental plan, defer non-essential features |

---

## 23. Custom Policy Ideas (from Knowledge Documents)

| Policy | Type | Description | Status |
|--------|------|-------------|--------|
| Continuous classing | Soft pref | Group classes to reduce idle time/gaps | Not built (related to compactness) |
| Energy saving | Soft pref | Fewer active buildings, compact room usage | ✅ Built in solver |
| Traffic reduction | Soft pref | Avoid last slot, minimize building transitions | ✅ Built in solver |
| Morning preference | Soft pref | Optional — research warns early starts hurt attendance | ✅ Built in solver |
| Early ending | Soft pref | Penalize classes after threshold time | ✅ Built in solver |
| Minimal perturbation | Workflow | Keep changes small during re-optimization | Not built (planned) |

---

## 24. Document Sources (Complete Inventory)

| # | Document | Lines Read | Content Type |
|---|----------|-----------|--------------|
| 1 | `docs/SRS.md` | 235/235 (full) | Authoritative requirements |
| 2 | `FInal Knowledge Base/deep-research-report.md` | 413/413 (full) | Research plan (aspirational) |
| 3 | `FInal Knowledge Base/UTOS_Complete_Final_Knowledge_Document.docx` | ~800 (full) | Comprehensive knowledge doc |
| 4 | `New folder/UTOS_SE_Project_Document.docx` | ~440 (full) | SE project document with DFDs |
| 5 | `temp/Assignment_2.3_High_Level_Use_Cases_Final.docx` | 230/230 (full) | Use cases UC01-UC10 |
| 6 | `temp/Assignment_1.3_Process_Model_Selection_Final.docx` | 119/119 (full) | Process model selection |
| 7 | `knowledge base/Executive Summary.docx` | ~30 (partial) | Executive summary |
| 8 | `REAL/questioning the customers.docx` | ~80 (partial) | Stakeholder interviews |
| 9 | `REAL/FF.docx` | ~60 (partial) | Research hypotheses |
| 10 | `CMM + webservers assignment 0.docx` | 52/52 (full) | CMM levels + web servers |
| 11 | `Capability Maturity Model Integration (CMMI).txt` | 6/6 (full) | CMMI summary |
| 12 | `CLAUDE.md` | 185 (40 read) | Dev guidance for Claude |
| 13 | `AGENTS.md` | Full (via user rules) | Dev rules |
| 14 | `CHANGELOG.md` | 24/24 (full) | Login fix history |
| 15 | `app/README.md` | 24/24 (full) | App run instructions |
| 16 | `app/backend/schema.sql` | 121/121 (full) | DB schema |
| 17 | `app/backend/server.py` | 280/280 (full) | API routes |
| 18 | `app/backend/database.py` | 41/41 (full) | DB connection |
| 19 | `app/backend/seed.py` | 139/139 (full) | Seed data |
| 20 | `app/backend/migrate.py` | 26/26 (full) | Schema migration |
| 21 | `app/backend/algorithms/timetable_solver.py` | 290/290 (full) | Solver algorithm |
| 22 | `app/backend/repositories/timetable_repository.py` | 210/210 (full) | Timetable data access |
| 23 | `app/frontend/scripts/render.js` | 662/662 (full) | UI rendering |
| 24 | `app/frontend/scripts/main.js` | ~119 (full, prior session) | Event wiring |
| 25 | `app/frontend/scripts/api.js` | 118/118 (full) | API client |
| 26 | `app/frontend/scripts/state.js` | 53/53 (full) | State management |
| 27 | `app/frontend/index.html` | 219/219 (full) | Page structure |

**Not read:** `diagrams_only.docx` (binary), PDFs (5 files), `temp/JUNK/*`, earlier assignment drafts (1.2, 2.2), `master_data.py`, `bootstrap_service.py`, `timetable_service.py`, CSS files (except components.css partial)

---

*Last updated: 2026-05-02 20:12 PKT*
