import { state } from "./state.js";

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

export function renderAll() {
  renderStats();
  renderStatus();
  renderFilter();
  renderTimetable();
  renderMasterData();
  renderReports();
}

function renderStats() {
  const data = state.masterData;
  const latest = state.latestTimetable;
  const stats = [
    ["Teachers", data.teachers.length],
    ["Rooms", data.rooms.length],
    ["Sections", data.sections.length],
    ["Courses", data.courses.length],
    ["Score", latest ? latest.score : "-"]
  ];
  byId("statsGrid").innerHTML = stats
    .map(([label, value]) => `<div class="stat-card"><span>${label}</span><strong>${value}</strong></div>`)
    .join("");
}

function renderStatus() {
  const latest = state.latestTimetable;
  if (!latest) {
    byId("statusPanel").innerHTML = `<div class="status-line warning"><span>No generated timetable yet.</span><span class="pill">Draft needed</span></div>`;
    return;
  }
  const lines = [
    [`Version ${latest.id}: ${escapeHtml(latest.name)}`, latest.status],
    [`Soft penalty: ${latest.soft_penalty}`, "quality"],
    [`Unplaced sessions: ${latest.unplaced_count}`, latest.unplaced_count ? "warning" : "clear"],
    [`Distance to feasibility: ${latest.distance_to_feasibility}`, "metric"]
  ];
  byId("statusPanel").innerHTML = lines
    .map(([text, tag]) => `<div class="status-line ${tag === "warning" ? "warning" : ""}"><span>${text}</span><span class="pill">${tag}</span></div>`)
    .join("");
}

function renderFilter() {
  const filter = byId("viewFilter");
  const current = filter.value || state.selectedSection;
  filter.innerHTML = [
    `<option value="all">All sections</option>`,
    ...state.masterData.sections.map(
      (section) => `<option value="${section.name}">${escapeHtml(section.name)}</option>`
    )
  ].join("");
  filter.value = current;
}

function renderTimetable() {
  const grid = byId("timetableGrid");
  const latest = state.latestTimetable;
  const timeslots = state.masterData.timeslots.filter((slot, index, all) => {
    return all.findIndex((item) => item.start_time === slot.start_time && item.end_time === slot.end_time) === index;
  });
  const entries = (latest?.entries || []).filter((entry) => {
    if (entry.status !== "placed") {
      return false;
    }
    return state.selectedSection === "all" || entry.section_name === state.selectedSection;
  });

  const lookup = new Map();
  for (const entry of entries) {
    const key = `${entry.day}|${entry.start_time}|${entry.end_time}`;
    if (!lookup.has(key)) {
      lookup.set(key, []);
    }
    lookup.get(key).push(entry);
  }

  const header = `<tr><th class="slot-label">Time</th>${days.map((day) => `<th>${day}</th>`).join("")}</tr>`;
  const rows = timeslots
    .map((slot) => {
      const cells = days
        .map((day) => {
          const key = `${day}|${slot.start_time}|${slot.end_time}`;
          const chips = (lookup.get(key) || []).map(classChip).join("");
          return `<td>${chips}</td>`;
        })
        .join("");
      return `<tr><th class="slot-label">${slot.start_time}<br>${slot.end_time}</th>${cells}</tr>`;
    })
    .join("");
  grid.innerHTML = header + rows;
  renderUnplaced();
}

function classChip(entry) {
  return `
    <div class="class-chip">
      <strong>${escapeHtml(entry.course_code)} - ${escapeHtml(entry.section_name)}</strong>
      <span>${escapeHtml(entry.course_title)}</span>
      <span>${escapeHtml(entry.teacher_name)}</span>
      <span>${escapeHtml(entry.room_code)} - ${escapeHtml(entry.room_building)}</span>
    </div>
  `;
}

function renderUnplaced() {
  const latest = state.latestTimetable;
  const unplaced = (latest?.entries || []).filter((entry) => entry.status === "unplaced");
  byId("unplacedList").innerHTML = unplaced
    .map(
      (entry) =>
        `<div class="notice">${escapeHtml(entry.course_code)} for ${escapeHtml(entry.section_name)} could not be placed.</div>`
    )
    .join("");
}

function renderMasterData() {
  byId("coursesList").innerHTML = state.masterData.courses.map((course) => `
    <div class="record">
      <strong>${escapeHtml(course.code)} - ${escapeHtml(course.title)}</strong>
      <span>${escapeHtml(course.section_name)} - ${escapeHtml(course.teacher_name)} - ${course.weekly_sessions} sessions</span>
    </div>
  `).join("");

  byId("roomsList").innerHTML = state.masterData.rooms.map((room) => `
    <div class="record">
      <strong>${escapeHtml(room.code)} - ${escapeHtml(room.building)}</strong>
      <span>${room.capacity} seats - ${escapeHtml(room.room_type)} - floor ${room.floor}</span>
    </div>
  `).join("");

  byId("preferencesList").innerHTML = state.masterData.preferences.map((pref) => `
    <div class="record">
      <strong>${escapeHtml(pref.label)}</strong>
      <span>${pref.enabled ? "Enabled" : "Disabled"} - weight ${pref.weight}</span>
    </div>
  `).join("");
}

function renderReports() {
  byId("roomReport").innerHTML = state.reports.room_utilization.map((room) => `
    <div class="report-row">
      <span>${escapeHtml(room.code)} - ${escapeHtml(room.building)} - ${room.capacity} seats</span>
      <span>${room.used_slots}</span>
    </div>
  `).join("");

  byId("teacherReport").innerHTML = state.reports.teacher_load.map((teacher) => `
    <div class="report-row">
      <span>${escapeHtml(teacher.name)} - ${escapeHtml(teacher.department)}</span>
      <span>${teacher.assigned_sessions}</span>
    </div>
  `).join("");
}
