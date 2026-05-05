# Software Requirements Specification (SRS)

## University Timetable Optimization and Management System (UTOS)

**Version:** 1.0  
**Date:** May 2026  
**Status:** Full Scope Document

---

## 1. Introduction

### 1.1 Purpose

This SRS defines the complete requirements specification for a web-based University Timetable Optimization and Management System. The system manages two interconnected modules:

1. **Class Timetabling Module** - Weekly class schedule generation and management
2. **Exam Timetabling Module** - Exam scheduling and room management

This document covers both modules as separate but related subsystems within a unified platform.

### 1.2 System Overview

The UTOS is a comprehensive platform that helps a full university (multiple departments, thousands of concurrent users) create, manage, optimize, and publish timetables for classes, examinations, and transportation constraints. It provides automated generation with manual override capabilities, conflict detection, quality scoring, versioning, and role-based access for different user types.

### 1.3 Problem Statement

Manual timetable creation at university scale is extremely complex:

- **Class Timetabling**: Teacher clashes, room conflicts, section scheduling, holiday handling, variable class durations (1h, 1h30m, 2h), hard/soft constraints, thousands of students across dozens of departments
- **Exam Scheduling**: Multiple courses, large student populations, room capacity constraints, varied exam durations, no double-booking

The system must handle full university scale while remaining responsive and usable.

---

## 2. Scope

### 2.1 In Scope

#### Class Timetabling Module:
- Multi-department timetable generation
- Teacher, room, section, course, timeslot management
- Academic calendar and holiday handling
- Hard constraints and soft preferences configuration
- Variable duration classes (1 hour, 1.5 hours, 2 hours)
- 2-hour class handling options: single per day, morning only, continuous, late options
- Flexible or fixed time slots
- Conflict detection and resolution
- Room capacity and type matching
- Timetable quality scoring
- Manual adjustment and locking
- Version control and re-optimization
- Change request workflow
- Published views for teachers and students

#### Exam Timetabling Module:
- Room management (capacity, type: lab/conference/classroom)
- Optional distance graph between buildings
- Student hierarchy: University → Faculty → Department → Batch → Section → Student details
- Nested tree-view of student data
- Course-exam association
- Semi-automatic exam placement (system suggests, admin confirms)
- Exam duration configuration
- Room availability checking
- No student double-booking
- Exam day utilization optimization

#### System-Wide:
- Role-based access control
- Full university scale (thousands of concurrent users)
- Background generation (non-blocking UI)
- Version control
- Audit logging

### 2.2 Out of Scope

- Personalized timetables for individual students (section-level only)
- Full multi-campus simulation
- Deep algorithm benchmarking
- Financial/fee management
- Attendance tracking
- Hostel allocation

---

## 3. Users and Roles

### 3.1 Actors

| Role | Description |
|------|-------------|
| **Timetable Administrator** | Full access to all modules, generation, publishing, configuration |
| **Department Coordinator** | Department-level data validation, review, change approval |
| **Teacher** | View timetable, submit availability/change requests |
| **Student** | View published timetable for their section |
| **Facility Manager** | Room management, utilization reports |
| **System Administrator** | User accounts, roles, security, backups |

### 3.2 User Characteristics

| User Type | Skill Level | Application |
|-----------|-------------|-------------|
| Timetable Administrator | Moderate technical | Full system operation |
| Department Coordinator | Basic-moderate | Review and approval |
| Teacher | Basic | View + request only |
| Student | Basic | View published only |
| Facility Manager | Basic-moderate | Room reports |
| System Administrator | Technical | System management |

---

## 4. Functional Requirements

### MODULE 0: SYSTEM-WIDE FEATURES

#### UC-00: Authentication & Login
- FR-00.1 The system shall allow Timetable Administrator to login with role + password (no email)
- FR-00.2 The system shall allow other users to login with email + password
- FR-00.2a Login page shall be single page with role selection
- FR-00.2b Random password generated for new users
- FR-00.3 Passwords shall be stored (plain text for MVP, hashed in production)
- FR-00.3 Passwords shall be stored (plain text for MVP, hashed in production)
- FR-00.4 Session shall be stored in browser localStorage
- FR-00.5 Session shall persist across browser refresh
- FR-00.5a Non-admin users shall auto-logout after inactivity
- FR-00.5b Admin users shall stay logged in
- FR-00.6 Users shall be able to logout
- FR-00.6a Users shall be able to reset password via email link
- FR-00.6b Users shall be able to view their profile (name, email, role)
- FR-00.6c Profile editing shall be view-only (admin changes)

#### UC-00: Organization Hierarchy
- FR-00.6a The system shall support University → Faculty → Department hierarchy
- FR-00.6b The system shall support Batch → Section under departments
- FR-00.6c The system shall allow multiple academic terms/semesters
- FR-00.6d Each term shall have its own timetable versions

#### UC-00: Export Timetable
- FR-00.1 The system shall export timetable to PDF (printable format)
- FR-00.2 The system shall export timetable to Excel (.xlsx)
- FR-00.3 The system shall export timetable to CSV (for external systems)
- FR-00.4 Export shall include all relevant columns: day, time, course, teacher, room, section
- FR-00.5 PDF export shall be formatted for A4 printing
- FR-00.5a Export shall support exam schedule export to PDF
- FR-00.5b Export shall support exam schedule export to Excel

#### UC-00: Notifications
- FR-00.6 The system shall send in-app notifications to users
- FR-00.7 Users shall see notification bell/icon with unread count
- FR-00.8 Notifications shall be sent when timetable is published
- FR-00.9 Notifications shall be sent when timetable generation completes
- FR-00.10 Notifications shall be sent when change request status updates
- FR-00.11 Notifications shall be sent when change request is approved/rejected
- FR-00.12 Notifications shall be sent when timetable entry is locked/unlocked
- FR-00.13 Notifications shall be sent when new timetable version is created
- FR-00.14 Users shall be able to view notification history

#### UC-00: Version Comparison
- FR-00.15 The system shall allow comparing two timetable versions side-by-side
- FR-00.16 Changed entries shall be highlighted in color (e.g., yellow)
- FR-00.17 Added entries shall be highlighted (e.g., green)
- FR-00.18 Removed entries shall be highlighted (e.g., red)
- FR-00.19 The system shall show summary: total added, removed, changed count

---

### MODULE 1: CLASS TIMETABLING

#### UC-01: Maintain Academic Calendar
- FR-01.1 The system shall allow the Timetable Administrator to add semester dates (start, end)
- FR-01.2 The system shall allow adding holidays, blackout dates, closure days
- FR-01.3 The system shall prevent classes on holidays or blocked dates
- FR-01.4 The system shall support makeup classes for missed sessions due to holidays
- FR-01.5 Makeup classes shall be scheduled on available days after semester ends

#### UC-02: Manage Master Data
- FR-02.1 The system shall allow adding/updating/deleting teachers with name, department, max_daily_load
- FR-02.1a Default max_daily_load shall be 4 classes per day
- FR-02.2 The system shall allow managing rooms with building, floor, capacity, room_type, features
- FR-02.2a Room capacity shall be >= section size (not exact match)
- FR-02.3 The system shall allow managing sections with name, department, size, student list
- FR-02.3a Section can have multiple courses per semester
- FR-02.4 The system shall allow managing courses with teacher, section, weekly sessions, required room type
- FR-02.4a Each course has one teacher assigned
- FR-02.4b Lab courses shall only use lab rooms
- FR-02.5 The system shall support class duration: 1 hour, 1.5 hours, or 2 hours per session
- FR-02.6 Days shall be Monday to Friday (weekdays only, no weekend)
- FR-02.6a There shall be 15-minute break between class slots
- FR-02.6b Sessions with break automatically calculated (e.g., 8:30-10:00, 10:15-11:45)

#### UC-03: Define Constraints and Preferences
**Hard Constraints:**
- FR-03.1 No teacher clash (same teacher, same timeslot)
- FR-03.2 No room clash (same room, same timeslot)
- FR-03.3 No section clash (same section, same timeslot)
- FR-03.4 Room capacity >= section size
- FR-03.5 Lab courses → lab rooms only
- FR-03.6 Holiday exclusion
- FR-03.7 Teacher availability enforcement
- FR-03.7a Teachers shall be able to specify their unavailable times (detailed input)
- FR-03.7b Teachers shall mark specific day/time slots as unavailable
- FR-03.7c Unavailable times shall be stored in teacher availability table
- FR-03.8 University hours: all classes within start/end time (08:30 - 16:00)

**Soft Preferences (Configurable):**
- FR-03.9 Morning preference option
- FR-03.10 Early ending preference
- FR-03.11 Room proximity preference
- FR-03.12 Energy-saving (building compaction) option
- FR-03.13 Traffic reduction option
- FR-03.14 2-hour class options: single per day, morning only, continuous, late allowed
- FR-03.15 Holiday maximization preference

#### UC-04: Generate Timetable
- FR-04.1 The system shall generate a complete weekly timetable
- FR-04.2 The system shall enforce all hard constraints
- FR-04.3 The system shall optimize for selected soft preferences
- FR-04.4 The system shall return unplaced sessions with reasons
- FR-04.5 The system shall calculate quality score and penalty breakdown
- FR-04.6 Generation shall run in background without blocking UI
- FR-04.7 The system shall show progress indicator during generation
- FR-04.7a The system shall automatically resolve conflicts without user intervention
- FR-04.7b When conflict found, system shall try alternative room/time automatically
- FR-04.7c If all alternatives exhausted, show unplaced with reason

#### UC-05: Review Timetable Quality
- FR-05.1 The system shall display timetable in weekly grid view
- FR-05.2 The system shall show hard conflicts with details
- FR-05.3 The system shall display soft penalty breakdown
- FR-05.4 The system shall show room utilization statistics
- FR-05.5 The system shall show teacher load per day

#### UC-06: Manual Adjustment and Locking
- FR-06.1 The system shall allow manual timetable entry adjustment
- FR-06.2 The system shall validate manual changes against constraints
- FR-06.3 The system shall allow locking specific entries
- FR-06.4 Locked entries shall not change during re-optimization

#### UC-07: Re-optimization
- FR-07.1 The system shall re-optimize after approved changes
- FR-07.2 The system shall minimize disruption to existing entries
- FR-07.3 Locked entries shall remain unchanged

#### UC-08: Publish Timetable
- FR-08.1 The system shall allow publishing approved timetable
- FR-08.1a Both Department Coordinator and Admin must approve before publishing
- FR-08.2 Published timetable shall be visible to teachers
- FR-08.3 Published timetable shall be visible to students (by section)
- FR-08.4 Only one timetable shall be published per term
- FR-08.4a Maximum 10 draft versions shall be stored per term
- FR-08.4b Old drafts beyond 10 shall be archived automatically

#### UC-09: View Personal Timetable
- FR-09.1 Teachers shall view their weekly teaching schedule
- FR-09.2 Students shall view their section's timetable
- FR-09.3 Views shall show course, room, time, teacher details

#### UC-10: Change Requests
- FR-10.1 Teachers shall submit timetable change requests with reason
- FR-10.1a Reason shall be optional (not required)
- FR-10.2 Department Coordinators shall review/approve requests
- FR-10.3 Approved requests shall trigger re-optimization

---

### MODULE 2: UNIVERSITY HOURS

#### UC-11: Configure University Hours
- FR-11.1 The system shall allow setting university start time (e.g., 08:30)
- FR-11.2 The system shall allow setting university end time (e.g., 16:00 or 04:00 PM)
- FR-11.3 All classes shall be scheduled within university hours

---

### MODULE 3: EXAM TIMETABLING

#### UC-15: Manage Exam Rooms
- FR-15.1 The system shall allow adding rooms with capacity
- FR-15.2 The system shall allow room types: classroom, lab, conference, group study
- FR-15.3 The system shall allow optional distance graph between buildings
- FR-15.4 Room data shall be reusable from class timetable

#### UC-16: Manage Student Hierarchy
- FR-16.1 The system shall store: University → Faculty → Department → Batch → Section → Students
- FR-16.2 Student details: name, ID, registration number
- FR-16.3 The system shall display hierarchical tree view
- FR-16.4 Section shall link to enrolled courses

#### UC-17: Manage Exam Courses
- FR-17.1 The system shall associate courses with exams
- FR-17.2 The system shall store exam duration (1h, 2h, 3h)
- FR-17.3 The system shall link courses to taking sections

#### UC-18: Exam Scheduling
- FR-18.1 The system shall suggest available room+time slots
- FR-18.2 Admin shall confirm/modify suggestions
- FR-18.3 No student shall have overlapping exams
- FR-18.3a Normally one exam per day per student
- FR-18.3b Maximum two exams per day allowed if exam days running out
- FR-18.4 No room double-booking allowed (block)
- FR-18.5 Room capacity must accommodate enrolled students
- FR-18.6 Exams shall be scheduled on weekdays and Saturdays
- FR-18.7 Exams shall start at 9:00 AM
- FR-18.8 15-minute check-in time shall be allocated before each exam session

#### UC-19: Exam Views
- FR-19.1 Students shall view their exam schedule
- FR-19.2 Teachers shall view invigilation duties
- FR-19.2a The system shall suggest invigilation assignments based on availability
- FR-19.2b Admin shall confirm/modify invigilation assignments
- FR-19.3 Facility managers shall view room usage
- FR-19.4 The system shall export exam schedule to PDF
- FR-19.5 The system shall export exam schedule to Excel

---

### MODULE 4: SYSTEM ADMINISTRATION

#### UC-20: User Management
- FR-20.1 System Administrator shall create user accounts
- FR-20.2 System Administrator shall assign roles
- FR-20.3 Role-based access shall be enforced
- FR-20.4 Teachers shall be able to self-register with email verification
- FR-20.5 Students shall be able to self-register with email verification
- FR-20.6 Admin shall be able to bulk import students from Excel/CSV file
- FR-20.7 Bulk import shall map columns: name, ID, registration number, section
- FR-20.8 Students shall be bulk imported with course enrollments

#### UC-21: System Reports
- FR-21.1 Room utilization reports
- FR-21.2 Teacher load reports (daily/weekly)
- FR-21.3 Conflict summaries
- FR-21.4 Audit logs
- FR-21.4a The system shall track all manual edits in audit log
- FR-21.4b The system shall show full action history
- FR-21.4c Users shall be able to view who made each change
- FR-21.4d Each action shall show timestamp and old/new values
- FR-21.5 Late class report (classes after specified time)
- FR-21.6 Energy usage report (building-wise compaction)
- FR-21.7 Quality score breakdown report
- FR-21.8 Section load report (classes per day per section)

---

## 5. Non-Functional Requirements

### 5.1 Performance

| Metric | Target |
|--------|--------|
| Page load time | < 1 second |
| API response time | < 1 second |
| Timetable generation | 5-30 minutes (background) |
| Background generation | Non-blocking UI |
| Concurrent users | 1000+ |

### 5.2 Scalability

- NFR-01: Support full university (multiple departments)
- NFR-02: Handle 1000+ concurrent users
- NFR-03: Store 10,000+ timetable entries
- NFR-04: Database must support growth

### 5.3 Security

- NFR-05: Role-based access control
- NFR-06: Input validation on all endpoints
- NFR-07: Audit logging for all changes
- NFR-08: Session management
- NFR-08a: Error messages shall be user-friendly (not technical)
- NFR-08b: Sensitive errors shall be logged but not shown to users
- NFR-08c: Mobile responsive design (future consideration)

### 5.4 Usability

- NFR-09: Weekly grid view for timetable
- NFR-09a: Timetable shall display with time slots as columns (horizontal)
- NFR-09b: Each day shall have its own column (Monday, Tuesday, etc.)
- NFR-09c: Entries shall be color-coded by course for easy identification
- NFR-10: Conflict warnings in plain language
- NFR-11: Consistent UI labels
- NFR-12: Progress indicators for long operations
- NFR-12a: Export buttons for PDF/Excel/CSV
- NFR-12b: Notification bell icon with unread count
- NFR-12c: Version comparison side-by-side view
- NFR-12d: Tab-based navigation for sections/days
- NFR-12e: Search functionality for finding entries
- NFR-12f: Filter by teacher, room, course, day
- NFR-12g: Dashboard showing system status and current term info
- NFR-12h: Help tooltips on hover
- NFR-12i: Help menu in navigation
- NFR-12j: Full help documentation page with tutorials
- NFR-12k: Video tutorials linked in help documentation
- NFR-12l: Text tutorials with screenshots

### 5.5 Availability

- NFR-13: Published timetable always accessible
- NFR-14: Version control for drafts
- NFR-15: Database backup capability
- NFR-15a: Data validation shall check required fields before saving
- NFR-15b: Duplicate entries shall be warned and blocked
- NFR-15c: Invalid data shall prevent save until corrected

### 5.6 Maintainability

- NFR-16: Modular architecture
- NFR-17: Swappable solver interface
- NFR-18: Separate module configurations

---

## 6. Architecture

### 6.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND                                │
│  (HTML/CSS/JavaScript - Vanilla, no build step)             │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/REST
┌─────────────────────┴───────────────────────────────────────┐
│                  BACKEND API                                │
│  Python HTTP Server (ThreadingHTTPServer)                   │
│  - Authentication/Authorization                          │
│  - Validation                                           │
│  - Business Logic                                       │
│  - Solver Orchestration                                 │
│  - Background Jobs (future)                            │
└───────┬──────────────────────┬───────────────────┬────────┘
        │                      │                   │
┌───────┴───────┐ ┌───────────┴────────┐ ┌───────────────┐
│   DATABASE    │ │  SOLVER ENGINE  │ │   SERVICES   │
│   SQLite    │ │  TimetableAlgo │ │  Bootstrap  │
│  (current)  │ │  CP-SAT      │ │  Timetable  │
│             │ │  (future)    │ │            │
└─────────────┘ └───────────────┘ └─────────────┘
```

### 6.2 Technology Stack

| Component | Current | Future Consideration |
|-----------|---------|---------------------|
| Frontend | Vanilla JS/CSS | - |
| Backend | Python stdlib | - |
| Database | SQLite | PostgreSQL for scale |
| Solver | Custom BFS | OR-Tools CP-SAT |
| Server | http.server | Consider ASGI |
| Jobs | Synchronous | Redis queue for background |

### 6.3 Module Separation

The two modules operate as subsystems:

1. **Class Timetabling** - Core weekly scheduling
2. **Exam Timetabling** - Separate but uses shared room data

---

## 7. Data Model

### Core Entities

```
┌─────────────────┐     ┌─────────────────┐
│      User        │     │     Role       │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id            │
│ name            │     │ name          │
│ email           │     │ permissions   │
│ password        │     │              │
│ role_id         │────<│              │
│ department_id  │     │              │
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│   Faculty       │     │   AcademicTerm │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id           │
│ name           │     │ name         │
│ university_id │     │ start_date   │
└─────────────────┘     │ end_date    │
                         │ is_active  │
                         └───────────┘

┌─────────────────┐     ┌─────────────────┐
│   Department    │     │    Teacher     │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │
│ name           │────<│ user_id         │
│ faculty_id     │     │ department_id   │
│ head_id        │     │ max_daily_load  │
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│     Room        │     │    Section      │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id              │
│ code            │     │ name           │
│ building       │────<│ department_id   │
│ floor          │     │ size          │
│ capacity      │     │ is_day_scholar │
│ room_type     │     │ batch_id       │
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│    Course       │     │   Timeslot     │
├─────────────────┤     ├─────────────────┤
│ id              │     │ id             │
│ code            │     │ day           │
│ title          │     │ start_time    │
│ teacher_id    │────<│ end_time     │
│ section_id    │     │ duration     │
│ weekly_sessions│    │ is_morning   │
│ duration      │     │ is_last_slot │
│ req_room_type │     │ sort_order   │
└─────────────────┘     └─────────────────┘

┌─────────────────┐
│ TimetableEntry  │
├─────────────────
│ id             │
│ version_id     │
│ course_id     │
│ teacher_id    │
│ section_id    │
│ room_id       │
│ timeslot_id   │
│ is_locked     │
│ duration      │
└─────────────────┘

┌─────────────────┐
│  VersionDiff   │
├─────────────────
│ id             │
│ version_a_id   │
│ version_b_id   │
│ added_count   │
│ removed_count │
│ changed_count │
│ diff_details  │
│ created_at    │
└─────────────────┘

For EXAM Module additional:
┌─────────────────┐     ┌─────────────────┐
│  ExamCourse    │     │  ExamSession   │
├─────────────────┤     ├─────────────────┤
│ course_id     │     │ id              │
│ exam_duration│────<│ exam_course_id │
│                │     │ room_id         │
│                │     │ date           │
│                │     │ start_time    │
│                │     │ end_time      │
└─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐
│   Building     │     │  DistanceGraph │
├─────────────────┤     ├─────────────────┤
│ id              │     │ from_building │
│ name           │     │ to_building  │
│                │     │ distance_km  │
└─────────────────┘     └─────────────────┘

Student Hierarchy (tree):
University → Faculty → Department → Batch → Section → Student

Notification Entities:
┌─────────────────┐     ┌─────────────────┐
│  Notification  │     │ NotificationUser │
├─────────────────┤     ├─────────────────┤
│ id              │     │ notification_id │
│ type            │────<│ user_id         │
│ title           │     │ is_read        │
│ message        │     │ created_at     │
│ link           │     │                │
│ created_at     │     │                │
└─────────────────┘     └─────────────────┘

Notification Types: publish, generate_complete, change_request, approve, reject, lock, unlock, version_create, exam_published, exam_reminder
```

---

## 8. Process Model

### 8.1 Selected Model

**Primary:** Incremental Process Model  
**Supporting:** Prototyping for UI validation

### 8.2 Planned Increments

| Increment | Module | Focus |
|-----------|--------|-------|
| 1 | All | Master data + Academic Calendar |
| 2 | Class | Hard constraints + basic generation |
| 3 | Class | Soft preferences + quality scoring |
| 4 | Class | Review + manual adjustment + locking |
| 5 | Class | Re-optimization + versioning |
| 6 | Class | Publish + role views |
| 7 | Exam | Room management + hierarchy |
| 8 | Exam | Exam scheduling |
| 9 | System | Background jobs + scale |
| 10 | All | Polish + integration |

---

## 9. Constraints and Assumptions

### 9.1 Project Constraints

- Single Python process for MVP
- SQLite database (scalability to be analyzed)
- Browser-based UI
- Semester timeline

### 9.2 Assumptions

- Full university will have 1000+ concurrent users
- Generation can take up to 30 minutes for large datasets
- Background processing required for non-blocking UI
- Room data shared between class and exam modules

---

## 10. Acceptance Criteria

### Class Timetabling
- [ ] System generates clash-free timetable for typical department
- [ ] Hard constraints enforced
- [ ] Soft preferences configurable
- [ ] UI responsive (< 1s page load)
- [ ] Generation runs in background
- [ ] Lock/unlock functionality works
- [ ] Published timetable visible to teachers/students

### Exam Timetabling
- [ ] Rooms with capacity and type stored
- [ ] Student hierarchy displayed
- [ ] Exam suggestions provided
- [ ] Admin can modify suggestions
- [ ] No student double-booking

### System
- [ ] Role-based access enforced
- [ ] 1000+ concurrent user support (verified at scale)
- [ ] Background generation non-blocking

---

## 11. Future Considerations (Not in v1.0)

- PostgreSQL upgrade for larger scale
- Redis job queue for background processing
- OR-Tools CP-SAT solver
- Multi-campus deployment
- Email/SMS notifications

---

## 12. References

- Andrea Bettinelli et al., "An overview of curriculum-based course timetabling", TOP, 2015
- Google OR-Tools CP-SAT Documentation
- Lewis, R. "Post Enrolment based Course Timetabling", 2007

---

*This SRS is a living document and will be updated as the project progresses.*