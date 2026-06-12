# UTOS — Software Engineering Process

**Project:** UTOS — University Timetable Optimization System
**Team:** Hakari Bankai · **Author:** Muhammad Hammad Shakeel · **Instructor:** Dr. Sajid Anwar
**Course:** Software Engineering
**Live demo:** https://utos.onrender.com

---

## How to read this document

This is the **process narrative** for the whole project: it explains, in order, *how* every
assignment deliverable was produced, *what* belongs inside each one, the *notation/standard*
it follows, and how each maps to UTOS specifically. Think of it as the index and the
"making-of" for the artifacts that end up in the final report.

The graded artifacts live in two places:

| Stage | What it is | Built deliverable |
|-------|-----------|-------------------|
| **0** | Pre-steps / project inception | this document + repo, vision, scope |
| **R** | Requirements engineering (SRS) | `docs/SRS_v1.0_Full_Scope.md` |
| **01** | Process model selection & justification | `Assignment_01_Process_Model.docx` |
| **02** | Use case diagram + high-level & expanded use cases | `Assignment_02_Use_Cases.docx` |
| **03** | Domain model | `Assignment_03_Domain_Model.docx` |
| **04** | Data Flow Diagrams (L0 context + decomposition) | `Assignment_04_DFD.docx` |
| **05** | Design class diagram | `Assignment_05_Class_Diagram.docx` |
| **06** | System sequence diagrams | `Assignment_06_System_Sequence_Diagrams.docx` |
| **07** | Operation contracts | `Assignment_07_Operation_Contracts.docx` |
| **+** | Packages, package diagram & CRC cards | `Design_Artifacts_Packages_and_CRC.docx` |
| **08** | Final combined project report | `Assignment_08_Final_Project_Report.docx` (+ PDF) |

All of the above are **generated, not hand-typed**, by the toolkit in `build/report/`
(see [§ The build pipeline](#the-build-pipeline)). Final copies are mirrored to
`docs/FULLY FINAL COMPLETE/Built Reports/`.

---

## The build pipeline

Every `.docx` is emitted from Python so the artifacts stay consistent (one title-page style,
one heading scheme, one table look) and are trivially regenerable. The toolkit lives in
`build/report/`:

```
source .docx ──extract.py──► extracted/<stem>.json  +  images/<stem>/*.png
                                      │
                report_builder.py  (Report class: title page, headings,
                                     banded tables, captioned figures, TOC field)
                                      │
        ┌──────────────┬─────────────┼───────────────┬────────────────┐
   build_assignments  build_design   build_final   make_package_      (UI screenshots
   .py (A01–A07)      _artifacts.py  .py (A08)      diagram.py          via html2canvas)
                      (packages+CRC) (whole report) (UML package dia.)
                                      │
                              .docx in build/report/out/
                                      │
                      Word COM pass (PowerShell): Fields.Update()
                      / TablesOfContents.Update()  → real page-numbered TOC
                                      │
                              docx → PDF for visual QA
```

Key conventions baked into `report_builder.py`:

- **Title page** on every deliverable — project title, team, author = *Muhammad Hammad
  Shakeel*, instructor = *Dr. Sajid Anwar*.
- **Numbered headings** (1, 1.1, 1.1.1) so the TOC and cross-references resolve.
- **Banded tables** for use-case fields, contracts, CRC cards.
- **Captioned figures** ("Figure N: …") for every diagram, so they're referenceable.
- **TOC field** is inserted empty by Python, then **populated by a Word COM pass** (Python
  cannot compute page numbers). The same COM pass renders the PDF for QA.

> Tooling note: this machine has Word (COM automation) + matplotlib + PyMuPDF, but **no
> LibreOffice and no Graphviz `dot`**. UML/diagrams that had to be drawn fresh (e.g. the
> package diagram) were rendered with **matplotlib**, not `dot`.

---

# Stage 0 — Pre-Steps / Project Inception

*Everything that has to happen before Assignment 01 can be written.* This stage produces no
graded diagram, but it fixes the decisions every later artifact depends on. If the domain,
scope, and actor set were wrong here, every use case and class downstream would be wrong too.

### 0.1 Problem identification
We chose a problem we genuinely understood as students: **university timetable scheduling**.
Manual timetabling is slow, error-prone (double-booked rooms/teachers, over-capacity rooms),
and hard to revise when one change ripples through the week. That gives a clear pain point
and a clear "win condition" (a *conflict-free* timetable), which matters because Assignments
02–07 all need a system with real, checkable rules — not a vague CRUD app.

### 0.2 Vision & scope
- **Vision:** a web app that turns teachers, courses, rooms and sections into conflict-free
  weekly timetables via a constraint solver, with role-based access for the people who use it.
- **In scope (this iteration):** master-data management, constraint-based generation,
  manual lock + re-optimization, change-request workflow, versioning/diff, publishing,
  notifications, reports, audit log.
- **Out of scope (Phase 2):** real authentication/passwords, an OR-Tools CP-SAT solver,
  exam timetabling, real calendar dates, multi-department scope. Naming these *now* keeps
  the use-case diagram honest.

### 0.3 Stakeholders & actors
We identified **five actor roles**, which become the actors in the Assignment 02 diagram:
Timetable **Administrator**, Department **Coordinator**, **Teacher**, **Student**, and
**Facility Manager**. Each has a distinct goal (admin generates/publishes; coordinator
recommends; teacher/student view their own schedule + request changes; facility manager
watches room utilization).

### 0.4 Requirements elicitation
Functional requirements (FR-01…) and non-functional requirements were captured in the SRS
(`docs/SRS_v1.0_Full_Scope.md`). These FRs are the spine that every use case traces back to.

### 0.5 Technology & environment decisions
Decided up front, because they shape the design class diagram and package diagram:

- **Backend:** Python **standard library only** (`http.server`, `sqlite3`, `json`) — zero
  third-party runtime deps, so it deploys anywhere and there's nothing to "install."
- **Database:** SQLite (file-based, versioned timetables).
- **Frontend:** vanilla HTML/CSS/JS — no framework, no build step.
- **Solver:** isolated behind a `solve(problem) -> result` interface so it can later be
  swapped for OR-Tools without touching the rest of the system.

### 0.6 Project setup
Git repository created, folder structure laid out (`app/backend`, `app/frontend`, `tests/`,
`docs/`, `tools/`), and the documentation toolkit (`build/report/`) established so artifacts
are reproducible rather than hand-maintained.

**Exit criteria for Stage 0:** problem, vision, scope, actor set, FR list, tech stack, and
repo all fixed → we can now do disciplined requirements engineering.

---

# Stage R — Requirements Engineering (the SRS)

*The bridge between "we have an idea" (Stage 0) and "we can model it" (Assignments 02–07).*
This stage turns the rough vision into a written, traceable **Software Requirements
Specification** (`docs/SRS_v1.0_Full_Scope.md`, v1.0). Every use case, domain concept,
class, SSD, and contract downstream is justified by a requirement captured here — so this is
where correctness is anchored.

### R.1 The four activities

1. **Elicitation** — gathering needs. Sources: our own experience of manual timetabling, the
   five stakeholder roles' goals, and the pain points (teacher/room/section clashes, room
   capacity & type mismatches, holiday handling, variable class durations, the difficulty of
   *revising* a published timetable). Techniques: brainstorming, scenario walkthroughs per
   role, and studying how a real faculty timetable behaves.
2. **Analysis & negotiation** — resolving conflicts and priorities. Example trade-offs we
   settled: section-level timetables only (not per-student); a single department for this
   iteration; picker-based login instead of real auth. Each became an explicit **scope
   decision** rather than an accident.
3. **Specification** — writing it down in the SRS structure (below).
4. **Validation** — checking the SRS is complete, consistent, unambiguous, and verifiable;
   every FR must be testable. (Our test suite later validates many FRs directly — e.g.
   "publishing archives the previous published version" is both FR and regression test.)

### R.2 SRS structure (what the document contains)

The SRS is organized as:

1. **Introduction** — purpose, system overview, **problem statement** (why manual
   timetabling is hard at scale).
2. **Scope** — explicit **In Scope** vs **Out of Scope** lists, split across the
   **Class Timetabling** module and the (future) **Exam Timetabling** module. Writing the
   out-of-scope list (no fee/attendance/hostel, no multi-campus, section-level only) is what
   keeps the use-case diagram honest.
3. **Users & Roles** — the actor table (Administrator, Coordinator, Teacher, Student,
   Facility Manager, System Administrator) plus **user characteristics** (skill level,
   intended use). These actors flow straight into Assignment 02.
4. **Functional Requirements** — numbered **FR-xx.y**, grouped by module and by use case
   (UC-00 Authentication, then master-data, generation, locking/re-optimization, change
   requests, publishing, reporting…). The FR numbering is the **traceability key** the rest
   of the project cites.
5. **Non-Functional Requirements** — quality attributes: usability, performance
   (responsive UI, background/non-blocking generation), reliability (no hard-constraint
   violations, server never crashes on bad input), security/role-based access, portability
   (stdlib-only backend), maintainability (swappable solver).
6. **Constraints & assumptions** — hard constraints (no teacher/room/section double-booking,
   room capacity, room type, holidays, teacher daily load) vs **soft preferences** (morning
   classes, early endings, room proximity, energy saving, traffic reduction) — the exact
   split the solver implements.

### R.3 Classifying UTOS requirements

- **Functional** (what the system does): generate a conflict-free timetable, lock an entry,
  re-optimize preserving locks, submit/approve change requests, publish a version, diff two
  versions, produce reports, log every write.
- **Non-functional** (how well): generation runs in the background without freezing the UI;
  the server returns 4xx on malformed/injection/auth-bypass input and stays alive; the
  backend has **zero third-party runtime dependencies**; the solver sits behind a clean
  `solve(problem) -> result` seam so it can be replaced without ripple.
- **Domain/business rules**: a timetable is only "publishable" as one official version per
  term; publishing archives the prior published version; hard constraints can **never** be
  violated even when the load is infeasible (the solver degrades gracefully and reports
  *why* each session is unplaced).

### R.4 Traceability

Requirements are traced forward through every later artifact:

```
FR-xx  →  Use case (A02)  →  Domain concept (A03)  →  Design class/op (A05)
       →  System event (A06 SSD)  →  Operation contract (A07)  →  Test case
```

This chain is what lets us claim the design is *complete* (every FR is realized) and
*justified* (no class or operation exists without a requirement behind it).

### R.5 Validation & the role of tests

Because every FR was written to be **verifiable**, much of the SRS is validated executably:
the `tests/` suite (solver correctness, HTTP API, role enforcement, validation, publishing/
re-optimization, version diff, notifications, adversarial edge cases) plus the `tools/`
red-team and stress seeds confirm the hard-constraint and robustness requirements hold.

**Exit criteria for Stage R:** a validated, numbered SRS with a clear scope boundary and a
testable FR set → we can now choose a *process model* and begin modelling.

---

# Assignment 01 — Software Process Model

**Task:** Pick a software development process model for the project and justify it; then
propose a fallback model to switch to if the first proves unsuitable.

### What goes inside
1. **Brief survey** of candidate models (Waterfall, Incremental, Iterative, Spiral, Agile/
   Scrum, Prototyping) and their defining characteristics — strengths and weaknesses.
2. **The selected model** with explicit justification tied to *this* project's realities.
3. **The alternative/fallback model** and the trigger conditions that would make us switch.

### Our choice and why
- **Selected: Iterative & Incremental development.** UTOS is feature-stacked (master data →
  solver → lock/re-optimize → versioning → publishing → reports). Each is a self-contained
  increment that adds working value on top of a running system, and our understanding of the
  constraints (especially the solver) sharpened *as we built*, which iterative cycles absorb
  naturally. A running thin slice early also de-risked the riskiest part (generation).
- **Fallback: Agile/Scrum.** If requirements churned faster than increments could close —
  e.g. stakeholders kept reshaping roles, constraints, or the workflow — we'd move to short
  time-boxed sprints with a backlog and per-sprint review to re-prioritize continuously.
  The trigger: instability of requirements rather than instability of the build.

### Standard / notation
Prose + a comparison table; optionally a phase diagram of the iterative loop
(plan → design → build → test → evaluate → repeat).

---

# Assignment 02 — Use Case Diagram, High-Level & Expanded Use Cases

**Task:** Build a use-case diagram; for **each** use case give both a **high-level**
description and a **detailed (expanded)** specification.

### What goes inside
1. **Use case diagram** — actors (the five roles + the system/solver as supporting actor),
   use-case ellipses, `<<include>>` / `<<extend>>` relationships, system boundary.
2. **High-level description** per use case: name, primary actor, and a 1–2 sentence summary
   of intent.
3. **Expanded (fully-dressed) use case** per use case, using the standard template:
   - Use case name & ID, scope, level, **primary actor**, **stakeholders & interests**,
   - **Preconditions**, **postconditions (success guarantees)**,
   - **Main success scenario** (numbered steps),
   - **Extensions / alternate flows**, **special requirements**, frequency, open issues.

### UTOS use cases (UC00–UC22)
Generate timetable, Lock/Unlock entry, Re-optimize (repair), Publish version, Submit change
request, Approve/Reject change request, Re-generate from approval, Manage master data
(teachers/rooms/sections/courses/timeslots/holidays), Edit teacher availability, Configure
preferences, Compare versions, View role timetable, View reports, View audit log,
View notifications, Login (role picker). Each traces back to an FR from the SRS.

### Standard / notation
UML use-case diagram + Cockburn-style fully-dressed use-case template (banded two-column
tables in the generated docx).

---

# Assignment 03 — Domain Model

**Task:** Produce a domain model capturing the key concepts, their attributes, and their
relationships.

### What goes inside
1. **Conceptual classes** (domain concepts, *not* software classes) — Teacher, Course,
   Room, Section, Timeslot, Holiday, TimetableVersion, TimetableEntry, ChangeRequest,
   Preference, TeacherAvailability, User/Actor, Notification, AuditEntry.
2. **Attributes** on each concept (e.g. Room: code, building, floor, capacity, room_type,
   features).
3. **Associations** with **multiplicities** and meaningful names (e.g. a *TimetableVersion*
   1—* *TimetableEntry*; a *Course* is taught by 1 *Teacher* to 1 *Section*; a
   *TimetableEntry* occupies 1 *Room* in 1 *Timeslot*).
4. **Association classes / generalizations** where natural (e.g. roles generalizing User).

### Notes for UTOS
The domain model is the conceptual ancestor of the SQLite schema (11 tables) but stays at
the *concept* level — no methods, no foreign-key plumbing, no UI. It's the shared vocabulary
the rest of the analysis uses.

### Standard / notation
UML domain/conceptual class diagram (boxes with concept name + attributes; lines with role
names and multiplicities). **No operations** at this stage.

---

# Assignment 04 — Data Flow Diagrams

**Task:** Build a DFD starting at **Level 0 (context diagram)**, then a functional hierarchy
that decomposes the system into its major processes.

### What goes inside
1. **Level 0 / Context diagram** — UTOS as a single process bubble, the **external entities**
   (the five user roles), and the major **data flows** in/out (login, master-data edits,
   generation requests, published timetables, change requests, notifications, reports).
2. **Level 1** — decomposition into major processes, e.g.
   1.0 Manage Master Data, 2.0 Generate/Optimize Timetable, 3.0 Lock & Re-optimize,
   4.0 Change-Request Workflow, 5.0 Publish & Notify, 6.0 Reporting & Audit — plus the
   **data stores** (Master Data, Timetable Versions, Change Requests, Audit Log, Notifications).
3. **Level 2** (where useful) — e.g. exploding "Generate/Optimize Timetable" into build
   problem → run solver → score & detect conflicts → persist version.
4. A **functional hierarchy** tree mirroring the leveling.

### Standard / notation
Classic DFD notation: process = bubble/rounded rect, external entity = rectangle,
data store = open-ended bar, data flow = labeled arrow. **Balancing rule:** inputs/outputs
at each parent process must reconcile with its child diagram.

---

# Assignment 05 — Design Class Diagram

**Task:** Produce a detailed **class diagram** with classes, attributes, methods, and the
**multiplicities** of the relationships among them.

### What goes inside
1. **Software classes** (the *design* view, unlike A03's concepts): the repositories
   (`MasterDataRepository`, `TimetableRepository`, system/notification & audit access),
   services (`BootstrapService`, `TimetableService`), the solver (`TimetableSolver`), the
   HTTP `Server`/request handler, and the entity classes (Teacher, Room, Section, Course,
   Timeslot, TimetableVersion, TimetableEntry, ChangeRequest, Preference, …).
2. **Attributes with types** and **methods with signatures** (e.g. `TimetableSolver.solve(
   problem: dict) -> dict`; `MasterDataRepository.insert_teacher(...) -> int`).
3. **Relationships** — association, aggregation/composition, dependency — each with
   **multiplicities** (e.g. Server →* Repository; TimetableService → 1 TimetableSolver;
   TimetableVersion ◇—* TimetableEntry).

### Notes for UTOS
This diagram reflects the real 4-layer architecture (Server → Services/Repositories →
Solver → SQLite) and shows the **swappable-solver seam** as a dependency on the `solve()`
interface.

### Standard / notation
UML design class diagram (three-compartment boxes: name / attributes / operations),
visibility markers (+ public, - private), typed members, multiplicities on every association.

---

# Assignment 06 — System Sequence Diagrams

**Task:** For **each** use case (referencing the expanded use cases), develop a **system
sequence diagram** (SSD).

### What goes inside
- One SSD per essential use case, showing the **actor**, the **System** as a single black
  box, and the **time-ordered system events** (messages) the actor sends, plus the system's
  returns. SSDs capture *what crosses the system boundary*, not internal objects.
- Examples:
  - **Generate Timetable:** Admin → `generateTimetable()` → System returns version + score +
    conflict report.
  - **Submit Change Request:** Teacher → `submitChangeRequest(target, reason)` → System
    returns request id; (async) notifies admins.
  - **Publish Version:** Admin → `publish(versionId)` → System archives previous published,
    notifies affected users, returns confirmation.
  - **Lock Entry / Re-optimize / Approve Request / Compare Versions** — one each.
- Loops/alternatives shown with `loop` / `alt` frames where the use case has them.

### Standard / notation
UML sequence diagram with a single `:System` lifeline; messages named as the **system
operations** that will become the contracts in Assignment 07.

---

# Assignment 07 — Operation Contracts

**Task:** For **each operation** identified in the SSDs, write an **operation contract**
using the lecture template.

### What goes inside (per operation)
- **Operation:** signature (name + parameters), e.g. `generateTimetable()`.
- **Cross-references:** the use case(s) it belongs to.
- **Preconditions:** what must be true before (e.g. master data exists; timeslots defined).
- **Postconditions** (the heart of the contract), expressed as state changes:
  - **instances created / deleted** (e.g. a `TimetableVersion` was created; `TimetableEntry`
    instances were created and associated with it),
  - **associations formed / broken** (entries linked to version, room, timeslot, teacher),
  - **attributes modified** (version.status set to *draft*; score/conflict counts set;
    on publish, previous published version.status → *archived*).

### Operations covered for UTOS
`generateTimetable`, `reoptimize`, `lockEntry`/`unlockEntry`, `publishVersion`,
`submitChangeRequest`, `updateChangeRequestStatus`, `insert/update/delete` master-data
operations, `configurePreference`, `editTeacherAvailability`, `compareVersions`. Each is one
contract table.

### Standard / notation
Larman-style contract template (Operation / Cross-References / Preconditions /
Postconditions), postconditions written in the **past tense as state changes**, not as
procedural steps.

---

# Design Artifacts — Packages, Package Diagram & CRC Cards

*(The extra design step, built alongside the assignments as
`Design_Artifacts_Packages_and_CRC.docx`.)*

### Packages & package diagram
- **Purpose:** show the system's logical decomposition and the **dependency direction**
  between packages, confirming a clean layered architecture (no upward/cyclic deps).
- **Packages:** `frontend` (api / state / main / render), `backend.server`,
  `backend.services`, `backend.repositories`, `backend.algorithms` (solver),
  `backend.database` (+ schema/seed). Dependencies flow **downward**: server → services →
  repositories → database; services → algorithms.
- **Diagram:** UML package notation (tabbed folders + dashed dependency arrows), drawn fresh
  with **matplotlib** (`make_package_diagram.py`) since no Graphviz is available.

### CRC cards
- **Class–Responsibility–Collaborator** cards for the principal classes: each card lists the
  **class name**, its **responsibilities** (what it knows/does), and its **collaborators**
  (classes it works with). e.g. `TimetableService` — *responsibility:* build the solver
  problem, run the solver, persist the resulting version; *collaborators:* MasterDataRepository,
  TimetableSolver, TimetableRepository.

### Standard / notation
UML package diagram + standard 3-section CRC card tables (banded in the docx).

---

# Assignment 08 — Final Project Report

**Task:** Submit the final report following the **sample project report** format: title page
(project title + all team members), table of contents, and **all artifacts in the same order
and sequence** as the sample. Deviation from the prescribed sequence loses marks.

### What goes inside (in order)
1. **Title page** — project title, team members.
2. **Table of contents** — real, page-numbered (Word COM pass).
3. The artifacts, **in the sample's prescribed order**, as chapters:
   process model → requirements/use cases → domain model → DFDs → design class diagram →
   system sequence diagrams → operation contracts → (package/CRC design artifacts) →
   supporting material.

### How it's assembled
`build_final.py` calls the same `emit_aNN(...)` body emitters used for the standalone
assignments, but with a heading-level offset (`loff`) so each assignment becomes a numbered
**chapter** under one continuous document. That guarantees the combined report and the
standalone deliverables never drift out of sync — they are literally the same content,
re-leveled. The TOC + page numbers are then filled by the Word COM pass, and the whole thing
is rendered to `Assignment_08_Final_Project_Report_PDF.pdf` for visual QA.

### Standard / notation
Strict adherence to the provided **sample report** structure and formatting; consistent
heading scheme, captioned figures, and a generated TOC.

---

## Standards summary (quick reference)

| Artifact | Notation / template |
|----------|--------------------|
| Process model | Prose + comparison table; iterative-loop phase diagram |
| Use cases | UML use-case diagram + Cockburn fully-dressed template |
| Domain model | UML conceptual class diagram (concepts + attributes + multiplicities, **no methods**) |
| DFD | Yourdon/DeMarco DFD (process, entity, store, flow) + balancing + functional hierarchy |
| Class diagram | UML design class diagram (3 compartments, visibility, types, multiplicities) |
| SSD | UML sequence diagram, single `:System` lifeline, boundary-crossing events |
| Operation contracts | Larman template (Op / Refs / Pre / Post-as-state-change) |
| Packages | UML package diagram (matplotlib) + downward dependencies |
| CRC | 3-section CRC card tables |
| Final report | Sample-report order, generated TOC, captioned figures |

## Reproducing the deliverables

From `build/report/`:

```bash
python extract.py                 # source .docx → extracted JSON + images
python build_assignments.py       # Assignment_01 … Assignment_07 .docx
python build_design_artifacts.py  # packages + CRC .docx
python make_package_diagram.py    # UML package diagram (matplotlib)
python build_final.py             # Assignment_08 combined report .docx
# then the Word COM pass (PowerShell) updates the TOC fields and exports PDF
```

Outputs land in `build/report/out/` and are mirrored to
`docs/FULLY FINAL COMPLETE/Built Reports/`.
