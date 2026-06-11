# UTOS Web App

This is the first modular build for the University Timetable Optimization and Management System.

Run it from the repository root:

```powershell
python -m app.backend.server
```

Then open:

```text
http://127.0.0.1:8000
```

The app uses only Python standard-library modules for the backend and SQLite database. The frontend is plain HTML, CSS, and JavaScript split into small modules. The solver is a transparent constructive/backtracking baseline designed to be replaced later by CP-SAT or another optimizer without changing the UI.

Run the automated test suite:

```bash
python -B -m unittest discover -v
```

See the top-level [README](../README.md) for full feature, architecture, and
deployment documentation.
