from __future__ import annotations

import sqlite3

from ..algorithms.timetable_solver import TimetableSolver
from ..repositories.master_data import get_solver_problem
from ..repositories.timetable_repository import (
    compare_versions,
    get_latest_version,
    get_reports,
    save_timetable_result,
)


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


def reoptimize_timetable(conn: sqlite3.Connection) -> dict:
    """Repair the latest draft: locked entries stay fixed, everything else may move."""
    previous = get_latest_version(conn)
    if previous is None:
        return generate_timetable(conn)

    problem = get_solver_problem(conn)
    problem["locked_entries"] = [
        entry
        for entry in previous["entries"]
        if entry["locked"] and entry["status"] == "placed"
    ]
    solver = TimetableSolver()
    result = solver.solve(problem)
    version_id = save_timetable_result(conn, result, name_prefix="Re-optimized draft")
    conn.commit()

    diff = compare_versions(conn, previous["id"], version_id)
    latest = get_latest_version(conn)
    return {
        "versionId": version_id,
        "result": result,
        "latestTimetable": latest,
        "reports": get_reports(conn, version_id),
        "comparedTo": previous["id"],
        "disruption": {
            **diff["totals"],
            "unchanged": diff["unchanged_count"],
            "locked_preserved": len(problem["locked_entries"]),
        },
    }
