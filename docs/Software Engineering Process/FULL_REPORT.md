# UTOS — Full Software Engineering Report (Process + All Artifacts)

**Project:** UTOS — University Timetable Optimization System
**Team:** Hakari Bankai · **Author:** Muhammad Hammad Shakeel · **Instructor:** Dr. Sajid Anwar
**Course:** Software Engineering · **Version:** 1.0 · **Live demo:** https://utos.onrender.com

> This is the complete written-out report: every stage and every assignment artifact spelled
> out in full, in the prescribed order. The companion `PROCESS.md` is the shorter "making-of"
> narrative; this file is the content itself. Diagrams that are graphical in the `.docx`
> deliverables are reproduced here as labelled text/ASCII so the document is self-contained.

---

## Table of Contents

0. [Stage 0 — Project Inception](#stage-0--project-inception)
1. [Stage R — Requirements (SRS digest)](#stage-r--requirements-srs-digest)
2. [Assignment 01 — Software Process Model](#assignment-01--software-process-model)
3. [Assignment 02 — Use Cases](#assignment-02--use-cases)
4. [Assignment 03 — Domain Model](#assignment-03--domain-model)
5. [Assignment 04 — Data Flow Diagrams](#assignment-04--data-flow-diagrams)
6. [Assignment 05 — Design Class Diagram](#assignment-05--design-class-diagram)
7. [Assignment 06 — System Sequence Diagrams](#assignment-06--system-sequence-diagrams)
8. [Assignment 07 — Operation Contracts](#assignment-07--operation-contracts)
9. [Design Artifacts — Packages & CRC](#design-artifacts--packages--crc)
10. [Assignment 08 — Final Report Assembly](#assignment-08--final-report-assembly)

---

# Stage 0 — Project Inception

### 0.1 Problem
Manual university timetabling is slow and error-prone: teachers get double-booked, rooms
clash or are too small/of the wrong type, holidays are forgotten, and any single change
forces a tedious manual re-check of the whole week. There is no notion of *versions*, no
audit trail, and no easy way for a teacher or student to see "their" schedule.

### 0.2 Vision
A web application that converts master data (teachers, courses, rooms, sections, timeslots)
into **conflict-free weekly timetables** via a constraint-based solver, with **role-based
access**, manual **locking**, **re-optimization**, a **change-request workflow**,
**versioning/diff**, **publishing**, **notifications**, **reports**, and an **audit log**.

### 0.3 Scope (this iteration)
- **In scope:** single department (Faculty of Computing), class timetabling, the full feature
  set above.
- **Out of scope (Phase 2):** real authentication/passwords, OR-Tools CP-SAT solver, exam
  timetabling module, real academic-calendar dates, multi-department/multi-campus.

### 0.4 Actors (5)
Timetable **Administrator**, Department **Coordinator**, **Teacher**, **Student**, Facility
**Manager**. (A 6th "System Administrator" exists in the full SRS but is out of scope here.)

### 0.5 Technology decisions
- Backend: **Python standard library only** (`http.server`, `sqlite3`, `json`).
- Database: **SQLite** (file-based, versioned).
- Frontend: **vanilla HTML/CSS/JS** — no framework, no build step.
- Solver isolated behind `solve(problem) -> result` for future replacement.

### 0.6 Setup
Git repo, layered folder layout (`app/backend`, `app/frontend`, `tests/`, `tools/`, `docs/`),
and a reproducible documentation toolkit (`build/report/`).

---

# Stage R — Requirements (SRS digest)

The full SRS is `docs/SRS_v1.0_Full_Scope.md`. The requirements **realized in this iteration**
are summarized below. FR identifiers follow the SRS so every later artifact can cite them.

### R.1 Functional requirements (implemented subset)

| ID | Requirement |
|----|-------------|
| **FR-00** | Single-page login with role/account picker; session in `localStorage`, persists across refresh; logout. |
| **FR-01** | Maintain holidays/blocked days; the solver excludes them. |
| **FR-02** | CRUD for teachers (name, department, max_daily_load), rooms (code, building, floor, capacity, room_type, features), sections (name, department, size), courses (code, title, teacher, section, weekly_sessions, required_room_type), timeslots, holidays. |
| **FR-03** | Configure hard constraints (no teacher/room/section clash, capacity ≥ size, lab→lab, holiday exclusion, teacher availability, university hours) and weighted soft preferences (morning, early-ending, room proximity, energy saving, traffic reduction). Per-teacher availability grid. |
| **FR-04** | Generate a complete weekly timetable enforcing all hard constraints, optimizing soft preferences, returning **unplaced sessions with reasons** and a **quality score + penalty breakdown**; runs without blocking the UI. |
| **FR-05** | Review quality: weekly grid, hard-conflict list, soft-penalty breakdown, utilization & teacher-load stats. |
| **FR-06** | Manual locking of entries; locked entries are validated and preserved. |
| **FR-07** | Re-optimize (repair) the draft after an approved change, **minimizing disruption** and keeping locked entries fixed; report a disruption summary. |
| **FR-08** | Publish one official version per term; publishing **archives** the previously published version and **notifies** affected users. |
| **FR-09** | Teachers view their own schedule; students view their section's **published** timetable. |
| **FR-10** | Teachers/coordinators submit change requests with a reason; admins approve/reject/implement; coordinators add recommendations. |
| **FR-11** | Versioning: every generation/repair is a saved version; **compare** any two side-by-side (added/removed/changed + summary counts). |
| **FR-12** | In-app notifications (bell + unread count) on generate, publish, request submit/decision, lock/unlock. |
| **FR-13** | Audit log: every state-changing write records actor (`X-User-Id`), action, entity, old/new values. |
| **FR-14** | Export (CSV) and print stylesheet. |

### R.2 Non-functional requirements

- **NFR-1 Usability** — single-page UI, role-tailored views, one-click actions.
- **NFR-2 Performance** — generation does not freeze the UI; SQLite `busy_timeout=5000` so
  threaded requests wait rather than fail with "database is locked".
- **NFR-3 Reliability/Robustness** — hard constraints are **never** violated even under
  infeasible load (graceful degradation with reasons); every handler runs inside a dispatch
  wrapper that converts exceptions to JSON errors so a bad request never kills the server.
- **NFR-4 Security/Access** — role-based access; write requests carrying `X-User-Id` are
  checked against role permissions (403 on violation); parametrized SQL (injection-safe);
  output escaped on render (XSS-safe).
- **NFR-5 Portability** — backend uses only the Python standard library; no third-party
  runtime dependencies; runs on any host with a long-lived process.
- **NFR-6 Maintainability** — solver isolated behind `solve(problem) -> result`; layered
  architecture; small, loosely-coupled frontend modules.

### R.3 Constraints & business rules
- **Hard constraints (never violated):** no teacher/room/section double-booking; room
  capacity ≥ section size; lab courses → lab rooms; no classes on holidays; teacher
  availability respected; all classes within university hours (08:30–16:00), weekdays only.
- **Soft preferences (weighted 0–10):** morning classes, early endings, room proximity,
  energy saving (building compaction), traffic reduction.
- **Business rules:** exactly one *published* version per term; publishing archives the prior
  published version; a change request must be approved before re-optimization realizes it.

### R.4 Traceability chain
`FR → Use case (A02) → Domain concept (A03) → Design class/operation (A05) → System event
(A06 SSD) → Operation contract (A07) → Test case`.

---

# Assignment 01 — Software Process Model

### A1.1 Survey of candidate models

| Model | Characteristics | Fit for UTOS |
|-------|-----------------|--------------|
| **Waterfall** | Sequential, heavy up-front specification, no overlap, change is expensive. | Poor — our understanding of the **solver/constraints** only matured by building. |
| **Incremental** | System delivered in working increments, each adding value on a stable base. | Strong — features stack cleanly (master data → solver → lock → versioning → publish). |
| **Iterative** | Repeated cycles refine the same product as understanding grows. | Strong — the solver and scoring were refined across cycles. |
| **Spiral** | Risk-driven iterations with prototyping; heavyweight. | Overkill for a course-scale project. |
| **Agile/Scrum** | Time-boxed sprints, backlog, continuous re-prioritization, embraces volatile requirements. | Good fallback if requirements churn. |
| **Prototyping** | Throwaway/evolutionary prototypes to clarify requirements. | Used informally for the solver, not as the overall model. |

### A1.2 Selected model — Iterative & Incremental

**Justification.** UTOS is naturally decomposable into self-contained increments that each
leave a *running* system: (1) master-data CRUD, (2) constraint generation, (3) lock &
re-optimize, (4) change-request workflow, (5) versioning/diff & publishing, (6) reports &
audit. We chose **iterative & incremental** because:

1. **Risk is front-loaded in the solver.** Building a thin end-to-end slice early (generate →
   persist → view) de-risked the hardest part before investing in workflow/reporting.
2. **Requirements were *stable in shape* but *deep in detail*.** We knew the features; what
   we learned by building was *how* constraints and scoring should behave — exactly what
   iterative cycles absorb.
3. **Each increment is independently demonstrable and testable**, which matched our
   test-driven validation of the FRs.
4. **Low integration risk** because every increment builds on an already-working base rather
   than a big-bang integration at the end.

### A1.3 Alternative model — Agile/Scrum

If, at any stage, requirements began to **churn faster than increments could close** — e.g.
stakeholders repeatedly reshaping the role set, the constraint rules, or the approval
workflow — we would switch to **Agile/Scrum**: a prioritized product backlog, short
time-boxed sprints, and a sprint review/retro after each, so priorities are renegotiated
continuously instead of per-increment. **Trigger to switch:** instability of *requirements*
(scope volatility), as opposed to the iterative model's assumption of stable feature shape.

---

# Assignment 02 — Use Cases

### A2.1 Use case diagram (text form)

```
                         ┌──────────────────────── UTOS ─────────────────────────┐
                         │                                                        │
   Administrator ───────►│  UC1 Manage Master Data    UC4 Generate Timetable      │
        │   │   │        │  UC5 Lock / Unlock Entry   UC6 Re-optimize (Repair)     │
        │   │   └───────►│  UC7 Publish Version       UC11 Compare Versions        │
        │   └───────────►│  UC9 Approve/Reject CR     UC10 Re-generate from CR      │
        │               │  UC13 Configure Preferences UC14 Edit Availability        │
   Coordinator ────────►│  UC8 Submit Change Request  UC9a Recommend on CR          │
   Teacher ────────────►│  UC8 Submit Change Request  UC12 View My Timetable        │
        │               │  UC14 Edit My Availability                               │
   Student ────────────►│  UC12 View My (Published) Timetable                       │
   Facility Manager ───►│  UC15 View Reports (utilization / load / gaps)            │
   All actors ─────────►│  UC0 Login    UC16 View Notifications                     │
                         │                                                        │
                         │  «include» UC4 ──▶ UC4a Run Solver                       │
                         │  «include» UC7 ──▶ UC16 Notify Users                     │
                         │  «extend»  UC6  ◀── UC10 Re-generate from CR             │
                         └────────────────────────────────────────────────────────┘
```

### A2.2 High-level use cases (all)

| UC | Name | Primary actor | Summary |
|----|------|---------------|---------|
| UC0 | Login | All | Pick an account/role; session stored in browser. |
| UC1 | Manage Master Data | Administrator | CRUD teachers/rooms/sections/courses/timeslots/holidays. |
| UC4 | Generate Timetable | Administrator | Run the solver to create a new draft version. |
| UC5 | Lock / Unlock Entry | Administrator | Pin an entry so re-optimization preserves it. |
| UC6 | Re-optimize (Repair) | Administrator | Repair the draft preserving locks, minimizing disruption. |
| UC7 | Publish Version | Administrator | Make one version official; archive previous; notify. |
| UC8 | Submit Change Request | Teacher/Coordinator | Request a modification with a reason. |
| UC9 | Approve/Reject Change Request | Administrator | Decide on a request; notify requester. |
| UC9a | Recommend on Request | Coordinator | Attach a recommendation note. |
| UC10 | Re-generate from Approval | Administrator | Apply an approved request and re-optimize; mark implemented. |
| UC11 | Compare Versions | Administrator | Diff two versions (added/removed/changed). |
| UC12 | View My Timetable | Teacher/Student | View own/section published schedule. |
| UC13 | Configure Preferences | Administrator | Enable/disable + weight (0–10) soft preferences. |
| UC14 | Edit Teacher Availability | Admin/Teacher | Mark per-slot availability. |
| UC15 | View Reports | Facility Manager/Admin | Utilization, teacher load, section gaps. |
| UC16 | View Notifications | All | Read in-app notifications. |

### A2.3 Expanded (fully-dressed) use cases

#### UC4 — Generate Timetable

| Field | Content |
|-------|---------|
| **Scope** | UTOS |
| **Level** | User goal |
| **Primary actor** | Timetable Administrator |
| **Stakeholders & interests** | *Admin:* wants a conflict-free schedule fast. *Teachers/Students:* want a feasible, fair timetable. *Facility Mgr:* wants balanced room use. |
| **Preconditions** | Master data exists (≥1 teacher, room, section, course); timeslots defined; admin logged in. |
| **Postconditions (success)** | A new `TimetableVersion` (status *draft*) is created with `TimetableEntry` rows for placed sessions; score, hard-conflict count, soft-penalty, and unplaced count are recorded; a notification is created. |
| **Main success scenario** | 1. Admin requests generation. 2. System assembles the solver problem from master data + constraints + preferences. 3. System runs the solver. 4. Solver returns placed entries, unplaced sessions (with reasons), score, conflicts. 5. System persists a new draft version + entries. 6. System records a notification. 7. System returns the version, score, and conflict/unplaced report. |
| **Extensions** | 4a. Some sessions unplaced → each stored with a reason (no room of type / none large enough / teacher unavailable / contention) and shown in the UI. 3a. Infeasible load → solver degrades gracefully, never violating a hard constraint. *a. Any handler error → JSON error response, server stays alive. |
| **Special requirements** | Non-blocking UI; deterministic enough to re-run. |
| **Frequency** | Several times per scheduling session. |

#### UC7 — Publish Version

| Field | Content |
|-------|---------|
| **Primary actor** | Timetable Administrator |
| **Preconditions** | A draft version exists and is selected; admin logged in. |
| **Postconditions (success)** | The selected version's status → *published*; any previously published version (same term) → *archived*; affected teachers/students receive notifications; the published timetable becomes the role-filtered view source. |
| **Main success scenario** | 1. Admin selects a draft and requests publish. 2. System archives the current published version (if any). 3. System sets the selected version to *published*. 4. System creates notifications for affected users. 5. System confirms. |
| **Extensions** | 2a. No prior published version → skip archive. *a. Unknown version id → 404. *b. Handler error → JSON error (the historical publish crash is fixed and regression-tested). |

#### UC8 — Submit Change Request

| Field | Content |
|-------|---------|
| **Primary actor** | Teacher (or Coordinator) |
| **Preconditions** | Actor logged in; a target entry/course exists. |
| **Postconditions (success)** | A `ChangeRequest` (status *pending*) is created linking requester → target with a reason; admins/coordinators are notified. |
| **Main success scenario** | 1. Actor selects a target and enters a reason. 2. System validates input. 3. System creates the request. 4. System notifies admins/coordinators. 5. System returns the request id. |
| **Extensions** | 2a. Missing/invalid fields → 400. |

#### UC6 — Re-optimize (Repair)

| Field | Content |
|-------|---------|
| **Primary actor** | Timetable Administrator |
| **Preconditions** | A draft version exists; zero or more entries are locked. |
| **Postconditions (success)** | A repaired version is produced; **locked entries are unchanged**; disruption (count of moved entries) is minimized and reported; score/conflict metrics updated. |
| **Main success scenario** | 1. Admin requests re-optimization (optionally tied to an approved change request). 2. System pre-assigns locked entries. 3. System re-runs the solver over the remaining sessions. 4. System persists the repaired version and a disruption summary. 5. System returns the summary. |
| **Extensions** | 1a. Triggered from an approved request → mark that request *implemented* (UC10). |

#### UC1 — Manage Master Data (representative: Add Teacher)

| Field | Content |
|-------|---------|
| **Primary actor** | Timetable Administrator |
| **Preconditions** | Admin logged in. |
| **Postconditions (success)** | A new `Teacher` row is created with a generated id; the action is audited (actor, entity, new values). |
| **Main success scenario** | 1. Admin submits name, department, max_daily_load. 2. System validates (string lengths, numeric load). 3. System inserts the teacher and commits. 4. System audits the write. 5. System returns 201 + id. |
| **Extensions** | 2a. Invalid field → 400. 3a. Delete path: if the entity is referenced by a saved timetable (room/timeslot in use) → 409. |

#### UC0 — Login

| Field | Content |
|-------|---------|
| **Primary actor** | Any user |
| **Preconditions** | The account list is loaded. |
| **Postconditions (success)** | `state.currentUser` is set and persisted in `localStorage`; role-appropriate views are shown. |
| **Main success scenario** | 1. User opens the app. 2. System lists accounts per role (searchable). 3. User selects their account. 4. System stores the session and renders their role's views. |
| **Extensions** | *a. Session already in `localStorage` → auto-restore on refresh. |

---

# Assignment 03 — Domain Model

### A3.1 Conceptual classes, attributes, associations

```
        ┌──────────────┐            teaches            ┌──────────────┐
        │   Teacher    │1 ───────────────────────────* │   Course     │
        │──────────────│                               │──────────────│
        │ name         │                       *┌──────│ code, title  │
        │ department   │                        │      │ weekly_sess. │
        │ max_daily_ld │                        │      │ req_room_type│
        └──────┬───────┘                        │      └──────┬───────┘
               │1                               │1 belongs to │ scheduled as
               │ availability                   │             │
        ┌──────┴────────────┐            ┌───────┴──────┐      │*
        │TeacherAvailability│*          │   Section    │      │
        │───────────────────│           │──────────────│      │
        │ is_available      │           │ name, dept   │      │
        └─────────┬─────────┘           │ size         │      │
                  │* for slot           └──────┬───────┘      │
                  │                            │ for          │
        ┌─────────┴────┐                       │*             │
        │   Timeslot   │1*─────────────────────┘              │
        │──────────────│                                      │
        │ day, start,  │◄──────────────occupies───────────────┤
        │ end, is_morn │                                      │
        │ is_last_slot │              ┌──────────────┐        │
        └──────┬───────┘              │     Room     │        │
               │ blocked by           │──────────────│ in     │
        ┌──────┴───────┐              │ code, bldg   │1*───────┤
        │   Holiday    │              │ floor, cap   │        │
        │──────────────│              │ room_type    │        │
        │ name, day    │              │ features     │        │
        └──────────────┘              └──────────────┘        │
                                                              │
        ┌───────────────────┐ 1        contains          *   │
        │ TimetableVersion  │────────────────────────► TimetableEntry ◄┘
        │───────────────────│                          │──────────────│
        │ name, status      │                          │ event_uid    │
        │ score             │                          │ locked       │
        │ hard_conflicts    │                          │ status       │
        │ soft_penalty      │                          │ reason       │
        │ unplaced_count    │                          └──────────────┘
        │ created_at        │
        └───────────────────┘

        ┌───────────────┐  about  ┌──────────────┐    ┌──────────────┐
        │ ChangeRequest │────────►│ (target)     │    │ Preference   │
        │───────────────│         │ Course/Entry │    │──────────────│
        │ reason,status │         └──────────────┘    │ key, label   │
        │ created_at    │                             │ enabled,     │
        └──────┬────────┘                             │ weight,value │
               │ raised by                            └──────────────┘
        ┌──────┴───────┐    ┌──────────────┐   ┌──────────────┐
        │     User     │    │ Notification │   │  AuditEntry  │
        │──────────────│    │──────────────│   │──────────────│
        │ name, email  │1  *│ message,read │   │ actor,action │
        │ role         │───►│ created_at   │   │ entity,old/new│
        │ teacher_id?  │    └──────────────┘   └──────────────┘
        │ section_id?  │
        └──────────────┘
```

### A3.2 Key associations & multiplicities

- Teacher `1` ── teaches ── `*` Course
- Section `1` ── enrolls in ── `*` Course
- Course `1` ── scheduled as ── `*` TimetableEntry
- TimetableVersion `1` ── contains ── `*` TimetableEntry
- TimetableEntry `*` ── occupies ── `1` Timeslot, `*` ── in ── `1` Room
- Teacher `1` ── has ── `*` TeacherAvailability ── `*` for ── `1` Timeslot
- Holiday `*` ── blocks ── `*` Timeslot/day
- User `1` ── raises ── `*` ChangeRequest; User `1` ── receives ── `*` Notification
- (Domain model carries **concepts + attributes + multiplicities only — no methods**.)

---

# Assignment 04 — Data Flow Diagrams

### A4.1 Level 0 — Context diagram

```
   Administrator ──(master data, generate/publish/lock cmds)──►┌─────────┐
   Coordinator  ──(recommendations, approvals)────────────────►│         │
   Teacher      ──(availability, change requests)─────────────►│  UTOS   │──► Teacher/Student
   Student      ──(login)────────────────────────────────────►│ (System)│   (published timetable)
   Facility Mgr ──(report requests)──────────────────────────►│         │──► All (notifications)
                ◄─(timetables, reports, notifications, status)─└─────────┘
```

### A4.2 Level 1 — Major processes & data stores

```
 External entities: Administrator, Coordinator, Teacher, Student, Facility Manager

  1.0 Manage Master Data ───────► D1 Master Data (teachers/rooms/sections/courses/timeslots/holidays)
  2.0 Generate / Optimize ──reads D1, D3──► writes D2 Timetable Versions & Entries
  3.0 Lock & Re-optimize ──reads D2──► writes D2 (repaired version, locks preserved)
  4.0 Change-Request Workflow ──► D4 Change Requests   ──► (feeds 3.0 on approval)
  5.0 Publish & Notify ──reads D2──► updates D2 status ──► writes D5 Notifications
  6.0 Reporting & Audit ──reads D1,D2──► reports;  all writes ──► D6 Audit Log
  0.0 Authn/Session ──► (role gate for 1.0–6.0)

  Data stores: D1 Master Data · D2 Timetable Versions/Entries · D3 Preferences/Availability
               D4 Change Requests · D5 Notifications · D6 Audit Log
```

### A4.3 Level 2 — Explode "2.0 Generate / Optimize"

```
  2.1 Build solver problem  ◄── D1 Master Data, D3 Preferences/Availability, D1 Holidays
  2.2 Run solver (construct + backtrack)  ── placed entries, unplaced+reasons
  2.3 Score & detect conflicts            ── score, hard_conflicts, soft_penalty
  2.4 Persist new draft version           ──► D2 Timetable Versions/Entries
  2.5 Emit notification                   ──► D5 Notifications
```

### A4.4 Functional hierarchy

```
UTOS
├── 0  Authentication & Session
├── 1  Manage Master Data
│   ├── 1.1 Teachers   1.2 Rooms   1.3 Sections
│   ├── 1.4 Courses    1.5 Timeslots 1.6 Holidays
│   └── 1.7 Preferences & Availability
├── 2  Generate / Optimize
│   ├── 2.1 Build problem  2.2 Run solver  2.3 Score
│   └── 2.4 Persist version 2.5 Notify
├── 3  Lock & Re-optimize
├── 4  Change-Request Workflow (submit → recommend → approve/reject → implement)
├── 5  Publish & Notify
└── 6  Reporting & Audit (utilization · teacher load · section gaps · audit log)
```

**Balancing:** every flow entering/leaving a parent process re-appears in its child diagram
(e.g. 2.0's inputs D1/D3 and output D2 reconcile with 2.1–2.5).

---

# Assignment 05 — Design Class Diagram

### A5.1 Classes, attributes, methods, relationships

```
┌───────────────────────────┐        ┌────────────────────────────────┐
│        Server             │        │      BootstrapService          │
│  (ThreadingHTTPServer +   │ uses   │────────────────────────────────│
│   RequestHandler)         │───────►│ + get_bootstrap(): dict        │
│───────────────────────────│        └───────────────┬────────────────┘
│ + do_GET() do_POST()      │                        │ uses
│ + do_PUT() do_DELETE()    │        ┌───────────────┴────────────────┐
│ - dispatch(handler)       │ uses   │      TimetableService          │
│ - route(path): handler    │───────►│────────────────────────────────│
└──────────┬────────────────┘        │ + generate(problem): Version    │
           │ uses                    │ + reoptimize(...): Summary      │
           │                         └───┬───────────────────┬────────┘
   ┌───────┴───────────┐                 │ uses              │ uses
   │MasterDataRepository│                ▼                   ▼
   │────────────────────│      ┌──────────────────┐  ┌──────────────────────┐
   │+ get_master_data() │      │ TimetableSolver  │  │ TimetableRepository  │
   │+ insert_teacher()  │      │──────────────────│  │──────────────────────│
   │+ update_teacher()  │      │+ solve(problem):  │  │+ get_latest_version()│
   │+ delete_teacher()  │      │     result        │  │+ lock_entry(id)      │
   │+ insert_room() ... │      │- _preassign_locked│  │+ unlock_entry(id)    │
   │  (rooms/sections/  │      │- _construct()     │  │+ publish_version(id) │
   │   courses/slots/   │      │- _backtrack()     │  │+ insert_change_req() │
   │   holidays)        │      │- _score()         │  │+ get_change_requests()│
   └─────────┬──────────┘      └──────────────────┘  │+ update_cr_status()  │
             │ reads/writes                          └──────────┬───────────┘
             ▼                                                  │ reads/writes
        ┌─────────────────────────── Database (SQLite) ─────────┴────┐
        │  connection factory · schema.sql · seed · busy_timeout=5000 │
        └─────────────────────────────────────────────────────────────┘

Entities (data classes mirroring schema):
  Teacher, Room, Section, Course, Timeslot, Holiday, TeacherAvailability,
  Preference, TimetableVersion 1◇──* TimetableEntry, ChangeRequest, User,
  Notification, AuditEntry
```

### A5.2 Relationships & multiplicities

- `Server` `1` ──► `*` Repository/Service (dependency; routes requests).
- `TimetableService` `1` ──► `1` `TimetableSolver` (**the swappable seam**: depends only on
  `solve(problem) -> result`).
- `TimetableService` / repositories ──► `1` `Database`.
- `TimetableVersion` `1` ◇── `*` `TimetableEntry` (composition).
- `TimetableEntry` `*` ──► `1` Course, `1` Teacher, `1` Section, `1` Room, `1` Timeslot.
- Visibility: `+` public handler/repo methods, `-` private helpers (`_construct`,
  `_backtrack`, `_score`, `dispatch`).

---

# Assignment 06 — System Sequence Diagrams

Each SSD shows the actor, the `:System` black box, and the boundary-crossing events. Returns
are shown with `◄--`.

### A6.1 Generate Timetable
```
Administrator        :System
     │  generateTimetable()        │
     │ ───────────────────────────►│
     │                             │ (build problem, run solver, persist draft, notify)
     │  ◄-- version, score, conflicts, unplaced[]
```

### A6.2 Publish Version
```
Administrator        :System
     │  publishVersion(versionId)  │
     │ ───────────────────────────►│
     │                             │ (archive prev published, set published, notify users)
     │  ◄-- confirmation
```

### A6.3 Lock / Unlock Entry
```
Administrator        :System
     │  lockEntry(entryId)         │ ──►│  ◄-- ok
     │  unlockEntry(entryId)       │ ──►│  ◄-- ok
```

### A6.4 Re-optimize (Repair)
```
Administrator        :System
     │  reoptimize(versionId?)     │
     │ ───────────────────────────►│ (preassign locks, re-solve rest, persist)
     │  ◄-- repairedVersion, disruptionSummary
```

### A6.5 Submit Change Request
```
Teacher              :System
     │  submitChangeRequest(target, reason) │ ──►│ (validate, create, notify admins)
     │  ◄-- requestId
```

### A6.6 Approve / Reject Change Request
```
Administrator        :System
     │  updateChangeRequestStatus(id, decision) │ ──►│ (update, notify requester)
     │  ◄-- ok
```

### A6.7 Re-generate from Approval (loop+alt)
```
Administrator        :System
     │  regenerateFromRequest(reqId) │ ──►│  alt[approved]: mark implemented, reoptimize
     │  ◄-- repairedVersion           │     [else]: 409
```

### A6.8 Compare Versions
```
Administrator        :System
     │  compareVersions(a, b)      │ ──►│  ◄-- {added[], removed[], changed[], counts}
```

### A6.9 Configure Preference
```
Administrator        :System
     │  configurePreference(key, enabled, weight) │ ──►│  ◄-- ok (weight clamped 0–10)
```

### A6.10 Edit Teacher Availability
```
Teacher/Admin        :System
     │  setAvailability(teacherId, slotId, isAvailable) │ ──►│  ◄-- ok
```

### A6.11 View My Timetable
```
Teacher/Student      :System
     │  getPublishedTimetable(userId) │ ──►│  ◄-- entries filtered to identity
```

### A6.12 View Reports
```
Facility Manager     :System
     │  getReports()               │ ──►│  ◄-- {utilization[], teacherLoad[], sectionGaps[]}
```

---

# Assignment 07 — Operation Contracts

Postconditions are written in the **past tense as state changes** (Larman style).

### Contract CO1: generateTimetable
- **Operation:** `generateTimetable()`
- **Cross-references:** UC4
- **Preconditions:** Master data exists; timeslots defined.
- **Postconditions:**
  - a `TimetableVersion` was created (status = *draft*).
  - `TimetableEntry` instances were created for placed sessions and associated with the version, their Course/Teacher/Section/Room/Timeslot.
  - unplaced sessions were recorded with a `reason`.
  - version.score, .hard_conflicts, .soft_penalty, .unplaced_count were set.
  - a `Notification` was created.

### Contract CO2: publishVersion
- **Operation:** `publishVersion(versionId)`
- **Cross-references:** UC7
- **Preconditions:** version `versionId` exists.
- **Postconditions:**
  - the previously published version (if any) had status changed to *archived*.
  - version[versionId].status was changed to *published*.
  - `Notification` instances were created for affected teachers/students.

### Contract CO3: lockEntry / unlockEntry
- **Operation:** `lockEntry(entryId)` / `unlockEntry(entryId)`
- **Cross-references:** UC5
- **Preconditions:** entry `entryId` exists.
- **Postconditions:** entry[entryId].locked was set to true (resp. false); the action was audited.

### Contract CO4: reoptimize
- **Operation:** `reoptimize(versionId)`
- **Cross-references:** UC6
- **Preconditions:** a draft version exists.
- **Postconditions:**
  - locked `TimetableEntry` instances were preserved unchanged.
  - non-locked entries were re-created from a fresh solve.
  - a disruption summary (count of moved entries) was produced.
  - version score/conflict metrics were updated.

### Contract CO5: submitChangeRequest
- **Operation:** `submitChangeRequest(target, reason)`
- **Cross-references:** UC8
- **Preconditions:** requester is authenticated; target exists.
- **Postconditions:**
  - a `ChangeRequest` was created (status = *pending*) and associated with requester + target.
  - `Notification` instances were created for admins/coordinators.

### Contract CO6: updateChangeRequestStatus
- **Operation:** `updateChangeRequestStatus(id, status)`
- **Cross-references:** UC9
- **Preconditions:** request `id` exists; `status` ∈ {approved, rejected, implemented}.
- **Postconditions:** request[id].status was changed; a `Notification` was created for the requester.

### Contract CO7: insertTeacher (representative master-data create)
- **Operation:** `insertTeacher(name, department, maxDailyLoad)`
- **Cross-references:** UC1
- **Preconditions:** fields valid (non-empty name, numeric load).
- **Postconditions:** a `Teacher` was created with a new id; the write was audited (actor, entity, new values).

### Contract CO8: deleteRoom (representative guarded delete)
- **Operation:** `deleteRoom(roomId)`
- **Cross-references:** UC1
- **Preconditions:** room exists **and is not referenced by any saved timetable** (else 409).
- **Postconditions:** the `Room` was deleted; the write was audited.

### Contract CO9: configurePreference
- **Operation:** `configurePreference(key, enabled, weight)`
- **Cross-references:** UC13
- **Preconditions:** preference `key` exists; `0 ≤ weight ≤ 10`.
- **Postconditions:** preference.enabled and .weight were updated.

### Contract CO10: setAvailability
- **Operation:** `setAvailability(teacherId, slotId, isAvailable)`
- **Cross-references:** UC14
- **Preconditions:** teacher and slot exist.
- **Postconditions:** the `TeacherAvailability` for (teacher, slot) was set to `isAvailable`.

### Contract CO11: compareVersions
- **Operation:** `compareVersions(a, b)`
- **Cross-references:** UC11
- **Preconditions:** versions `a` and `b` exist.
- **Postconditions:** *(query — no state change)* a diff {added, removed, changed} with summary counts was returned.

---

# Design Artifacts — Packages & CRC

### A8.1 Package diagram (text form)

```
        ┌──────────────────────────── frontend ────────────────────────────┐
        │  api.js   state.js   main.js   render.js   (vanilla modules)       │
        └───────────────────────────────┬──────────────────────────────────┘
                                         │ HTTP/JSON (dependency)
        ┌────────────────────────────────▼─────────────────────────────────┐
        │                        backend.server                             │
        └───────────────┬───────────────────────────────┬──────────────────┘
                        │ depends on                     │ depends on
            ┌───────────▼───────────┐         ┌──────────▼───────────┐
            │   backend.services    │────────►│ backend.algorithms   │
            │ (bootstrap, timetable)│         │   (timetable_solver) │
            └───────────┬───────────┘         └──────────────────────┘
                        │ depends on
            ┌───────────▼────────────┐
            │  backend.repositories  │
            │ (master_data, timetable,│
            │  system: notif/audit)  │
            └───────────┬────────────┘
                        │ depends on
            ┌───────────▼────────────┐
            │   backend.database     │  (connection, schema.sql, seed, migrations)
            └────────────────────────┘
```

Dependencies flow strictly **downward** — server → services → repositories → database, and
services → algorithms. No upward or cyclic dependencies (clean layering).

### A8.2 CRC cards

| Class | Responsibilities | Collaborators |
|-------|------------------|---------------|
| **Server / RequestHandler** | Parse HTTP requests; route by path/method; wrap handlers so errors become JSON; enforce role (`X-User-Id`). | Services, Repositories |
| **BootstrapService** | Assemble the initial payload (master data + latest timetable + reports). | MasterDataRepository, TimetableRepository |
| **TimetableService** | Build the solver problem; run the solver; persist the resulting version; produce disruption summary. | MasterDataRepository, TimetableSolver, TimetableRepository |
| **TimetableSolver** | Place sessions satisfying all hard constraints; optimize soft prefs; preserve locked entries; score; explain unplaced. | (pure — receives a problem dict) |
| **MasterDataRepository** | CRUD for teachers/rooms/sections/courses/timeslots/holidays; guard in-use deletes. | Database |
| **TimetableRepository** | Versions, entries, lock/unlock, publish/archive, change requests, notifications, audit. | Database |
| **Database** | Provide SQLite connections; create/seed schema; `busy_timeout`. | (SQLite) |

---

# Assignment 08 — Final Report Assembly

**Task.** Submit the final report following the sample format: title page (project title +
team members), table of contents, and **all artifacts in the prescribed order**.

**Order (as in this document):** Inception → Requirements → Process model → Use cases →
Domain model → DFDs → Design class diagram → System sequence diagrams → Operation contracts →
Packages & CRC → supporting material.

**How it's built.** `build_final.py` calls the same `emit_aNN(...)` body emitters as the
standalone assignments with a heading-level offset (`loff`), so each assignment becomes a
numbered **chapter** under one continuous document — guaranteeing the combined report and the
standalone deliverables never drift. A **Word COM pass** then fills the TOC field with real
page numbers and renders `Assignment_08_Final_Project_Report_PDF.pdf` for visual QA.

**Reproduce from `build/report/`:**
```bash
python extract.py
python build_assignments.py        # A01–A07 .docx
python build_design_artifacts.py   # packages + CRC .docx
python make_package_diagram.py     # UML package diagram (matplotlib)
python build_final.py              # A08 combined report .docx
# then the Word COM (PowerShell) pass updates the TOC and exports the PDF
```
Outputs land in `build/report/out/` and are mirrored to
`docs/FULLY FINAL COMPLETE/Built Reports/`.

---

*End of report.*
