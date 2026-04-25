from __future__ import annotations

import unittest

from app.backend.algorithms.timetable_solver import TimetableSolver


def base_problem() -> dict:
    return {
        "teachers": [
            {"id": 1, "name": "Teacher A", "department": "CS", "max_daily_load": 3},
            {"id": 2, "name": "Teacher B", "department": "CS", "max_daily_load": 3},
        ],
        "rooms": [
            {
                "id": 1,
                "code": "A-101",
                "building": "Alpha",
                "floor": 1,
                "capacity": 40,
                "room_type": "lecture",
                "features": "",
            },
            {
                "id": 2,
                "code": "LAB-1",
                "building": "Beta",
                "floor": 1,
                "capacity": 35,
                "room_type": "lab",
                "features": "computers",
            },
        ],
        "sections": [
            {"id": 1, "name": "BSCS-1A", "department": "CS", "size": 30},
            {"id": 2, "name": "BSCS-1B", "department": "CS", "size": 25},
        ],
        "courses": [],
        "timeslots": [
            {
                "id": 1,
                "day": "Monday",
                "start_time": "08:30",
                "end_time": "10:00",
                "sort_order": 1,
                "is_morning": 1,
                "is_last_slot": 0,
            },
            {
                "id": 2,
                "day": "Monday",
                "start_time": "10:00",
                "end_time": "11:30",
                "sort_order": 2,
                "is_morning": 1,
                "is_last_slot": 0,
            },
            {
                "id": 3,
                "day": "Tuesday",
                "start_time": "15:30",
                "end_time": "17:00",
                "sort_order": 3,
                "is_morning": 0,
                "is_last_slot": 1,
            },
        ],
        "holidays": [],
        "availability": [],
        "preferences": [
            {"key": "morning_preference", "label": "Morning", "enabled": 1, "weight": 2, "value": ""},
            {"key": "traffic_reduction", "label": "Avoid last", "enabled": 1, "weight": 3, "value": ""},
        ],
    }


class TimetableSolverTests(unittest.TestCase):
    def test_solver_places_simple_problem_without_hard_conflicts(self) -> None:
        problem = base_problem()
        problem["courses"] = [
            {
                "id": 1,
                "code": "CS-101",
                "title": "Intro CS",
                "teacher_id": 1,
                "teacher_name": "Teacher A",
                "section_id": 1,
                "section_name": "BSCS-1A",
                "section_size": 30,
                "weekly_sessions": 2,
                "required_room_type": "lecture",
            }
        ]

        result = TimetableSolver().solve(problem)

        self.assertEqual(result["metrics"]["hard_conflicts"], 0)
        self.assertEqual(result["metrics"]["unplaced_count"], 0)
        self.assertEqual(len(result["entries"]), 2)

    def test_solver_respects_room_teacher_and_section_slot_conflicts(self) -> None:
        problem = base_problem()
        problem["courses"] = [
            {
                "id": 1,
                "code": "CS-101",
                "title": "Intro CS",
                "teacher_id": 1,
                "teacher_name": "Teacher A",
                "section_id": 1,
                "section_name": "BSCS-1A",
                "section_size": 30,
                "weekly_sessions": 2,
                "required_room_type": "lecture",
            },
            {
                "id": 2,
                "code": "CS-102",
                "title": "Advanced CS",
                "teacher_id": 1,
                "teacher_name": "Teacher A",
                "section_id": 2,
                "section_name": "BSCS-1B",
                "section_size": 25,
                "weekly_sessions": 1,
                "required_room_type": "lecture",
            },
        ]

        result = TimetableSolver().solve(problem)

        teacher_slots = {(entry["teacher_id"], entry["timeslot_id"]) for entry in result["entries"]}
        section_slots = {(entry["section_id"], entry["timeslot_id"]) for entry in result["entries"]}
        room_slots = {(entry["room_id"], entry["timeslot_id"]) for entry in result["entries"]}
        self.assertEqual(len(teacher_slots), len(result["entries"]))
        self.assertEqual(len(section_slots), len(result["entries"]))
        self.assertEqual(len(room_slots), len(result["entries"]))

    def test_solver_blocks_holidays_and_teacher_unavailability(self) -> None:
        problem = base_problem()
        problem["holidays"] = [{"id": 1, "name": "Holiday", "day": "Tuesday"}]
        problem["availability"] = [{"teacher_id": 1, "timeslot_id": 1, "is_available": 0}]
        problem["courses"] = [
            {
                "id": 1,
                "code": "CS-101",
                "title": "Intro CS",
                "teacher_id": 1,
                "teacher_name": "Teacher A",
                "section_id": 1,
                "section_name": "BSCS-1A",
                "section_size": 30,
                "weekly_sessions": 1,
                "required_room_type": "lecture",
            }
        ]

        result = TimetableSolver().solve(problem)

        self.assertEqual(result["metrics"]["unplaced_count"], 0)
        self.assertEqual(result["entries"][0]["timeslot_id"], 2)

    def test_solver_reports_infeasible_room_capacity(self) -> None:
        problem = base_problem()
        problem["courses"] = [
            {
                "id": 1,
                "code": "CS-999",
                "title": "Huge Course",
                "teacher_id": 1,
                "teacher_name": "Teacher A",
                "section_id": 1,
                "section_name": "BSCS-1A",
                "section_size": 99,
                "weekly_sessions": 1,
                "required_room_type": "lecture",
            }
        ]

        result = TimetableSolver().solve(problem)

        self.assertEqual(result["metrics"]["unplaced_count"], 1)
        self.assertEqual(result["metrics"]["distance_to_feasibility"], 99)
        self.assertIn("Some sessions could not be placed", " ".join(result["warnings"]))

    def test_solver_uses_lab_room_for_lab_course(self) -> None:
        problem = base_problem()
        problem["courses"] = [
            {
                "id": 1,
                "code": "LAB-101",
                "title": "Programming Lab",
                "teacher_id": 2,
                "teacher_name": "Teacher B",
                "section_id": 2,
                "section_name": "BSCS-1B",
                "section_size": 25,
                "weekly_sessions": 1,
                "required_room_type": "lab",
            }
        ]

        result = TimetableSolver().solve(problem)

        self.assertEqual(result["metrics"]["unplaced_count"], 0)
        self.assertEqual(result["entries"][0]["room_code"], "LAB-1")

    def test_solver_backtracks_when_first_room_choice_blocks_later_event(self) -> None:
        problem = base_problem()
        problem["rooms"] = [
            {
                "id": 1,
                "code": "LAB-1",
                "building": "Beta",
                "floor": 1,
                "capacity": 30,
                "room_type": "lab",
                "features": "computers",
            },
            {
                "id": 2,
                "code": "A-101",
                "building": "Alpha",
                "floor": 1,
                "capacity": 40,
                "room_type": "lecture",
                "features": "",
            },
        ]
        problem["timeslots"] = [problem["timeslots"][0]]
        problem["courses"] = [
            {
                "id": 1,
                "code": "CS-101",
                "title": "Lecture",
                "teacher_id": 1,
                "teacher_name": "Teacher A",
                "section_id": 1,
                "section_name": "BSCS-1A",
                "section_size": 30,
                "weekly_sessions": 1,
                "required_room_type": "lecture",
            },
            {
                "id": 2,
                "code": "LAB-101",
                "title": "Lab",
                "teacher_id": 2,
                "teacher_name": "Teacher B",
                "section_id": 2,
                "section_name": "BSCS-1B",
                "section_size": 25,
                "weekly_sessions": 1,
                "required_room_type": "lab",
            },
        ]

        result = TimetableSolver().solve(problem)

        room_by_course = {entry["course_code"]: entry["room_code"] for entry in result["entries"]}
        self.assertEqual(result["metrics"]["unplaced_count"], 0)
        self.assertEqual(room_by_course["CS-101"], "A-101")
        self.assertEqual(room_by_course["LAB-101"], "LAB-1")

    def test_soft_penalty_applies_for_last_non_morning_slot(self) -> None:
        problem = base_problem()
        problem["timeslots"] = [problem["timeslots"][2]]
        problem["courses"] = [
            {
                "id": 1,
                "code": "CS-101",
                "title": "Intro CS",
                "teacher_id": 1,
                "teacher_name": "Teacher A",
                "section_id": 1,
                "section_name": "BSCS-1A",
                "section_size": 30,
                "weekly_sessions": 1,
                "required_room_type": "lecture",
            }
        ]

        result = TimetableSolver().solve(problem)

        self.assertEqual(result["metrics"]["soft_penalty"], 5)
        self.assertEqual(result["metrics"]["score"], 95)


if __name__ == "__main__":
    unittest.main()
