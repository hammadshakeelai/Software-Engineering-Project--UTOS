const jsonHeaders = {
  "Content-Type": "application/json"
};

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: jsonHeaders,
    ...options
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
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
  getUsers() {
    return request("/api/users");
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
  submitChangeRequest(requester_id, target_type, target_id, reason) {
    return request("/api/change-requests", {
      method: "POST",
      body: JSON.stringify({ requester_id, target_type, target_id, reason })
    });
  },
  updateChangeRequestStatus(request_id, status) {
    return request(`/api/change-requests/${request_id}/status`, {
      method: "PUT",
      body: JSON.stringify({ status })
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
