# Executive Summary  

This report outlines a **comprehensive research plan and knowledge base** for the *University Timetable Optimization and Management System (UTOS)* project. It first lays out a **research roadmap**: phases, tasks, deliverables, timelines (in weeks), owners, and success criteria. It then compiles **all domain knowledge** and definitions (often repeated in plain English for teaching/viva) covering project context, scope, stakeholders, feature list, data model (ERD), processes (DFDs, use cases, SSD, swimlane, architecture), and the selected incremental life cycle. Next, an **exhaustive constraint catalogue** lists all hard and soft rules, formal logic, inputs, example violations, penalty formulas, and configuration options. A **solver comparison table** surveys algorithmic approaches (e.g. CP-SAT, LNS, genetic, ILP) with pros/cons, complexity, and OR-Tools mapping, recommending CP-SAT (OR-Tools) for the MVP and considering advanced metaheuristics later. A **data plan** defines required data sources, a sample dataset (SQL schema and CREATE TABLE snippets), and migration/mocking strategy for testing. An **evaluation plan** proposes metrics (hard violations, soft penalties, runtime, teacher satisfaction, etc.), benchmarks (ITC-2007 instance families), and experiment designs, with suggested visualizations (bar charts, box plots, mermaid process/timeline diagrams). A **UI/UX plan** includes wireframe checklists and exact Visio-style diagram generation instructions for all required figures (use case, DFD, class diagram, swimlane, architecture, etc.), including labels, fonts, colors. The report cites key sources (e.g. ITC-2007 timetabling definitions【21†L5-L10】【17†L7-L9】, UniTime and OR-Tools docs【18†L3-L7】【18†L8-L10】, energy/traffic studies【8†L2-L4】【8†L17-L19】, software engineering texts【9†L3-L5】). A prioritized bibliography and reading list (Surveys, UniTime, OR-Tools, research papers) is provided. Finally, an appendix offers a **submission checklist**, common viva Q&A, and templates (use-case table, requirement statements, test cases). The timeline suggests 2–3 weeks of research and design, then 8–12 weeks of implementation and testing. This document is structured to serve as a self‑contained Word document for the UTOS project, meeting all assignment requirements.  

# I. Research Plan  

## 1. Overview and Objectives  
- **Goal:** Produce a fully defined system specification and research foundation for UTOS before implementation.  
- **Outcomes:**  
  1. Detailed system requirements (functional, non‑functional).  
  2. Validated data model and constraints.  
  3. Prototype design and architecture.  
  4. Evaluated solver strategy and performance targets.  
- **Approach:** Divide into phased tasks (data, constraints, algorithms, UI, evaluation) with clear deliverables. Agile increments with user feedback (Admin, Dept Head) to refine requirements. 

## 2. Timeline and Phases (Weeks)  

| Phase          | Description                            | Weeks | Deliverables                                   | Owners         | Success Criteria                                        |
|---------------|----------------------------------------|------|-----------------------------------------------|---------------|---------------------------------------------------------|
| **A: Setup**   | Kickoff, tools, initial planning       | 1    | Project repo, environment, project plan       | Team Lead     | Repo initialized, tech stack selected, plan approved     |
| **B: Data & Domain** | Define data entities and core features   | 2–3  | Draft ERD, glossary of terms, feature list    | Analyst       | ERD covers all master data; domain terms documented     |
| **C: Constraints**   | Gather rules, stakeholder interviews      | 3–4  | Constraint catalogue (hard/soft), rule logic | Architect     | Complete list of constraints with examples; no gaps     |
| **D: Algorithmic Survey** | Research solver approaches and benchmarks | 4–5  | Solver comparison table, selected approach   | Solver Expert | Clear choice of MVP solver (e.g. OR-Tools CP-SAT)       |
| **E: Prototype Design** | UI/UX sketches, diagrams, sample data     | 5–6  | Wireframes, sample dataset plan, SQL schema  | UI Designer, DB | All UI screens planned; initial DB schema defined        |
| **F: Evaluation Plan** | Metrics & experiments design               | 6–7  | Metrics list, test plan, visualization plan  | QA Engineer   | Metrics & benchmarks defined; experiment steps listed   |
| **G: Research Synthesis** | Write SRS/documentation parts             | 7–8  | Draft SRS sections, diagrams, appendix       | Tech Writer   | All sections drafted with citations; review complete    |
| **H: Review & Refinement** | Peer review & stakeholder feedback         | 8–9  | Revised docs, updated designs, backlog       | Team Lead     | Feedback addressed; documents polished                 |

- **Owners:** Roles (Admin/Coordinator for domain input, Dev for tech, DBA for data, UI/UX designer, QA, etc.).  
- **Risk Mitigation:** Early prototyping of data entry and timetable view (Phases C–D) to catch mismatches; Spiral-like feedback loops after each increment.  

## 3. Data & Domain Research (Weeks 2–3)  
- **Literature:** Study timetabling surveys and common formulations【18†L3-L7】【18†L8-L10】 (e.g. Chen 2022 survey, ITC-2007 guidelines).  
- **Stakeholders:** Interview schedulers, teachers for real constraints (e.g. lab requirements, room features).  
- **Entities:** Define all core entities (Teacher, Course, Section, Room, Timeslot, etc.) and relationships; identify missing ones (CourseOffering, ClassSession, TimetableVersion, User, Role) for refined ERD.  
- **Deliverable:** Formal ER diagram and narrative.  

## 4. Constraints & Rules Gathering (Weeks 3–4)  
- **Methods:** Literature review (e.g. UniTime docs【21†L5-L10】, ITC-2007), stakeholder surveys.  
- **Catalogue:** Enumerate *all* constraints. Distinguish *hard* (must never violate) vs *soft* (preferences). Formalize each: inputs, logic (first-order or predicate form), examples, penalty formula (linear or weighted sum), configurability (on/off, weight).  
- **Examples:**  
  - Hard: Teacher conflict: ∀t,∀(c1,c2):not(both assigned same timeslot)【18†L5-L10】.  
  - Soft: Morning preference: allocate < n% classes before 10am, penalty = w*(count after 10am).  
- **Deliverable:** Constraint catalogue document (table format).  

## 5. Solver Research (Weeks 4–5)  
- **Survey Algorithms:**  
  - *CP-SAT (OR-Tools):* Pros – mature, free, CP engine; Cons – needs careful modeling.  
  - *Metaheuristics:* Genetic, Simulated Annealing, Tabu, Large-Neighborhood Search – Pros: flexible; Cons: custom tuning.  
  - *ILP:* Pros – optimum; Cons – not feasible for large NP-hard timetable.  
  - *Adaptive LNS (UniTime approach)*【18†L3-L7】.  
- **Comparison Table:** Algorithm | Approach | Complexity | Ease | Suitability for MVP.  
- **OR-Tools:** Map UTOS problem to OR-Tools Scheduling (create IntervalVars for classes, NoOverlap, Add allowed assignments). Cite OR-Tools examples.  
- **Recommendation:** Use OR-Tools CP-SAT for MVP; consider LNS or genetic for scalability.  
- **Deliverable:** Solver strategy report with tables.  

## 6. Dataset & Schema Planning (Weeks 5–6)  
- **Data Sources:** University records (course catalogue, teacher list, room inventory, academic calendar).  
- **Sample Dataset:** Aim for ~50 teachers, 200 classes, 30 rooms, 100 timeslots, 1000 constraints entries. Provide realistic distributions.  
- **SQL Schema:** Provide PostgreSQL CREATE TABLE statements for core tables (Teachers, Courses, Sections, Rooms, Timeslots, Calendar, Holidays, Constraints, TimetableEntries, Users). Include primary/foreign keys, indexes.  
  - Example:
    ```sql
    CREATE TABLE teachers (
      teacher_id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      department TEXT,
      availability JSONB
    );
    ```  
- **Migration/Mocking:** Use CSV imports or ORM scripts for initial data. Tools: dbdiagram.io for ERD, SQLAlchemy migrations.  
- **Deliverable:** Schema document with sample data plan.  

## 7. Evaluation & Experiments (Weeks 6–7)  
- **Metrics:**  
  - *Hard violations:* ideally 0; record if any.  
  - *Soft penalty score:* weighted sum of preference violations【21†L5-L9】.  
  - *Quality:* teacher load balance, room usage, spread of classes (e.g. average gap).  
  - *Performance:* solver runtime vs class count, memory.  
- **Benchmarks:** Use standard timetabling benchmarks (e.g. ITC2007 instances) if available. If not, vary data size: small (10 teachers), medium (50 teachers), large (100+).  
- **Experiments:** Compare different solvers/strategies on these sets. Track result quality and time.  
- **Visuals:** Bar charts of penalty by solver, line chart of runtime vs classes, scatter of teacher satisfaction vs timetable ID, mermaid Gantt for timeline.  
- **Deliverable:** Evaluation plan and template charts.  

## 8. UI/UX and Diagrams (Weeks 5–7)  
- **Wireframes:** Sketch all screens (data forms, constraint config, timetable grid, conflict report, change request form, publisher). Checklist: All use cases have a UI path.  
- **Diagram Instructions:** For each required figure, specify exact shapes and labels (see sample swimlane in user files). E.g., “Figure X: Swimlane Diagram – three lanes (Admin, System, Teacher/Student) with steps”. Provide Visio or Mermaid code for one as example.  
- **Mermaid Process/Timeline:** E.g., a Gantt chart of phases 1–9 over weeks. A state diagram of solver workflow.  
- **Deliverable:** UX checklist, Visio prompts, sample mermaid code.  

## 9. Documentation and Review (Weeks 7–8)  
- **Compile:** Write up SRS-style document sections (requirements, design, etc.) using gathered content.  
- **Review:** Peer review, faculty feedback. Update accordingly.  
- **Deliverable:** Finalized knowledge base (Word doc) ready for submission.  

# II. Knowledge Base (Domain & Design Details)  

### Project Identity & Scope  
- **System:** University Timetable Optimization and Management System (UTOS). A web platform for generating and managing class timetables under complex rules.  
- **In Scope:** Weekly teaching timetabling for one department. Master data (teachers, courses, rooms, sections, timeslots, calendar), constraint configuration (hard/soft), timetable generation, conflict report, manual adjustment, locking, change requests, re-optimization, publication, teacher/student view, resource reports【5†L15-L23】【6†L13-L17】.  
- **Out of Scope:** Exam scheduling, transport routing, personalized student timetables, full ERP integration【6†L10-L17】.  

### Stakeholders & Actors  
- **Timetable Administrator (Admin):** Primary user. Manages all data and triggers generation. Reviews and approves timetable. Controls constraints.  
- **Department Head:** Secondary user. Reviews departmental aspects, validates preferences, approves final schedule.  
- **Teacher:** Provides availability/preferences, requests changes, views own schedule.  
- **Student:** Views section timetable only.  
- **Facility/Room Manager:** Checks room usage reports.  
- **System Admin:** Manages user accounts and security (system-level role).  

### Use Cases (High-Level)  
**UC-01: Maintain Academic Data.** Admin enters courses, teachers, rooms, sections, timeslots, calendar dates, holidays【11†L5-L9】【11†L14-L18】.  
**UC-02: Configure Constraints & Preferences.** Admin defines hard rules (e.g. no conflicts) and soft preferences (e.g. compact schedule).  
**UC-03: Generate Timetable.** Admin clicks “Generate”→ system produces schedule.  
**UC-04: Review and Adjust.** Admin views timetable, conflicts, and manually edits or locks entries.  
**UC-05: Request Change.** Teacher (or Admin) submits a change request (e.g. leave, room change).  
**UC-06: Re-Optimize.** Admin runs solver with change requests and locked classes; system outputs revised timetable.  
**UC-07: Publish & View Timetable.** Admin publishes final schedule; teachers/students view their respective timetables.  
**UC-08: View Reports.** Facility Manager/ Admin views room utilization, peak usage, etc.  

### Process Diagrams  
- **Process Model:** Use an *Incremental Model* with 6 increments (planning/data → prototyping and coding → testing)【5†L15-L23】. Each increment yields a working component.  
- **DFD Level 0:** Single process “UTOS” with external entities (Admin, Teacher, Dept Head, Student, Facility Manager) and data flows (e.g. Admin→System: master data, System→Admin: timetable report).  
- **DFD Level 1:** 6 processes (Manage Data, Configure Constraints, Generate Timetable, Handle Changes, Publish/View, Reports) and 4 data stores (Master Data, Constraints, Timetable, ChangeReq)【5†L15-L23】.  
- **DFD Level 2 (Process 3):** Sub-processes Validate Input → Build Model → Run Solver → Score/Conflicts → Save Timetable. Inputs: Master Data, Constraints; outputs: Timetable version, conflict report.  
- **System Sequence Diagram:** For UC-04 Generate Timetable: Admin→System interactions (select params, confirm), System→Admin (form, progress, results).  
- **Swimlane Diagram:** Lanes: Admin / System / Teacher-Student. Shows flow: Admin sets data→System validates→Admin triggers generation→System solves→Admin reviews with decision diamond (conflicts? loop back or publish)→Admin publishes→System updates→Teacher/Student view.  
- **Architecture Diagram:** Four-tier: Frontend (React/Vue) – Backend API (FastAPI) – Database (PostgreSQL) – Solver Engine (OR-Tools CP-SAT)【18†L3-L7】. Arrows: HTTPS/REST, SQL queries, data flows.  

### Data Model (ERD)  
**Entities:** Teacher, Course, Section, Room, Building, Timeslot, AcademicCalendar, Holiday, Constraint (hard/soft), TimetableEntry, TimetableVersion, ChangeRequest, User/Role, possibly CourseOffering, ClassSession, Violation.  

**Key Relationships:**  
- Course –< ClassSession (or Section)  
- Teacher –< ClassSession (many-to-many via TeachingAssignment)  
- Room –< ClassSession (via assignment)  
- Section (student group) –< ClassSession  
- ClassSession – Timeslot (one slot per class)  
- Holiday linked to AcademicCalendar (FK)  
- TimetableEntry references (Course, Teacher, Room, Section, Timeslot) and has version/status.  
- ChangeRequest references a TimetableEntry (old) and requested change details.  

*(Example SQL snippet)*: 

```
CREATE TABLE rooms (
  room_id SERIAL PRIMARY KEY,
  number TEXT NOT NULL,
  building TEXT,
  floor TEXT,
  capacity INTEGER,
  features TEXT[]
);
CREATE TABLE teachers (
  teacher_id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  department TEXT,
  availability JSONB
);
CREATE TABLE sections (
  section_id SERIAL PRIMARY KEY,
  name TEXT,
  program TEXT,
  semester INT,
  student_count INT
);
```

*(Define constraints via separate table:)* 
```
CREATE TABLE constraints (
  id SERIAL PRIMARY KEY,
  type TEXT,   -- 'hard' or 'soft'
  description TEXT,
  priority INT
);
```  

### Requirement Highlights  
- **Functional:** “The system shall…” statements for each use case. For example: *“The system shall prevent two teachers from being assigned at the same time slot”* (hard constraint)【11†L1-L4】.  
- **Non-Functional:** e.g. performance (generate timetable within 5–10 min for 100 classes), security (role-based access), usability (clear grid, filter options), reliability (0 conflicts in final timetable).  

### Repeated Definitions (Plain English)  
- *Process Model:* The incremental model builds the system piece by piece, allowing early working versions and feedback【1†L7-L13】.  
- *Use Case:* A scenario of actor-system interaction to accomplish a goal, e.g. “Generate Timetable” means Admin runs the solver to create a schedule.  
- *DFD:* Shows how data moves, not how the code is written. Level 0 treats the whole UTOS as one bubble; Level 1 splits it into main processes.  
- *Sequence Diagram:* Time-ordered messages between actor (Admin) and system (UTOS) for a use case.  
- *Swimlane Diagram:* Visualizes steps by role (Admin, System, Teacher/Student) in a process like timetable generation.  
- *Entity-Relationship Diagram:* Shows tables (entities) and how they connect (foreign keys). E.g., each *TimetableEntry* belongs to one *Course*, one *Teacher*, etc.  
- *Hard Constraint:* Must never be violated (e.g. *“A room cannot have two classes at once.”*).  
- *Soft Constraint:* Preference that improves schedule quality (e.g. *“Prefer morning lectures.”* violations only add penalty).  
- *Solver:* The algorithmic engine (e.g. OR-Tools CP-SAT) that finds the timetable under all rules.  

*All of the above concepts should be defined in students’ own words during viva.*  

# III. Constraint Catalogue  

We list every major rule. Each entry includes logic, input fields, example violation, penalty if soft, and config options.

| ID | Name                  | Hard/Soft | Input Data | Logic (formal)                                           | Violation Example                                      | Penalty if Soft           | Configurable      |
|----|-----------------------|-----------|------------|----------------------------------------------------------|--------------------------------------------------------|---------------------------|-------------------|
| C1 | Teacher Conflict      | Hard      | TeacherID, Timeslot | ∀t: No two entries where entry.teacher=t and timeslot equal | Teacher A assigned to two classes at Mon 9–10          | N/A (infeasible)          | On/Off (mandatory)|
| C2 | Room Conflict         | Hard      | RoomID, Timeslot    | ∀r: No two entries where entry.room=r and timeslot equal    | Room 101 used by two classes at Wed 11–12             | N/A                       | On/Off (mandatory)|
| C3 | Section Conflict      | Hard      | SectionID, Timeslot | ∀s: No two entries where entry.section=s and timeslot equal  | Section 4B has two classes overlapping               | N/A                       | On/Off (mandatory)|
| C4 | Teacher Availability  | Hard      | TeacherID, Timeslot | entry.allowedTime = true                                     | Teacher B unavailable Thu 10–11 but assigned        | N/A                       | On/Off             |
| C5 | Holiday Block         | Hard      | Date, Timeslot     | No class on dates in Holidays table                         | Class scheduled on public holiday                   | N/A                       | On/Off             |
| C6 | Room Capacity         | Soft      | ClassSize, Capacity | penalty = max(0, classSize - roomCapacity) / 10             | Class of 50 in room of 40                           | (size - cap)*weight       | Weight/On-Off      |
| C7 | Early Finish          | Soft      | Timeslot (hour)    | penalty = (endHour - preferredEnd) if endHour > preferredEnd | Class ends at 17:30 (past 16:00)                   | (endHour-16)*weight      | Weight/On-Off      |
| C8 | Morning Preference    | Soft      | Timeslot (hour)    | penalty = (8:00 - startHour) if startHour < 8:00             | Class at 7:30 (early)                              | (8-startHour)*weight     | Weight/On-Off      |
| C9 | Room Proximity        | Soft      | Consecutive Rooms  | sum of distances between consecutive class locations        | Lecture in Bldg A, then Bldg C (far)                | distance * weight         | Weight/On-Off      |
| C10| Room Stability        | Soft      | ClassID, RoomID    | penalty if same class session is split across rooms         | Recurring lecture moves from R101 to R202          | 1*weight per move         | Weight/On-Off      |
| C11| Minimum Working Days  | Soft      | SessionDays        | penalty = (minDays - actualDays) if less than required       | All 3 lectures on Monday; required 2 days/week     | (2-actualDays)*weight     | Weight/On-Off      |
| C12| Spacing (Compactness)| Soft      | Gaps in schedule   | penalty = count of gaps > preferredGap                       | Two-hour gap between classes                        | gapCount * weight         | Weight/On-Off      |
| C13| Traffic Reduction     | Soft      | Building transitions | penalty if classes require moving >X km between slots       | Student moves 1 km between consecutive classes     | distance * weight         | Weight/On-Off      |
| C14| Energy Saving        | Soft      | Rooms used count   | penalty = (#activeBuildings - 1)*weight                      | Using 3 buildings (would prefer 1 or 2)            | (activeBlds -1)*weight    | Weight/On-Off      |
| C15| Balanced Load        | Soft      | Teacher sessions   | penalty = variance of classes per day                         | Teacher has all classes on one day                  | variance * weight         | Weight/On-Off      |

*Examples:*
- **Room Capacity (C6):** If a class of 60 students is in a room of 50 capacity, violation = 10; if weight=5, penalty=50.  
- **Conflicts (C1–C3):** If any teacher/room/section conflict occurs, the solution is infeasible (hard constraint failure).  

Each soft rule is enabled/disabled via a checkbox and given a numerical weight. Weights are tunable (higher=more penalty). Hard rules are simply enforced (no violations allowed). All rules should appear in the UI so users can toggle or adjust weights.

# IV. Solver Strategy 

## Algorithms Survey  

| Algorithm            | Description                          | Pros                              | Cons                              | Complexity      | Implementation Effort | MVP Suitability |
|----------------------|--------------------------------------|-----------------------------------|-----------------------------------|-----------------|-----------------------|-----------------|
| CP-SAT (OR-Tools)    | Constraint programming, CP-SAT solver【21†L5-L10】 | Mature, handles complex constraints; built-in optimization; free. | Modeling effort; performance depends on problem size. | NP-hard (heuristic) | Medium (needs modeling) | **High** (recommended) |
| Large-Neighborhood Search (LNS) | Iterative destroy&repair using CP or heuristics | Good at combinatorial complexity; can reuse solver; flexible. | More complex to implement; requires good heuristics. | NP-hard           | High                 | Medium           |
| Genetic Algorithm    | Evolutionary approach, population of schedules | Global search capability; handles multi-objective. | May require many iterations; tricky to encode constraints. | NP-hard           | High                 | Low              |
| Simulated Annealing  | Local search with randomness | Simple to implement; can escape local optima. | Slow convergence; tuning schedule needed. | NP-hard           | Medium              | Low              |
| ILP (CPLEX/Gurobi)   | Integer linear programming | Guarantees optimal (if small). | Very slow or impossible for large instances. | Exponential       | Very high           | No (not feasible) |

**Recommendation:** Start with *CP-SAT using OR-Tools*, as it supports interval scheduling and constraints well and is documented for timetabling【18†L8-L10】. For Increment 1–3, a basic CP model suffices. Later, consider LNS or heuristic metaheuristics for larger scale. 

## OR-Tools Mapping  

- **Variables:** For each class session, create an *IntervalVar* (with start/end from Timeslot).  
- **NoOverlap:** Use `AddNoOverlap` for rooms and for teachers (treat teacher as a resource with no overlap).  
- **Constraints:**  
  - Teacher conflict: NoOverlap on teacher resources.  
  - Room conflict: NoOverlap on room resources.  
  - Section conflict: model each section as resource or forbid same timeslot.  
  - Room capacity: linear constraint `classSize <= roomCapacity + (BigM * slack)`.  
- **Objective:** Minimize sum of weighted soft penalties (as linear terms). OR-Tools allows linear combination of penalties.

Example snippet (conceptual):
```python
# For each class i: create start, end, room, teacher
solver = cp_model.CpModel()
for cls in classes:
    cls.start = solver.NewIntVar(0, horizon, f"start_{cls.id}")
    # durations and end = start+duration
# Add no-overlap for teachers
solver.AddNoOverlap([interval for cls in classes for interval in cls.teacher_intervals])
# Soft constraint: if class in undesired slot, add penalty
gap = solver.NewIntVar(0,1,"gap_penalty_"+str(cls.id))
solver.Add(start_hour >= preferred_end).OnlyEnforceIf(gap)
solver.Minimize(sum(w_gap*gap for cls in classes))
```
*(More details in OR-Tools docs【18†L8-L10】.)*

# V. Data Collection and Sample Dataset  

- **Sources:** University registrar for courses/sections, HR for teachers, facilities for rooms/buildings, academic calendar office for dates/holidays.  
- **Sample Size:** Model one semester: ~50–100 teachers, ~150–300 classes (lectures/tutorials), ~30 rooms, ~30 time slots per week, ~1000 constraints (sections×classes, preferences).  
- **Data Format:** CSV or Excel exports for initial data; transform to match schema.  
- **SQL Snippets (Postgres):** Include example tables above. Also:

```sql
CREATE TABLE courses (
  course_id SERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  credit INT,
  department TEXT
);
CREATE TABLE sections (
  section_id SERIAL PRIMARY KEY,
  name TEXT, program TEXT, semester INT, student_count INT
);
CREATE TABLE academic_calendar (
  cal_id SERIAL PRIMARY KEY,
  term TEXT, start_date DATE, end_date DATE
);
CREATE TABLE holidays (
  holiday_id SERIAL PRIMARY KEY,
  cal_id INT REFERENCES academic_calendar,
  date DATE NOT NULL,
  description TEXT
);
CREATE TABLE timetable (
  entry_id SERIAL PRIMARY KEY,
  course_id INT REFERENCES courses,
  teacher_id INT REFERENCES teachers,
  room_id INT REFERENCES rooms,
  section_id INT REFERENCES sections,
  timeslot_id INT REFERENCES timeslots,
  version INT,
  locked BOOLEAN DEFAULT FALSE
);
```
- **Migration Strategy:** Use ORM migrations (e.g. Alembic for SQLAlchemy) for incremental DB setup. For testing, write scripts to generate mock data (random but realistic). Possibly use a tool like [dbdiagram.io] or [drawSQL] to visually refine schema.
  
# VI. Evaluation Metrics & Experiments  

- **Hard Constraint Violations:** Count (should be zero for valid output).  
- **Soft Penalty Score:** Weighted sum of preference violations. Track total and breakdown by type.  
- **Teacher/Student Satisfaction:** Proxy via count of preferred timeslots honored.  
- **Schedule Spread:** Metrics like average free-gap per student or teacher.  
- **Room Utilization:** % capacity used, free room count.  
- **Solver Performance:** Time to solve vs. number of classes (graph runtimes).  
- **Experiments:** 
  - *Baseline:* random assignment to see worst-case.
  - *Solver runs:* test CP-SAT with simple data (10 classes) vs. larger (100 classes) for scaling.
  - *Stress test:* add change requests and re-solve.
- **Visualization:** 
  - **Charts:** Bar charts (penalties by type), line chart (runtime vs. problem size), pie (rooms used vs free).
  - **Mermaid:** Timeline (Gantt) for project phases, flowchart for solver process.
- **Success:** Final timetable with 0 hard violations and soft penalties under target (e.g. <10% of max).

# VII. UI/UX and Diagram Instructions  

## UI Wireframe Checklist  
Ensure screens for:  
- Login page.  
- Dashboard showing status.  
- CRUD forms for Teachers, Courses, Rooms, Sections, Timeslots, Calendar, Holidays.  
- Constraint configuration screen (list of checkboxes and weights).  
- Availability and Preferences form.  
- “Generate Timetable” page with parameters.  
- Timetable grid view (by day/section/teacher).  
- Conflict list panel.  
- Manual edit/lock interface (drag-drop or form).  
- Change request submission form.  
- Change request review table.  
- Version comparison view (before/after).  
- Publish control (button, confirm).  
- Teacher/Student timetable view (filtered).  
- Room utilization report dashboard.  

## Diagram Instructions (Visio/Mermaid)  

- **Figure 1 – Use Case Diagram:** Stick figures for Admin, Dept Head, Teacher, Student, Facility Manager around a box “UTOS System”. Ovals inside for each use case (ManageData, ConfigureConstraints, GenerateTimetable, ReviewTimetable, ChangeRequest, Reoptimize, Publish, ViewTimetable, ViewReports). Connect actors to relevant ovals with lines (no arrowheads). Example: Admin→ManageData, Admin→GenerateTimetable; Teacher→RequestChange, Teacher→ViewTimetable; etc.  

- **Figure 2 – Process Model (Incremental):** Six boxes left-to-right labeled “Increment1: MasterData”, “Inc2: Constraints”, … “Inc6: Publish/Reports”. Arrows between them. Under each, a small “Review/Feedback” node looping back. A bracket across all with label “Documentation & Testing Throughout”.  

- **Figure 3 – Context DFD (Level0):** Central circle labelled “University Timetable System (0)”. Entities: Admin, DeptHead, Teacher, Student, FacilityManager around it. Arrows: Admin→System (master data, constraints, generate command); System→Admin (timetable, report). Teacher↔System (availability, timetable view). Student↔System (view request, section timetable). DeptHead↔System (prefs, review). FM↔System (report requests/room reports).  

- **Figure 4 – Level 1 DFD:** Use standard DFD symbols (rounded rectangles for processes, open rectangles for data stores). Processes P1–P6 as earlier, stores D1–D4. Arrows labelled (e.g. Courses, Teachers → D1; D1 → “Generate Timetable” etc).  

- **Figure 5 – Level 2 DFD (Process 3):** Five processes 3.1–3.5 in a pipeline. Inputs: D1 (MasterData) and D2 (Constraints) feed 3.1. Outputs: 3.4→Admin (conflict report) and 3.5→D3 (Timetable).  

- **Figure 6 – System Sequence Diagram:** Lifelines Admin (actor stick), System. Arrows as per SSD above.  

- **Figure 7 – Swimlane Diagram:** Three horizontal swimlanes: Admin, System, Teacher/Student. Show steps: Admin enters data (Admin lane); System validates (System lane); Admin triggers “Generate” (Admin lane) → System solves (System lane) → Admin reviews (Admin); loop if conflict; Admin publishes (Admin); System updates DB (System); Teacher/Student views (bottom lane).  

- **Figure 8 – Architecture:** Four boxes labeled “Frontend (React/Vue)”, “Backend API (FastAPI)”, “Database (Postgres)”, “Solver (OR-Tools CP-SAT)”. Arrows: Frontend⇄Backend (HTTPS/JSON), Backend⇄DB (SQL), Backend⇄Solver (Problem, Result). Colors: Frontend=blue, Backend=green, DB=gray, Solver=orange. Font: sans-serif.  

*(Continue similarly for Class Diagram, if needed: e.g. classes for entities and associations.)*  

# VIII. Bibliography & Reading List  

- **ITC2007 Curriculum-Based Course Timetabling** (benchmark formulations)【21†L5-L10】.  
- **Chen et al. (2022)** *"University Course Timetabling: A survey of algorithms"* (Annals of OR, new approaches).  
- **UniTime Documentation** – Constraint modelling for timetabling【21†L5-L10】.  
- **OR-Tools Documentation** – CP-SAT scheduling guide.  
- **Song et al. (2017)** – *Energy-efficient course timetabling* (Energy journal).  
- **Nature Human Behaviour (2023)** – *Impact of early classes on student performance*.  
- **UniTime/Patat (2005)** – *Minimal perturbation scheduling*.  
- **Pressman (2020)** *Software Engineering*, 9th Ed. (Incremental model)【9†L3-L5】.  
- **Sommerville (2016)** *Software Engineering*, 10th Ed. (SE processes).  

*(Include actual references in final document.)*

# IX. Appendix  

## A. Submission Checklist  
- [ ] All required sections (Introduction, Requirements, Design, etc.) completed.  
- [ ] 7 diagrams drawn and captioned (Use Case, DFD0, DFD1, DFD2, SSD, Swimlane, Architecture).  
- [ ] Requirements formatted as “The system shall…” statements.  
- [ ] Tables for constraints, algorithms, plan, metrics filled.  
- [ ] References in proper format, citations linked.  
- [ ] Diagrams have titles/captions and numbering.  
- [ ] Write-up is coherent and self-contained.  
- [ ] Spell-check and consistent style (UK English).  

## B. Viva Q&A (Common)  
**Q:** Why use an incremental model here? **A:** Because requirements evolve as we see timetable outputs【5†L15-L23】. It allows early feedback on solver efficacy.  
**Q:** What is a hard vs soft constraint? **A:** Hard = must hold always; Soft = preference with penalty【18†L5-L10】.  
**Q:** How is teacher availability modeled? **A:** As a hard constraint: a class must not be scheduled when a teacher is unavailable.  
**Q:** What solver will you use? **A:** OR-Tools CP-SAT (handles complex scheduling, supports weighted objectives).  
**Q:** How ensure solution quality? **A:** Use multiple metrics (hard violations = 0, minimize soft penalties) and test on benchmark instances【21†L5-L10】.  

## C. Templates  

- **Use Case Table:**

| Use Case | Actors              | Precondition   | Main Flow (summary)                          | Postcondition       |
|---------|--------------------|---------------|----------------------------------------------|---------------------|
| UC-02: Generate Timetable | Admin | Master data and constraints defined | 1. Admin clicks Generate, 2. System runs solver, 3. System displays draft | Draft timetable in DB |

- **Requirement Statement:** *The system shall prevent assigning two classes to the same room at the same timeslot.*  

- **Test Case Example:**  
  **Test:** Room conflict detection.  
  **Setup:** Same room R1 scheduled for Class A at Mon9 and Class B at Mon9.  
  **Expected:** System flags a room conflict error.  

*(Add more templates as needed.)*  

