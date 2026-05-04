# UTOS Application Audit Report
# Generated: 2026-05-02
# Project: SE-Hakari-Bankai (University Timetable Optimization System)

================================================================================
1. PROJECT STRUCTURE
================================================================================

SE-Hakari-Bankai/
├── app/
│   ├── backend/                    # Python HTTP server (stdlib only, no frameworks)
│   │   ├── server.py              # Main HTTP handler + routing (283 lines)
│   │   ├── database.py           # SQLite connection manager (41 lines)
│   │   ├── schema.sql           # Database schema (120 lines, 13 tables)
│   │   ├── seed.py              # Initial data seeder (138 lines)
│   │   ├── migrate.py           # Schema migrations (25 lines)
│   │   ├── algorithms/
│   │   │   └── timetable_solver.py   # Scheduling algorithm (289 lines)
│   │   ├── repositories/
│   │   │   ├── master_data.py         # Teachers/Rooms/Sections/Courses CRUD (138 lines)
│   │   │   └── timetable_repository.py # Timetable versioning + reports (215 lines)
│   │   └── services/
│   │       ├── timetable_service.py  # Generate timetable orchestration (22 lines)
│   │       └── bootstrap_service.py # Initial payload for frontend (15 lines)
│   ├── frontend/                 # Vanilla JS/CSS (no build step)
│   │   ├── index.html          # Single page app shell (219 lines)
│   │   └── scripts/
│   │       ├── main.js         # App entry, event handlers, RBAC (204 lines)
│   │       ├── api.js         # Fetch wrappers for all API calls (117 lines)
│   │       ├── render.js      # UI rendering (662 lines)
│   │       └── state.js      # Global state object (52 lines)
│   └── data/
│       └── utos.sqlite       # SQLite database (auto-created)
└── tests/
    ├── test_solver.py
    └── test_integration.py

================================================================================
2. DATABASE SCHEMA (13 TABLES)
================================================================================

TABLE: users
  - id INTEGER PRIMARY KEY
  - name TEXT NOT NULL
  - email TEXT NOT NULL UNIQUE
  - role TEXT CHECK (administrator, coordinator, teacher, student, facility_manager, system_admin)
  - teacher_id INTEGER REFERENCES teachers(id)
  - section_id INTEGER REFERENCES sections(id)

TABLE: teachers
  - id INTEGER PRIMARY KEY
  - name TEXT NOT NULL
  - department TEXT NOT NULL
  - max_daily_load INTEGER DEFAULT 4

TABLE: rooms
  - id INTEGER PRIMARY KEY
  - code TEXT NOT NULL UNIQUE
  - building TEXT NOT NULL
  - floor INTEGER DEFAULT 0
  - capacity INTEGER NOT NULL
  - room_type TEXT DEFAULT 'lecture' (lecture/lab/auditorium)
  - features TEXT DEFAULT ''

TABLE: sections
  - id INTEGER PRIMARY KEY
  - name TEXT NOT NULL UNIQUE
  - department TEXT NOT NULL
  - size INTEGER NOT NULL

TABLE: courses
  - id INTEGER PRIMARY KEY
  - code TEXT NOT NULL UNIQUE
  - title TEXT NOT NULL
  - teacher_id INTEGER NOT NULL REFERENCES teachers(id)
  - section_id INTEGER NOT NULL REFERENCES sections(id)
  - weekly_sessions INTEGER DEFAULT 2
  - required_room_type TEXT DEFAULT 'lecture'

TABLE: timeslots
  - id INTEGER PRIMARY KEY
  - day TEXT NOT NULL (Monday-Friday)
  - start_time TEXT NOT NULL
  - end_time TEXT NOT NULL
  - sort_order INTEGER NOT NULL
  - is_morning INTEGER DEFAULT 0
  - is_last_slot INTEGER DEFAULT 0

TABLE: holidays
  - id INTEGER PRIMARY KEY
  - name TEXT NOT NULL
  - day TEXT NOT NULL UNIQUE

TABLE: teacher_availability
  - id INTEGER PRIMARY KEY
  - teacher_id INTEGER NOT NULL REFERENCES teachers(id)
  - timeslot_id INTEGER NOT NULL REFERENCES timeslots(id)
  - is_available INTEGER DEFAULT 1

TABLE: preferences
  - id INTEGER PRIMARY KEY
  - key TEXT NOT NULL UNIQUE
  - label TEXT NOT NULL
  - enabled INTEGER DEFAULT 1
  - weight INTEGER DEFAULT 1
  - value TEXT DEFAULT ''

TABLE: timetable_versions
  - id INTEGER PRIMARY KEY
  - name TEXT NOT NULL
  - status TEXT DEFAULT 'draft' (draft/published/archived)
  - score INTEGER DEFAULT 0
  - hard_conflicts INTEGER DEFAULT 0
  - soft_penalty INTEGER DEFAULT 0
  - unplaced_count INTEGER DEFAULT 0
  - distance_to_feasibility INTEGER DEFAULT 0
  - created_at TEXT DEFAULT CURRENT_TIMESTAMP

TABLE: timetable_entries
  - id INTEGER PRIMARY KEY
  - version_id INTEGER REFERENCES timetable_versions(id)
  - course_id INTEGER REFERENCES courses(id)
  - teacher_id INTEGER REFERENCES teachers(id)
  - section_id INTEGER REFERENCES sections(id)
  - room_id INTEGER REFERENCES rooms(id)
  - timeslot_id INTEGER REFERENCES timeslots(id)
  - event_uid TEXT NOT NULL
  - locked INTEGER DEFAULT 0
  - status TEXT DEFAULT 'placed' (placed/unplaced)

TABLE: change_requests
  - id INTEGER PRIMARY KEY
  - requester_id INTEGER REFERENCES users(id)
  - target_type TEXT NOT NULL (teacher/room/timing)
  - target_id INTEGER
  - reason TEXT NOT NULL
  - urgency TEXT DEFAULT 'normal' (normal/urgent)
  - preferred_alternative TEXT DEFAULT ''
  - coordinator_note TEXT DEFAULT ''
  - admin_response TEXT DEFAULT ''
  - status TEXT DEFAULT 'pending' (pending/approved/rejected/implemented)
  - created_at TEXT DEFAULT CURRENT_TIMESTAMP

INDEXES:
  - idx_courses_teacher ON courses(teacher_id)
  - idx_courses_section ON courses(section_id)
  - idx_entries_version ON timetable_entries(version_id)
  - idx_entries_timeslot ON timetable_entries(timeslot_id)

================================================================================
3. API ENDPOINTS
================================================================================

GET  /api/health                  -> Health check
GET  /api/bootstrap              -> Full initial payload (masterData + latestTimetable + reports)
GET  /api/master-data            -> All master data (users, teachers, rooms, sections, courses, timeslots, holidays, preferences)
GET  /api/users                  -> User list
GET  /api/timetable/latest       -> Current draft + reports
GET  /api/change-requests        -> All change requests

POST /api/timetable/generate        -> Run solver, returns versionId + result + reports
POST /api/master-data/teachers    -> Add teacher (name, department, max_daily_load)
POST /api/master-data/rooms     -> Add room (code, building, floor, capacity, room_type, features)
POST /api/master-data/sections     -> Add section (name, department, size)
POST /api/master-data/courses      -> Add course (code, title, teacher_id, section_id, weekly_sessions, required_room_type)
POST /api/change-requests       -> Submit request (requester_id, target_type, target_id, reason, urgency, preferred_alternative)

PUT  /api/timetable/{id}/publish   -> CRASHES SERVER (known issue - AVOID)
PUT  /api/timetable/entry/{id}/lock   -> Lock entry
PUT  /api/timetable/entry/{id}/unlock -> Unlock entry
PUT  /api/master-data/teachers/{id} -> Update teacher
PUT  /api/master-data/rooms/{id}     -> Update room
PUT  /api/master-data/sections/{id} -> Update section
PUT  /api/master-data/courses/{id}  -> Update course
PUT  /api/change-requests/{id}/status -> Update request status
PUT  /api/change-requests/{id}/note   -> Add coordinator note

DELETE /api/master-data/teachers/{id}  -> Delete teacher
DELETE /api/master-data/rooms/{id}   -> Delete room
DELETE /api/master-data/sections/{id}  -> Delete section
DELETE /api/master-data/courses/{id}   -> Delete course

================================================================================
4. SOLVER ALGORITHM (TimetableSolver)
================================================================================

Location: app/backend/algorithms/timetable_solver.py (289 lines)

APPROACH:
- Bounded backtracking search (not optimal - documented as MVP baseline)
- Parameters: time_limit_seconds=5.0, max_nodes=30000

HARD CONSTRAINTS (must satisfy):
1. Room capacity >= section size
2. Room type matches (lab课程→lab room)
3. Teacher available at timeslot
4. Teacher not double-booked (teacher_id + timeslot_id unique)
5. Section not double-booked (section_id + timeslot_id unique)
6. Room not double-booked (room_id + timeslot_id unique)
7. Teacher daily load <= max_daily_load

SOFT PENALTIES (minimize):
- morning_preference: penalty if not morning slot
- traffic_reduction: penalty for last daily slot
- early_ending: penalty for late-day slots
- room_proximity: penalty for building/floor jumps
- energy_saving: penalty for empty buildings

EVENT PRIORITY (sort order):
1. Fewest available slots for teacher
2. Larger section size (more constrained first)
3. More weekly sessions
4. Course code alphabetical

OUTPUT METRICS:
- score: 100 - (hard_conflicts * 15) - soft_penalty
- hard_conflicts: count of unplaced sessions
- soft_penalty: sum of all soft penalties
- unplaced_count: count of unplaced events
- distance_to_feasibility: sum of section sizes for unplaced
- search_nodes: total nodes explored

================================================================================
5. FRONTEND ARCHITECTURE
================================================================================

UI PAGES (5 sections via hash navigation):
1. #dashboard - Stats grid + status panel
2. #timetable - Full weekly grid with section filter
3. #change-requests - Submit form + approval workflow
4. #master-data - Add/delete teachers, rooms (admin only)
5. #reports - Room utilization + teacher load

ROLE-BASED ACCESS CONTROL:

Role          | Dashboard | Timetable | Requests | MasterData | Reports
--------------|-----------|-----------|----------|------------|--------
administrator |    ✓      |     ✓     |    ✓     |     ✓      |   ✓
coordinator   |    ✓      |     ✓     |    ✓     |     ✗      |   ✓
teacher       |    ✓      |   own     |    ✓     |     ✗      |   ✗
student       |    ✓      |   own     |    ✗     |     ✗      |   ✗
facility_mgr   |    ✓      |    ✗     |    ✗     |     ✗      |   ✓

LOGIN SYSTEM:
- Static role cards in index.html (no password)
- User selection persisted to localStorage
- Pre-defined roles: admin, coordinator, teacher, student, facility_manager

STATE MANAGEMENT (state.js):
- currentUser: logged-in user
- masterData: teachers, rooms, sections, courses, timeslots, holidays, preferences
- latestTimetable: current draft with entries
- reports: room_utilization, teacher_load
- changeRequests: all requests
- selectedSection: filter value

RENDER FLOW (render.js):
- renderAll() -> orchestrates all section renders
- renderNav() -> shows/hides nav based on role
- renderStats() -> dashboard stats
- renderTimetable() -> weekly grid
- renderMasterData() -> CRUD forms (admin)
- renderReports() -> utilization reports
- renderChangeRequests() -> workflow forms

================================================================================
6. SEEDED DEMO DATA
================================================================================

TEACHERS (5):
1. Dr. Ayesha Khan - Computer Science, max 4/day
2. Dr. Bilal Ahmed - Computer Science, max 3/day
3. Prof. Sara Malik - Computer Science, max 4/day
4. Dr. Hamza Noor - Artificial Intelligence, max 3/day
5. Ms. Zainab Ali - Software Engineering, max 4/day

ROOMS (5):
1. A-101 - Alpha, floor 1, 45 seats, lecture
2. A-204 - Alpha, floor 2, 60 seats, lecture (smart-board)
3. B-110 - Beta, floor 1, 60 seats, lab (computers)
4. B-210 - Beta, floor 2, 50 seats, lecture
5. C-301 - Core, floor 3, 80 seats, auditorium

SECTIONS (4):
1. BSAI-4A - Artificial Intelligence, 42 students
2. BSAI-4B - Artificial Intelligence, 48 students
3. BSSE-6A - Software Engineering, 35 students
4. BSCS-2A - Computer Science, 55 students

COURSES (8):
1. SE-301 - Software Engineering (Ms. Zainab Ali, BSSE-6A, 2 sessions, lecture)
2. AI-220 - Artificial Intelligence (Dr. Hamza Noor, BSAI-4A, 2 sessions, lecture)
3. DB-210 - Database Systems (Dr. Ayesha Khan, BSCS-2A, 2 sessions, lab)
4. OS-240 - Operating Systems (Dr. Bilal Ahmed, BSCS-2A, 2 sessions, lecture)
5. ML-330 - Machine Learning (Prof. Sara Malik, BSAI-4A, 2 sessions, lab)
6. HCI-310 - Human Computer Interaction (Ms. Zainab Ali, BSSE-6A, 2 sessions, lecture)
7. DSA-120 - Data Structures (Dr. Ayesha Khan, BSCS-2A, 2 sessions, lecture)
8. QA-360 - Software Quality Assurance (Dr. Bilal Ahmed, BSSE-6A, 1 session, lecture)

TIMESLOTS (25):
- Monday-Friday × 5 periods
- 08:30-10:00 (slot 1, morning)
- 10:00-11:30 (slot 2, morning)
- 11:30-13:00 (slot 3)
- 14:00-15:30 (slot 4)
- 15:30-17:00 (slot 5, last)

HOLIDAYS (1):
- Friday (Department seminar day)

TEACHER AVAILABILITY:
- Dr. Bilal Ahmed: NOT available Fridays
- Dr. Hamza Noor: NOT available Fridays AND late slots (15:30+)

PREFERENCES (5):
1. morning_preference - weight 2
2. early_ending - weight 2
3. room_proximity - weight 1
4. energy_saving - weight 1
5. traffic_reduction - weight 3

================================================================================
7. WHAT WORKS / VERIFIED
================================================================================

✅ Python backend starts on http://127.0.0.1:8000
✅ SQLite database auto-creates with schema + seed
✅ Generate timetable runs solver and saves draft
✅ All CRUD operations for master data work
✅ Lock/unlock timetable entries work
✅ Change request workflow works
✅ Role-based navigation visibility works
✅ Reports show room/teacher utilization
✅ Session persistence in localStorage

================================================================================
8. KNOWN ISSUES
================================================================================

❌ PUT /api/timetable/{id}/publish CRASHES SERVER
   - Location: server.py line 131-136
   - Avoid using this endpoint

❌ No user authentication (localStorage-only, no password)
   - Anyone can impersonate any role

⚠️ No export functionality (PDF/CSV/print)
⚠️ No undo for published timetables
⚠️ No version comparison/diff
⚠️ No data validation (empty strings allowed)
⚠️ No pagination (all data loaded at once)

================================================================================
9. ENTRY POINT & RUN
================================================================================

Backend:
  python -m app.backend.server
  # Access at http://127.0.0.1:8000
  # Port can be changed via UTOS_PORT env var

Tests:
  python -B -m unittest discover -v
  python -B -m unittest tests.test_solver -v

================================================================================
END OF AUDIT

================================================================================
## REQUIRED UI SCREENSHOTS FOR DOCUMENTATION

| Screen | Description |
|--------|------------|
| Login | Role selection cards (5 roles) |
| Dashboard | Stats grid + status panel |
| Timetable | Weekly grid view |
| Teacher View | Personal schedule |
| Student View | Section timetable |
| Master Data | Teachers/Rooms CRUD |
| Change Requests | Submit + approval |
| Reports | Room utilization + teacher load |

================================================================================