# SRS Comparison Report: SRS.md vs SRS_v1.0_Full_Scope.md

## Overview

| Aspect | SRS.md | SRS_v1.0_Full_Scope.md |
|--------|-------|----------------------|
| **Version** | 0.1 (rough baseline) | 1.0 (Full Scope) |
| **Date** | 2026-04-26 | May 2026 |
| **Status** | MVP/Prototype | Production-ready spec |

---

## Scope Comparison

### SRS.md (v0.1) - SINGLE MODULE
- Class Timetabling only
- Single department
- Basic weekly scheduling

### SRS_v1.0 (v1.0) - TWO MODULES

| Module | Description |
|--------|-------------|
| **Module 1** | Class Timetabling (enhanced) |
| **Module 2** | Exam Timetabling |

---

## Feature Gap Analysis

### What's ONLY in SRS.md (v0.1)

| Feature | Notes |
|---------|-------|
| Basic soft preferences | morning, early ending, room proximity, energy saving, traffic reduction |
| Lock/unlock entries | Basic implementation |
| Change request workflow | Basic submit + approve/reject |
| Version control | Draft/published/archived |

### What's ONLY in SRS_v1.0 (Full Scope)

| Feature | Module | Priority |
|---------|--------|----------|
| Real authentication (password) | System-wide | HIGH |
| Organization hierarchy (University → Faculty → Dept) | System-wide | HIGH |
| Export (PDF/Excel/CSV) | System-wide | HIGH |
| Notifications | System-wide | HIGH |
| Version comparison (side-by-side) | System-wide | HIGH |
| Variable class duration (1h, 1.5h, 2h) | Module 1 | HIGH |
| Exam timetabling | Module 2 | HIGH |
| Student hierarchy tree | Module 2 | HIGH |
| Exam courses + sessions | Module 2 | MEDIUM |
| Invigilation duties | Module 2 | MEDIUM |
| Bulk student import | System | MEDIUM |
| Audit logging | System | MEDIUM |
| Background generation | System | MEDIUM |
| University hours config | Module 1 | LOW |
| Multiple approval for publish | Module 1 | LOW |
| Max 10 drafts per term | Module 1 | LOW |

---

## Functional Requirements Matrix

| UC | Feature | SRS v0.1 | SRS v1.0 | Status in Audit |
|----|---------|:--------:|:--------:|:--------------:|
| UC-00 | Authentication | ❌ | ✅ | ❌ Missing |
| UC-00 | Organization Hierarchy | ❌ | ✅ | ❌ Missing |
| UC-00 | Export | ❌ | ✅ | ❌ Missing |
| UC-00 | Notifications | ❌ | ✅ | ❌ Missing |
| UC-00 | Version Comparison | ❌ | ✅ | ❌ Missing |
| UC-01 | Academic Calendar | ✅ | ✅ | ✅ Implemented (holidays) |
| UC-02 | Master Data CRUD | ✅ | ✅ | ✅ Full CRUD |
| UC-03 | Hard Constraints | ✅ | ✅ | ✅ Implemented |
| UC-03 | Soft Preferences | ✅ | ✅ | ✅ Implemented |
| UC-04 | Generate Timetable | ✅ | ✅ | ✅ Working |
| UC-05 | Review Quality | ✅ | ✅ | ✅ Partial |
| UC-06 | Change Requests | ✅ | ✅ | ✅ Working |
| UC-07 | Lock/Unlock | ✅ | ✅ | ✅ Working |
| UC-08 | Publish | ⚠️ | ✅ | ❌ Crashes |
| UC-09 | View Personal | ✅ | ✅ | ✅ Working |
| UC-10 | Reports | ✅ | ✅ | ✅ Working |
| UC-11 | Exam Timetabling | ❌ | ✅ | ❌ Not started |
| UC-12 | User Management | ❌ | ✅ | ❌ Not started |

**Legend:**
- ✅ = Implemented in current build
- ⚠️ = Partially/broken
- ❌ = Not implemented

---

## User Roles Comparison

| Role | SRS v0.1 | SRS v1.0 |
|------|:--------:|:--------:|
| Administrator | ✅ | ✅ |
| Coordinator | ✅ | ✅ |
| Teacher | ✅ | ✅ |
| Student | ✅ | ✅ |
| Facility Manager | ✅ | ✅ |
| System Administrator | ✅ | ✅ |

**Note:** Both docs define the same 6 roles.

---

## Data Model Comparison

### Tables in SRS.md (current implementation)

| Table | In SRS v1.0? | Implemented? |
|-------|:------------:|:-----------:|
| users | ✅ (enhanced) | ✅ |
| teachers | ✅ | ✅ |
| rooms | ✅ | ✅ |
| sections | ✅ | ✅ |
| courses | ✅ | ✅ |
| timeslots | ✅ | ✅ |
| holidays | ✅ | ✅ |
| teacher_availability | ✅ | ✅ |
| preferences | ✅ | ✅ |
| timetable_versions | ✅ | ✅ |
| timetable_entries | ✅ | ✅ |
| change_requests | ✅ | ✅ |

### New Tables for SRS v1.0

| Table | Purpose | Priority |
|-------|---------|---------|
| roles | Role permissions | HIGH |
| faculties | University hierarchy | HIGH |
| departments | University hierarchy | HIGH |
| batches | Student grouping | HIGH |
| students | Individual student data | HIGH |
| student_courses | Enrollment records | HIGH |
| building_distances | Room proximity | MEDIUM |
| exam_courses | Exam schedule | MEDIUM |
| exam_sessions | Exam schedule | MEDIUM |
| notifications | System notifications | HIGH |
| notification_users | Read status | HIGH |
| audit_logs | Change tracking | MEDIUM |
| academic_terms | Semester management | HIGH |

---

## Architecture Comparison

### SRS v0.1 - Current
```
Frontend → Python stdlib HTTP → SQLite → Solver (custom backtracking)
```

### SRS v1.0 - Planned
```
Frontend → Python HTTP → PostgreSQL → Solver (CP-SAT future)
                  → Redis (background jobs)
                  → Notification service
```

---

## Non-Functional Requirements Comparison

| NFR | SRS v0.1 | SRS v1.0 | Gap |
|-----|:-------:|:-------:|------|
| Page load | 2s target | <1s target | 2x improvement |
| API response | 2s target | <1s target | 2x improvement |
| Generation | 30s target | 5-30min | Same |
| Concurrent users | - | 1000+ | Not tested |
| Background gen | ❌ | ✅ | Missing |
| Version diff | ❌ | ✅ | Missing |

---

## Process Model

Both documents specify **Incremental Process Model** - they agree here.

SRS v0.1: 5 increments (conceptual)
SRS v1.0: 12 increments (detailed table)

---

## Summary: What's Built vs What's Planned

### Already Built (matches SRS.md)

1. ✅ Master data CRUD (teachers, rooms, sections, courses)
2. ✅ Timeslots + holidays
3. ✅ Hard constraints enforcement
4. ✅ Soft preferences
5. ✅ Timetable generation (MVP backtracking solver)
6. ✅ Lock/unlock entries
7. ✅ Basic change request workflow
8. ✅ Role-based UI
9. ✅ Dashboard + reports

### Missing from SRS.md → SRS v1.0

1. ❌ Real authentication (password-based login)
2. ❌ Organization hierarchy (faculty/department)
3. ❌ Export (PDF/Excel/CSV)
4. ❌ Notifications
5. ❌ Version comparison
6. ❌ Publish endpoint (crashes)
7. ❌ Exam timetabling module
8. ❌ Background generation
9. ❌ Audit logging
10. ❌ Bulk import
11. ❌ Multiple approvers for publish

---

## Recommendations for Clean Room Engineering

Based on this comparison:

### Priority 1 (Core - from SRS v0.1, needs fixing)

- Fix the `/publish` endpoint crash
- Add proper authentication

### Priority 2 (High - from SRS v1.0)

- Export functionality (PDF/Excel/CSV)
- Version comparison/diff
- Audit logging

### Priority 3 (Medium - from SRS v1.0)

- Organization hierarchy
- Notification system
- Background generation

### Priority 4 (Future - from SRS v1.0)

- Exam timetabling module
- PostgreSQL upgrade for scale

---

*End of Comparison Report*