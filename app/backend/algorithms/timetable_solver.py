from __future__ import annotations

from collections import defaultdict
from time import monotonic
from typing import Any


class TimetableSolver:
    """Transparent MVP solver for university course timetabling.

    Research grounding:
    - Curriculum and post-enrolment course timetabling are assignment problems over
      events, rooms, and timeslots with hard constraints and soft penalties.
    - The current implementation is a bounded constructive/backtracking baseline,
      not a claim of optimality. It keeps the solver interface clean for a later
      CP-SAT, tabu search, or simulated annealing adapter.
    """

    def __init__(self, time_limit_seconds: float = 5.0, max_nodes: int = 30_000) -> None:
        self.time_limit_seconds = time_limit_seconds
        self.max_nodes = max_nodes

    def solve(self, problem: dict[str, Any]) -> dict[str, Any]:
        self.started_at = monotonic()
        self.nodes = 0
        self.problem = problem
        self.rooms = problem["rooms"]
        self.timeslots = problem["timeslots"]
        self.sections_by_id = {section["id"]: section for section in problem["sections"]}
        self.teachers_by_id = {teacher["id"]: teacher for teacher in problem["teachers"]}
        self.preferences = {
            pref["key"]: pref for pref in problem["preferences"] if int(pref["enabled"]) == 1
        }
        self.holiday_days = {holiday["day"] for holiday in problem["holidays"]}
        self.availability = {
            (row["teacher_id"], row["timeslot_id"]): bool(row["is_available"])
            for row in problem["availability"]
        }
        self.available_slot_count = self._available_slot_counts()

        self.entries: list[dict[str, Any]] = []
        self.unplaced: list[dict[str, Any]] = []
        self.teacher_at_slot: set[tuple[int, int]] = set()
        self.section_at_slot: set[tuple[int, int]] = set()
        self.room_at_slot: set[tuple[int, int]] = set()
        self.teacher_day_load: dict[tuple[int, str], int] = defaultdict(int)
        self.teacher_last_room: dict[tuple[int, str], dict[str, Any]] = {}
        self.current_soft_penalty = 0
        self.best_entries: list[dict[str, Any]] = []
        self.best_unplaced: list[dict[str, Any]] = []
        self.best_soft_penalty = float("inf")
        self.warnings: list[str] = []

        locked_uids = self._preassign_locked(problem.get("locked_entries", []))
        events = [
            event
            for event in self._expand_events(problem["courses"])
            if event["event_uid"] not in locked_uids
        ]
        events.sort(key=self._event_pressure_key)
        self.best_unplaced = events.copy()
        self._search(events, 0)
        self.entries = [entry.copy() for entry in self.best_entries]
        self.unplaced = [entry.copy() for entry in self.best_unplaced]
        for event in self.unplaced:
            event["reason"] = self._diagnose_unplaced(event)

        soft_penalty = sum(entry["soft_penalty"] for entry in self.entries)
        distance_to_feasibility = sum(entry["section_size"] for entry in self.unplaced)
        hard_conflicts = 0 if not self.unplaced else len(self.unplaced)
        score = max(0, 100 - (hard_conflicts * 15) - soft_penalty)
        if self.nodes >= self.max_nodes:
            self.warnings.append("Solver node limit reached before exhaustive search.")
        if monotonic() - self.started_at >= self.time_limit_seconds:
            self.warnings.append("Solver time limit reached before exhaustive search.")
        if self.unplaced:
            self.warnings.append("Some sessions could not be placed without violating hard constraints.")

        return {
            "entries": self.entries,
            "unplaced": self.unplaced,
            "warnings": self.warnings,
            "metrics": {
                "score": score,
                "hard_conflicts": hard_conflicts,
                "soft_penalty": soft_penalty,
                "unplaced_count": len(self.unplaced),
                "distance_to_feasibility": distance_to_feasibility,
                "search_nodes": self.nodes,
            },
        }

    def _diagnose_unplaced(self, event: dict[str, Any]) -> str:
        """Explain, in plain language, why a session has no valid placement.

        Distinguishes structural impossibility (no room is big enough / right
        type, teacher never available) from contention (rooms and slots exist
        but were all taken by other classes), so an admin knows what to fix.
        """
        required_type = event["required_room_type"]
        size = int(event["section_size"])

        type_rooms = [
            r for r in self.rooms
            if not (required_type and required_type != "lecture" and r["room_type"] != required_type)
        ]
        if not type_rooms:
            return f"No room of type '{required_type}' exists."

        big_enough = [r for r in type_rooms if int(r["capacity"]) >= size]
        if not big_enough:
            largest = max(int(r["capacity"]) for r in type_rooms)
            return (f"No {required_type} room is large enough for {size} students "
                    f"(largest holds {largest}).")

        non_holiday_slots = [s for s in self.timeslots if s["day"] not in self.holiday_days]
        if not non_holiday_slots:
            return "Every timeslot falls on a holiday."

        available_slots = [
            s for s in non_holiday_slots
            if self.availability.get((event["teacher_id"], s["id"]), True)
        ]
        if not available_slots:
            return f"{event['teacher_name']} is marked unavailable for every working timeslot."

        # Rooms and slots exist in principle: the conflict is contention with
        # other classes (teacher/section/room already busy in the open slots).
        return ("No free room and timeslot remained after placing higher-priority "
                "classes (teacher, section, or room conflicts). Add rooms/slots or "
                "relax load limits.")

    def _preassign_locked(self, locked_entries: list[dict[str, Any]]) -> set[str]:
        """Fix previously locked assignments in place (repair mode, FR-07.2).

        Locked entries occupy their teacher/section/room slots before the search
        starts, so the solver schedules everything else around them.
        """
        rooms_by_id = {room["id"]: room for room in self.rooms}
        slots_by_id = {slot["id"]: slot for slot in self.timeslots}
        locked_uids: set[str] = set()
        for locked in locked_entries:
            room = rooms_by_id.get(locked.get("room_id"))
            slot = slots_by_id.get(locked.get("timeslot_id"))
            if not room or not slot:
                self.warnings.append(
                    f"Locked entry {locked.get('event_uid')} references a missing room or timeslot; it was released."
                )
                continue
            event = {
                "event_uid": locked["event_uid"],
                "course_id": locked["course_id"],
                "course_code": locked.get("course_code", ""),
                "course_title": locked.get("course_title", ""),
                "teacher_id": locked["teacher_id"],
                "teacher_name": locked.get("teacher_name", ""),
                "section_id": locked["section_id"],
                "section_name": locked.get("section_name", ""),
                "section_size": locked.get("section_size", 0),
                "required_room_type": locked.get("required_room_type", "lecture"),
                "weekly_sessions": locked.get("weekly_sessions", 1),
            }
            self._assign(event, {"room": room, "slot": slot, "soft_penalty": 0})
            self.entries[-1]["locked"] = True
            locked_uids.add(locked["event_uid"])
        return locked_uids

    def _expand_events(self, courses: list[dict[str, Any]]) -> list[dict[str, Any]]:
        events = []
        for course in courses:
            for session_index in range(1, int(course["weekly_sessions"]) + 1):
                events.append(
                    {
                        "event_uid": f"{course['code']}-{session_index}",
                        "course_id": course["id"],
                        "course_code": course["code"],
                        "course_title": course["title"],
                        "teacher_id": course["teacher_id"],
                        "teacher_name": course["teacher_name"],
                        "section_id": course["section_id"],
                        "section_name": course["section_name"],
                        "section_size": course["section_size"],
                        "required_room_type": course["required_room_type"],
                        "weekly_sessions": course["weekly_sessions"],
                    }
                )
        return events

    def _available_slot_counts(self) -> dict[int, int]:
        counts: dict[int, int] = defaultdict(int)
        for teacher in self.problem["teachers"]:
            for slot in self.timeslots:
                if slot["day"] in self.holiday_days:
                    continue
                if self.availability.get((teacher["id"], slot["id"]), True):
                    counts[teacher["id"]] += 1
        return counts

    def _event_pressure_key(self, event: dict[str, Any]) -> tuple[int, int, int, str]:
        available_slots = self.available_slot_count.get(event["teacher_id"], len(self.timeslots))
        return (
            available_slots,
            -int(event["section_size"]),
            -int(event["weekly_sessions"]),
            event["course_code"],
        )

    def _search(self, events: list[dict[str, Any]], index: int) -> bool:
        if index >= len(events):
            self._record_best()
            return len(self.unplaced) == 0
        if self._limit_reached():
            self._record_partial_with_remaining(events[index:])
            return False

        possible_placed = len(self.entries) + (len(events) - index)
        if possible_placed < len(self.best_entries):
            return False
        if possible_placed == len(self.best_entries) and self.current_soft_penalty >= self.best_soft_penalty:
            return False

        self.nodes += 1
        event = events[index]
        candidates = self._candidate_assignments(event)
        for candidate in candidates:
            self._assign(event, candidate)
            solved = self._search(events, index + 1)
            self._undo(event, candidate)
            if solved:
                return True
            if self._limit_reached():
                self._record_partial_with_remaining(events[index + 1 :])
                return False

        self._mark_unplaced(event)
        solved = self._search(events, index + 1)
        self.unplaced.pop()
        return solved

    def _limit_reached(self) -> bool:
        return self.nodes >= self.max_nodes or monotonic() - self.started_at >= self.time_limit_seconds

    def _record_best(self) -> None:
        placed_count = len(self.entries)
        best_count = len(self.best_entries)
        if placed_count > best_count or (
            placed_count == best_count and self.current_soft_penalty < self.best_soft_penalty
        ):
            self.best_entries = [entry.copy() for entry in self.entries]
            self.best_unplaced = [entry.copy() for entry in self.unplaced]
            self.best_soft_penalty = self.current_soft_penalty

    def _record_partial_with_remaining(self, remaining_events: list[dict[str, Any]]) -> None:
        original_length = len(self.unplaced)
        self.unplaced.extend(remaining_events)
        self._record_best()
        del self.unplaced[original_length:]

    def _candidate_assignments(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        candidates = []
        for slot in self.timeslots:
            for room in self.rooms:
                if self._is_hard_feasible(event, room, slot):
                    penalty = self._soft_penalty(event, room, slot)
                    candidates.append({"room": room, "slot": slot, "soft_penalty": penalty})
        candidates.sort(
            key=lambda candidate: (
                candidate["soft_penalty"],
                candidate["slot"]["sort_order"],
                candidate["room"]["capacity"],
            )
        )
        return candidates

    def _is_hard_feasible(self, event: dict[str, Any], room: dict[str, Any], slot: dict[str, Any]) -> bool:
        if slot["day"] in self.holiday_days:
            return False
        if not self.availability.get((event["teacher_id"], slot["id"]), True):
            return False
        if int(room["capacity"]) < int(event["section_size"]):
            return False
        required_type = event["required_room_type"]
        if required_type and required_type != "lecture" and room["room_type"] != required_type:
            return False
        if (event["teacher_id"], slot["id"]) in self.teacher_at_slot:
            return False
        if (event["section_id"], slot["id"]) in self.section_at_slot:
            return False
        if (room["id"], slot["id"]) in self.room_at_slot:
            return False
        teacher = self.teachers_by_id[event["teacher_id"]]
        day_key = (event["teacher_id"], slot["day"])
        if self.teacher_day_load[day_key] >= int(teacher["max_daily_load"]):
            return False
        return True

    def _soft_penalty(self, event: dict[str, Any], room: dict[str, Any], slot: dict[str, Any]) -> int:
        penalty = 0
        if "morning_preference" in self.preferences and not int(slot["is_morning"]):
            penalty += int(self.preferences["morning_preference"]["weight"])
        if "traffic_reduction" in self.preferences and int(slot["is_last_slot"]):
            penalty += int(self.preferences["traffic_reduction"]["weight"])
        if "early_ending" in self.preferences:
            day_position = ((int(slot["sort_order"]) - 1) % 5) + 1
            penalty += max(0, day_position - 2) * int(self.preferences["early_ending"]["weight"])
        previous_room = self.teacher_last_room.get((event["teacher_id"], slot["day"]))
        if previous_room and "room_proximity" in self.preferences:
            building_jump = 0 if previous_room["building"] == room["building"] else 2
            floor_jump = abs(int(previous_room["floor"]) - int(room["floor"]))
            penalty += (building_jump + floor_jump) * int(self.preferences["room_proximity"]["weight"])
        if "energy_saving" in self.preferences:
            same_building_count = sum(
                1
                for entry in self.entries
                if entry["day"] == slot["day"] and entry["room_building"] == room["building"]
            )
            if same_building_count == 0:
                penalty += int(self.preferences["energy_saving"]["weight"])
        return penalty

    def _assign(self, event: dict[str, Any], candidate: dict[str, Any]) -> None:
        room = candidate["room"]
        slot = candidate["slot"]
        entry = {
            **event,
            "room_id": room["id"],
            "room_code": room["code"],
            "room_building": room["building"],
            "room_floor": room["floor"],
            "room_capacity": room["capacity"],
            "timeslot_id": slot["id"],
            "day": slot["day"],
            "start_time": slot["start_time"],
            "end_time": slot["end_time"],
            "sort_order": slot["sort_order"],
            "soft_penalty": candidate["soft_penalty"],
        }
        self.entries.append(entry)
        self.current_soft_penalty += candidate["soft_penalty"]
        self.teacher_at_slot.add((event["teacher_id"], slot["id"]))
        self.section_at_slot.add((event["section_id"], slot["id"]))
        self.room_at_slot.add((room["id"], slot["id"]))
        self.teacher_day_load[(event["teacher_id"], slot["day"])] += 1
        self.teacher_last_room[(event["teacher_id"], slot["day"])] = room

    def _undo(self, event: dict[str, Any], candidate: dict[str, Any]) -> None:
        room = candidate["room"]
        slot = candidate["slot"]
        removed = self.entries.pop()
        self.current_soft_penalty -= removed["soft_penalty"]
        self.teacher_at_slot.remove((event["teacher_id"], slot["id"]))
        self.section_at_slot.remove((event["section_id"], slot["id"]))
        self.room_at_slot.remove((room["id"], slot["id"]))
        day_key = (event["teacher_id"], slot["day"])
        self.teacher_day_load[day_key] -= 1
        same_day_entries = [
            entry
            for entry in self.entries
            if entry["teacher_id"] == event["teacher_id"] and entry["day"] == slot["day"]
        ]
        if same_day_entries:
            latest = same_day_entries[-1]
            self.teacher_last_room[day_key] = {
                "id": latest["room_id"],
                "building": latest["room_building"],
                "floor": latest["room_floor"],
            }
        else:
            self.teacher_last_room.pop(day_key, None)

    def _mark_unplaced(self, event: dict[str, Any]) -> None:
        self.unplaced.append(event)
