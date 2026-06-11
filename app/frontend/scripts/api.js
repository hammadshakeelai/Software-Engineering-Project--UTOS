function actorHeaders() {
  const headers = { "Content-Type": "application/json" };
  try {
    const stored = JSON.parse(localStorage.getItem("currentUser") || "null");
    if (stored?.id) headers["X-User-Id"] = String(stored.id);
  } catch {
    /* no actor header */
  }
  return headers;
}

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: actorHeaders(),
    ...options
  });
  if (!response.ok) {
    let message = `Request failed: ${response.status}`;
    try {
      const payload = await response.json();
      if (payload.error) message = payload.error;
    } catch {
      /* keep default message */
    }
    throw new Error(message);
  }
  return response.json();
}

export const api = {
  bootstrap() {
    return request("/api/bootstrap");
  },
  generateTimetable() {
    return request("/api/timetable/generate", { method: "POST" });
  },
  reoptimizeTimetable() {
    return request("/api/timetable/reoptimize", { method: "POST" });
  },
  getUsers() {
    return request("/api/users");
  },
  getVersions() {
    return request("/api/timetable/versions");
  },
  compareVersions(a, b) {
    return request(`/api/timetable/compare?a=${a}&b=${b}`);
  },
  getNotifications(user_id) {
    return request(`/api/notifications?user_id=${user_id}`);
  },
  markNotificationRead(notification_id) {
    return request(`/api/notifications/${notification_id}/read`, { method: "PUT" });
  },
  getAuditLog() {
    return request("/api/audit-log");
  },
  getChangeRequests() {
    return request("/api/change-requests");
  },
  addTeacher(name, department, max_daily_load = 4) {
    return request("/api/master-data/teachers", {
      method: "POST",
      body: JSON.stringify({ name, department, max_daily_load })
    });
  },
  updateTeacher(teacher_id, name, department, max_daily_load = 4) {
    return request(`/api/master-data/teachers/${teacher_id}`, {
      method: "PUT",
      body: JSON.stringify({ name, department, max_daily_load })
    });
  },
  deleteTeacher(teacher_id) {
    return request(`/api/master-data/teachers/${teacher_id}`, { method: "DELETE" });
  },
  addRoom(code, building, floor, capacity, room_type, features = "") {
    return request("/api/master-data/rooms", {
      method: "POST",
      body: JSON.stringify({ code, building, floor, capacity, room_type, features })
    });
  },
  updateRoom(room_id, code, building, floor, capacity, room_type, features = "") {
    return request(`/api/master-data/rooms/${room_id}`, {
      method: "PUT",
      body: JSON.stringify({ code, building, floor, capacity, room_type, features })
    });
  },
  deleteRoom(room_id) {
    return request(`/api/master-data/rooms/${room_id}`, { method: "DELETE" });
  },
  addSection(name, department, size) {
    return request("/api/master-data/sections", {
      method: "POST",
      body: JSON.stringify({ name, department, size })
    });
  },
  updateSection(section_id, name, department, size) {
    return request(`/api/master-data/sections/${section_id}`, {
      method: "PUT",
      body: JSON.stringify({ name, department, size })
    });
  },
  deleteSection(section_id) {
    return request(`/api/master-data/sections/${section_id}`, { method: "DELETE" });
  },
  addCourse(code, title, teacher_id, section_id, weekly_sessions, required_room_type) {
    return request("/api/master-data/courses", {
      method: "POST",
      body: JSON.stringify({ code, title, teacher_id, section_id, weekly_sessions, required_room_type })
    });
  },
  updateCourse(course_id, code, title, teacher_id, section_id, weekly_sessions, required_room_type) {
    return request(`/api/master-data/courses/${course_id}`, {
      method: "PUT",
      body: JSON.stringify({ code, title, teacher_id, section_id, weekly_sessions, required_room_type })
    });
  },
  deleteCourse(course_id) {
    return request(`/api/master-data/courses/${course_id}`, { method: "DELETE" });
  },
  addHoliday(name, day) {
    return request("/api/master-data/holidays", {
      method: "POST",
      body: JSON.stringify({ name, day })
    });
  },
  deleteHoliday(holiday_id) {
    return request(`/api/master-data/holidays/${holiday_id}`, { method: "DELETE" });
  },
  addTimeslot(day, start_time, end_time, sort_order, is_morning = 0, is_last_slot = 0) {
    return request("/api/master-data/timeslots", {
      method: "POST",
      body: JSON.stringify({ day, start_time, end_time, sort_order, is_morning, is_last_slot })
    });
  },
  deleteTimeslot(timeslot_id) {
    return request(`/api/master-data/timeslots/${timeslot_id}`, { method: "DELETE" });
  },
  updatePreference(preference_id, enabled, weight) {
    return request(`/api/master-data/preferences/${preference_id}`, {
      method: "PUT",
      body: JSON.stringify({ enabled, weight })
    });
  },
  getTeacherAvailability(teacher_id) {
    return request(`/api/teacher-availability?teacher_id=${teacher_id}`);
  },
  setTeacherAvailability(teacher_id, unavailable_slot_ids) {
    return request(`/api/teacher-availability/${teacher_id}`, {
      method: "PUT",
      body: JSON.stringify({ unavailable_slot_ids })
    });
  },
  submitChangeRequest(requester_id, target_type, target_id, reason, urgency = "normal", preferred_alternative = "") {
    return request("/api/change-requests", {
      method: "POST",
      body: JSON.stringify({ requester_id, target_type, target_id, reason, urgency, preferred_alternative })
    });
  },
  updateChangeRequestStatus(request_id, status, admin_response = "") {
    return request(`/api/change-requests/${request_id}/status`, {
      method: "PUT",
      body: JSON.stringify({ status, admin_response })
    });
  },
  addCoordinatorNote(request_id, note) {
    return request(`/api/change-requests/${request_id}/note`, {
      method: "PUT",
      body: JSON.stringify({ note })
    });
  },
  lockEntry(entry_id) {
    return request(`/api/timetable/entry/${entry_id}/lock`, { method: "PUT" });
  },
  unlockEntry(entry_id) {
    return request(`/api/timetable/entry/${entry_id}/unlock`, { method: "PUT" });
  },
  publishTimetable(version_id) {
    return request(`/api/timetable/${version_id}/publish`, { method: "PUT" });
  }
};
