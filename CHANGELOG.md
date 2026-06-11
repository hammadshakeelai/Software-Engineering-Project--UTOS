# Changelog

## SRS Implementation, Hardening & Deployment (2026-06)

**Broken features fixed**
- Publish endpoint no longer crashes; it archives the previous published version
  and notifies affected users (regression-tested).
- Teachers and students now see the **published** timetable filtered to their
  identity (not the latest draft).

**New features**
- Master-data CRUD UI with edit-in-place (teachers, rooms, sections, courses)
  plus holiday and timeslot management and a per-teacher availability grid.
- Soft-preference configuration (enable/disable + weight 0–10).
- Re-optimization that preserves locked entries and reports a disruption summary;
  "Re-generate with this change" from an approved change request.
- Timetable versioning + side-by-side comparison.
- In-app notifications with unread badge; audit log viewer.
- Reports: room utilization (peak/free flags), teacher load vs. limit, section gaps.
- CSV export and print stylesheet.
- Unplaced sessions now explain *why* they could not be placed.

**Hardening**
- Server-side input validation (room types, weekdays, HH:MM, string length) and
  correct status codes (400/403/404/405/409).
- Backend role enforcement via the `X-User-Id` header (403 when insufficient).
- Room/timeslot deletion blocked when referenced by a saved timetable.
- SQLite `busy_timeout` for concurrent requests.
- Verified by a 33-check adversarial red-team suite (`tools/redteam.py`) and a
  realistic + a deliberately-infeasible dataset (`tools/university_seed.py`,
  `tools/stress_seed.py`). Test suite expanded to ~160 passing tests.

**Deployment**
- Made the app host-aware (`UTOS_HOST`, `PORT`, `UTOS_DATA_DIR`); added
  `render.yaml`, `Procfile`, `requirements.txt`, and `DEPLOY.md`. Live on Render.
- Login shows a "waking up" state during free-tier cold starts.

**Repo cleanup**
- Wrote a real top-level README; corrected stale `AGENTS.md` notes and a
  machine-specific path in `app/README.md`; broadened `.gitignore`; removed
  committed server-log artifacts.

## Recent Changes

### Login Page Fixes (2026-05-02)

**Issue**: Login page had duplicate functions causing JavaScript errors.

**Changes Made**:

1. **render.js** - Fixed duplicate function definitions:
   - Removed duplicate `selectUserByIndex` (was defined twice)
   - Removed duplicate `updateRoleBadge` (was defined twice)  
   - Fixed `renderNav()` to properly update nav links based on role
   - Added `renderAll()` function that was missing

2. **main.js** - Removed duplicate local functions:
   - Removed local `selectUserByIndex` - now imports from `render.js`
   - Removed local `updateRoleBadge` - now imports from `render.js`
   - Updated imports to include `selectUserByIndex` and `updateRoleBadge`

**Before**: Both `render.js` and `main.js` had their own copies of `selectUserByIndex` and `updateRoleBadge`, causing duplicate definition errors.

**After**: Functions are defined once in `render.js` and imported where needed in `main.js`.