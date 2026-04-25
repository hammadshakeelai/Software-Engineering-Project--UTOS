from __future__ import annotations

import sqlite3

from ..algorithms.timetable_solver import TimetableSolver
from ..repositories.master_data import get_solver_problem
from ..repositories.timetable_repository import get_latest_version, get_reports, save_timetable_result


def generate_timetable(conn: sqlite3.Connection) -> dict:
    problem = get_solver_problem(conn)
    solver = TimetableSolver()
    result = solver.solve(problem)
    version_id = save_timetable_result(conn, result)
    conn.commit()
    latest = get_latest_version(conn)
    return {
        "versionId": version_id,
        "result": result,
        "latestTimetable": latest,
        "reports": get_reports(conn, version_id),
    }
