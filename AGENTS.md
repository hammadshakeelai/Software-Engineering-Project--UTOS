# AGENTS.md

## Critical Development Notes

### Backend Entry Point
```bash
python -m app.backend.server
```
Access at `http://127.0.0.1:8000`. Port can be changed via `UTOS_PORT` env var.

### Running Tests
```bash
python -B -m unittest discover -v
```
Single test: `python -m unittest tests.test_solver -v`

### Frontend
Vanilla JS/CSS - no build step required. Edit `index.html` or `scripts/*.js` directly.

### Known Issue
- `PUT /api/timetable/{id}/publish` crashes the server - avoid using it

### Role-Based Access
- 5 roles: administrator, coordinator, teacher, student, facility_manager
- Login uses localStorage session (no password)
- Permissions enforced at render level in `render.js`

### Key Files
- `app/backend/server.py` - HTTP routing, no frameworks
- `app/backend/algorithms/timetable_solver.py` - swappable solver
- `app/frontend/scripts/render.js` - UI rendering with role checks
- `app/frontend/scripts/state.js` - global state, contains `currentUser`

### Database
- Auto-created at `app/data/utos.sqlite` on first run
- Schema in `app/backend/schema.sql`, seeded by `app/backend/seed.py`

### Common Pitfalls
1. Don't duplicate functions across files - import instead
2. When editing render.js, ensure exported functions are used in main.js
3. Backend has no auth - frontend role checks are the only access control
4. Python stdlib only - no pip packages needed
5. Follow DRY (Don't Repeat Yourself) - extract shared code into reusable modules
6. Keep functions small and focused (Single Responsibility Principle)
7. Use consistent naming and follow existing code conventions
8. Test changes before committing - run `python -m unittest discover -v`