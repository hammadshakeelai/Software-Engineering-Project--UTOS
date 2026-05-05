# Software Requirements Specification

Project: University Timetable Optimization and Management System  
Version: 0.1 rough build baseline  
Date: 2026-04-26

## 1. Introduction

### 1.1 Purpose

This SRS defines the first buildable baseline for a web-based University Timetable Optimization and Management System. It consolidates the project material found in the repository, especially `REAL/questioning the customers.docx`, the combined assignment documents, the use-case diagrams, DFD diagrams, sequence diagram, and architecture sketches.

### 1.2 Product Scope

The system helps a university department create, review, repair, publish, and report weekly class timetables. It manages teachers, courses, rooms, sections, timeslots, holidays, constraints, and soft scheduling preferences. The first version targets one department or limited university scope.

### 1.3 Problem Statement

Manual timetable creation is slow, error-prone, and difficult to update when teacher availability, room capacity, holidays, sections, and institutional preferences change. The system shall reduce scheduling clashes, expose timetable quality, and support controlled changes without disturbing unrelated timetable entries.

### 1.4 In Scope

- Manage teachers, rooms, courses, sections, timeslots, academic calendar, and holidays.
- Define hard constraints and soft preferences.
- Generate an initial clash-free timetable when feasible.
- Report conflicts, unplaced classes, room use, teacher load, and soft-score penalties.
- Allow manual locking and future re-optimization.
- Publish views for teachers and students.
- Export or print the final timetable in a later increment.

### 1.5 Out of Scope

- Exam timetabling.
- Bus, hostel, attendance, fee, or full ERP management.
- Personalized timetables for individual students.
- Advanced AI prediction.
- Multi-campus deployment in the first version.

## 2. Overall Description

### 2.1 Users and Needs

- Timetable Administrator: maintain data, define rules, generate schedules, repair clashes, lock entries, approve, and publish.
- Department Coordinator: validate department data, review generated schedules, request changes.
- Teacher: view personal timetable, submit availability or change requests.
- Student: view section timetable.
- Facility Manager: review room use, free rooms, capacity issues, and building load.
- System Administrator: manage accounts, roles, settings, backups, and security controls.

### 2.2 Development Lifecycle

The selected lifecycle is the Incremental Process Model with early prototyping as a supporting technique. Planned increments are:

1. Master data and resource setup.
2. Constraints and policy configuration.
3. Initial timetable generation MVP.
4. Review, repair, and controlled re-optimization.
5. Publication and operational reporting.

### 2.3 Architecture

The planned architecture has four separable components:

- Frontend: HTML/CSS/JavaScript screens for operators and viewers.
- Backend API: validation, persistence, role-aware actions, and orchestration.
- Database: persistent master data, constraints, timetable versions, and audit records.
- Solver Engine: transforms data into a timetable assignment and score report.

The current implementation uses a dependency-light Python backend, SQLite database, and modular vanilla frontend. The architecture intentionally keeps the solver swappable so a future OR-Tools CP-SAT implementation can replace the current transparent MVP solver.

## 3. Functional Requirements

### UC01 - Maintain Academic Calendar

- FR-01.1 The system shall allow the Timetable Administrator to add semester dates.
- FR-01.2 The system shall allow the Timetable Administrator to add holidays, blackout dates, and closure days.
- FR-01.3 The system shall prevent generated classes from being placed on holiday or blocked timeslots.

### UC02 - Manage Master Data

- FR-02.1 The system shall allow the Timetable Administrator to add, update, and delete teachers.
- FR-02.2 The system shall allow the Timetable Administrator to add, update, and delete courses, sections, rooms, and timeslots.
- FR-02.3 The system shall store room number, capacity, building, floor, and facilities.
- FR-02.4 The system shall store course teacher, section, weekly session count, and required room type.

### UC03 - Define Constraints and Preferences

- FR-03.1 The system shall support hard constraints for teacher clashes, room clashes, section clashes, room capacity, holidays, and teacher availability.
- FR-03.2 The system shall support soft preferences for morning classes, early endings, nearby rooms, energy-aware building compaction, and traffic-reduction modes.
- FR-03.3 The system shall allow preferences to be enabled, disabled, and weighted.

### UC04 - Generate Timetable

- FR-04.1 The system shall generate a weekly timetable from teachers, courses, rooms, sections, timeslots, holidays, and constraints.
- FR-04.2 The system shall avoid assigning the same teacher, section, or room to two classes in the same timeslot.
- FR-04.3 The system shall assign rooms according to section size, room capacity, and room availability.
- FR-04.4 The system shall return unplaced classes when a complete timetable is infeasible.
- FR-04.5 The system shall calculate a timetable quality score and soft-constraint penalty.

### UC05 - Review Timetable Quality

- FR-05.1 The system shall display the generated timetable in a weekly grid.
- FR-05.2 The system shall show conflicts, warnings, and unplaced classes.
- FR-05.3 The system shall show room utilization, teacher load, and total penalty.

### UC06 - Request Timetable Change

- FR-06.1 The system shall allow teachers to submit change requests.
- FR-06.2 The system shall allow Department Coordinators to request changes for teachers, rooms, or class timings.
- FR-06.3 The system shall store each request reason, status, requester, and timestamp.

### UC07 - Re-optimize Timetable After Change

- FR-07.1 The system shall allow the Timetable Administrator to re-optimize after a teacher, room, or timing change.
- FR-07.2 The system shall minimize disturbance to already accepted classes.
- FR-07.3 The system shall keep locked timetable entries unchanged.

### UC08 - Lock Manual Decisions

- FR-08.1 The system shall allow the Timetable Administrator to lock specific timetable entries.
- FR-08.2 The system shall prevent locked entries from being changed automatically.
- FR-08.3 The system shall allow authorized unlocking.

### UC09 - Publish Timetable

- FR-09.1 The system shall allow the Timetable Administrator to publish an approved timetable.
- FR-09.2 The system shall make the published timetable visible to teachers and students.
- FR-09.3 The system shall support export or printing in a later increment.

### UC10 - View Personal Timetable

- FR-10.1 The system shall allow teachers to view their weekly timetable.
- FR-10.2 The system shall allow students to view their section timetable.
- FR-10.3 The system shall display day, time, room, course, teacher, and section.

### UC11 - View Resource Reports

- FR-11.1 The system shall show room utilization reports.
- FR-11.2 The system shall identify free, used, underused, and overused rooms.
- FR-11.3 The system shall show capacity warnings and peak load periods.

### UC12 - Manage Users and Roles

- FR-12.1 The system shall store user accounts and roles.
- FR-12.2 The system shall restrict timetable management actions to authorized roles.
- FR-12.3 The system shall prevent unauthorized access to restricted screens and API actions in production.

## 4. Non-Functional Requirements

### 4.1 Performance

- NFR-01 Normal dashboard and data requests should respond within 2 seconds for department-scale data.
- NFR-02 Initial timetable generation should complete within 30 seconds for the first academic prototype dataset.
- NFR-03 The solver shall expose partial or infeasible results rather than failing silently.

### 4.2 Security

- NFR-04 Role-based access shall separate Administrator, Coordinator, Teacher, Student, Facility Manager, and System Administrator capabilities.
- NFR-05 The system shall validate input before database writes.
- NFR-06 Production deployment shall use HTTPS, password hashing, audit logs, and database backups.

### 4.3 Usability

- NFR-07 The timetable shall be presented in a weekly grid readable by non-technical users.
- NFR-08 Conflicts and warnings shall be visible next to the generated timetable.
- NFR-09 Master data and policy screens shall use consistent labels and compact workflows suitable for repeated administrative use.

### 4.4 Availability and Reliability

- NFR-10 The system shall persist timetable data in a database so page refreshes and logouts do not lose work.
- NFR-11 The system shall maintain timetable versions so generated drafts can be reviewed later.
- NFR-12 The system shall fail gracefully when no feasible assignment exists.

### 4.5 Maintainability

- NFR-13 Frontend, backend API, repository, service, database, and solver modules shall be separated.
- NFR-14 The solver interface shall allow replacement by CP-SAT or another optimizer without rewriting the UI.
- NFR-15 Configuration data and seed data shall be isolated from algorithm logic.

## 5. Data Requirements

Core entities:

- User(id, name, email, role)
- Teacher(id, name, department, max_daily_load)
- Room(id, code, building, floor, capacity, features)
- Section(id, name, department, size)
- Course(id, code, title, teacher_id, section_id, weekly_sessions, required_room_type)
- Timeslot(id, day, start_time, end_time, sort_order, is_morning, is_last_slot)
- Holiday(id, name, day)
- TeacherAvailability(id, teacher_id, timeslot_id, is_available)
- Preference(id, key, label, enabled, weight, value)
- TimetableVersion(id, name, status, score, hard_conflicts, soft_penalty, created_at)
- TimetableEntry(id, version_id, course_id, teacher_id, section_id, room_id, timeslot_id, locked, status)
- ChangeRequest(id, requester_id, target_type, target_id, reason, status, created_at)

## 6. Solver Foundation

The first build models timetabling as assignment of course events to timeslots and rooms under hard and soft constraints. This follows the course timetabling literature, where a feasible timetable satisfies hard constraints and soft-constraint violations become penalties to minimize.

Current MVP algorithm:

1. Expand each course into weekly session events.
2. Sort events by constrainedness: larger sections, fewer available teacher slots, and higher session pressure first.
3. For each event, rank feasible room-timeslot candidates by soft penalty.
4. Use bounded backtracking to assign candidates while checking hard constraints.
5. Save placed entries and report unplaced entries with a distance-to-feasibility score.
6. Return soft penalties for last-slot usage, non-morning placement when morning preference is enabled, late-day placement, and building movement.

This is a transparent constructive/backtracking baseline. It is not claimed to be globally optimal. A future increment can replace it with CP-SAT, simulated annealing, tabu search, or a hybrid optimizer behind the same solver interface.

Research and technical references:

- Andrea Bettinelli, Valentina Cacchiani, Roberto Roberti, and Paolo Toth, "An overview of curriculum-based course timetabling", TOP, 2015. https://link.springer.com/article/10.1007/s11750-015-0366-z
- Rhydian Lewis, Ben Paechter, and Barry McCollum, "Post Enrolment based Course Timetabling: A Description of the Problem Model used for Track Two of the Second International Timetabling Competition", 2007. https://rhydlewis.eu/papers/PostEnrolTechRep.pdf
- Andrea Schaerf, "A Survey of Automated Timetabling", Artificial Intelligence Review, 1999. https://www.scirp.org/reference/referencespapers?referenceid=1938970
- Google OR-Tools CP-SAT documentation for future solver replacement. https://developers.google.com/optimization/cp/cp_solver

## 7. Constraints

- The first implementation uses SQLite for local development.
- The first implementation supports a single department-scale dataset.
- Authentication is represented in data and UI shape but is not production-enforced yet.
- The solver is a research-grounded MVP baseline, not a full industrial optimizer.

## 8. Acceptance Criteria For Current Build

- The app starts locally from a single Python command.
- The database schema initializes automatically.
- Seed data appears in the dashboard.
- The user can trigger timetable generation.
- The generated timetable is persisted as a version.
- The frontend displays timetable entries, warnings, room use, and teacher load.
- The codebase is modular enough for independent frontend, backend, database, and solver changes.
