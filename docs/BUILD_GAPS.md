# Current Build Gaps vs SRS v1.0

## What's Missing / Not Working

### Critical Bugs
- [ ] Publish endpoint crashes server (avoid using PUT /api/timetable/{id}/publish)

### Authentication
- [ ] No real password authentication
- [ ] Uses localStorage only

### Class Timetable (Module 1)
- [ ] Variable class duration (1h, 1.5h, 2h not supported)
- [ ] 2-hour class handling
- [ ] Organization hierarchy (faculty/department/batch not supported)

### System-Wide Features
- [ ] Export (PDF/Excel/CSV)
- [ ] Notifications
- [ ] Version comparison (side-by-side)
- [ ] Background generation (non-blocking UI)
- [ ] Multiple approvers for publish
- [ ] Audit logging

### Exam Timetabling (Module 2)
- [ ] NOT in current build - removed from scope

---

## Scope Decision

Current build = MVP (Class Timetabling only)
SRS v1.0 target = Class Timetabling (enhanced) + Exam Timetabling

Decision: Keep Class Timetabling enhanced features in SRS, remove Exam module.

---

## Last Updated: 2026-05-03