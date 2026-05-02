import { state, setBootstrap, setChangeRequests } from "./state.js";
import { api } from "./api.js";

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

export function renderLoginScreen() {
  const select = byId("userSelect");
  select.innerHTML = state.masterData.users
    .map(u => `<option value="${u.id}">${u.name} (${u.role})</option>`)
    .join("");
}

export function renderNav() {
  const role = state.currentUser?.role;
  const navLinks = document.querySelectorAll(".nav-link");
  const sectionsVisibility = {
    dashboard: ["administrator", "coordinator", "teacher", "student", "facility_manager"],
    timetable: ["administrator", "coordinator", "teacher", "student"],
    "master-data": ["administrator"],
    reports: ["administrator", "coordinator", "facility_manager"]
  };

  navLinks.forEach(link => {
    const href = link.getAttribute("href");
    const section = href.substring(1);
    const visible = sectionsVisibility[section]?.includes(role);
    link.style.display = visible ? "" : "none";
  });

  const actionButtons = document.querySelector(".actions");
  if (actionButtons) {
    const generateBtn = byId("generateBtn");
    const publishBtn = document.getElementById("publishBtn");
    if (generateBtn) generateBtn.style.display = role === "administrator" ? "" : "none";
    if (publishBtn) publishBtn.style.display = role === "administrator" ? "" : "none";
  }
}

export function renderAll() {
  renderStats();
  renderStatus();
  renderFilter();
  renderTimetable();
  renderRoleSpecificSections();
  renderReports();
}

function renderRoleSpecificSections() {
  const role = state.currentUser?.role;
  const masterDataSection = byId("master-data");
  const changeRequestsSection = byId("change-requests");

  if (masterDataSection) {
    masterDataSection.style.display = role === "administrator" ? "" : "none";
  }
  if (changeRequestsSection) {
    changeRequestsSection.style.display = ["administrator", "coordinator", "teacher"].includes(role) ? "" : "none";
    if (["administrator", "coordinator", "teacher"].includes(role)) {
      renderChangeRequests();
    }
  }

  if (role === "teacher") {
    renderTeacherView();
  } else if (role === "student") {
    renderStudentView();
  } else if (role === "facility_manager") {
    renderFacilityManagerView();
  } else {
    renderMasterData();
  }
}

function renderTeacherView() {
  byId("timetable").innerHTML = `
    <div class="section-heading">
      <div>
        <p class="eyebrow">Personal Schedule</p>
        <h2>My Timetable</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table class="timetable-grid" id="teacherTimetableGrid"></table>
    </div>
  `;
  renderTeacherTimetable();
}

function renderStudentView() {
  byId("timetable").innerHTML = `
    <div class="section-heading">
      <div>
        <p class="eyebrow">Class Schedule</p>
        <h2>Section Timetable</h2>
      </div>
    </div>
    <div class="table-wrap">
      <table class="timetable-grid" id="studentTimetableGrid"></table>
    </div>
  `;
  renderStudentTimetable();
}

function renderFacilityManagerView() {
  byId("reports").innerHTML = `
    <div class="section-heading">
      <div>
        <p class="eyebrow">Resource Management</p>
        <h2>Room & Facility Reports</h2>
      </div>
    </div>
    <div class="reports-grid">
      <section>
        <h3>Room Utilization & Capacity</h3>
        <div id="facilityRoomReport" class="report-table"></div>
      </section>
    </div>
  `;
  renderFacilityRoomReport();
}

function renderTeacherTimetable() {
  const grid = byId("teacherTimetableGrid");
  const latest = state.latestTimetable;
  const teacherId = state.currentUser?.teacher_id;
  const timeslots = state.masterData.timeslots.filter((slot, index, all) => {
    return all.findIndex((item) => item.start_time === slot.start_time && item.end_time === slot.end_time) === index;
  });
  const entries = (latest?.entries || []).filter((entry) => {
    return entry.status === "placed" && entry.teacher_id === teacherId;
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
}

function renderStudentTimetable() {
  const grid = byId("studentTimetableGrid");
  const latest = state.latestTimetable;
  const sectionId = state.currentUser?.section_id;
  const timeslots = state.masterData.timeslots.filter((slot, index, all) => {
    return all.findIndex((item) => item.start_time === slot.start_time && item.end_time === slot.end_time) === index;
  });
  const entries = (latest?.entries || []).filter((entry) => {
    return entry.status === "placed" && entry.section_id === sectionId;
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
}

function renderFacilityRoomReport() {
  const roomReport = byId("facilityRoomReport");
  const rooms = state.masterData.rooms;
  const utilization = state.reports.room_utilization;

  roomReport.innerHTML = utilization.map((room) => {
    const fullRoom = rooms.find(r => r.code === room.code);
    const utilizationPercent = fullRoom ? Math.round((room.used_slots / (fullRoom.capacity * 5)) * 100) : 0;
    return `
      <div class="report-row">
        <div>
          <strong>${escapeHtml(room.code)} - ${escapeHtml(room.building)}</strong>
          <span>${room.capacity} capacity, ${room.used_slots} used slots</span>
        </div>
        <div style="min-width: 100px;">
          <span style="font-weight: bold;">${utilizationPercent}%</span>
        </div>
      </div>
    `;
  }).join("");
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
  const role = state.currentUser?.role;
  if (["teacher", "student"].includes(role)) {
    return;
  }

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

  setTimeout(() => {
    if (state.currentUser?.role === "administrator") {
      document.querySelectorAll(".lock-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          const entryId = parseInt(e.target.dataset.entryId);
          const isLocked = e.target.dataset.locked === "1";
          try {
            if (isLocked) {
              await api.unlockEntry(entryId);
            } else {
              await api.lockEntry(entryId);
            }
            const payload = await api.bootstrap();
            setBootstrap(payload);
            renderAll();
          } catch (err) {
            console.error("Error toggling lock:", err);
          }
        });
      });
    }
  }, 0);

  renderUnplaced();
}

function classChip(entry) {
  const role = state.currentUser?.role;
  const lockBtn = role === "administrator"
    ? `<button class="lock-btn" data-entry-id="${entry.id}" data-locked="${entry.locked}">${entry.locked ? "Unlock" : "Lock"}</button>`
    : "";

  return `
    <div class="class-chip" data-entry-id="${entry.id}">
      <strong>${escapeHtml(entry.course_code)} - ${escapeHtml(entry.section_name)}</strong>
      <span>${escapeHtml(entry.course_title)}</span>
      <span>${escapeHtml(entry.teacher_name)}</span>
      <span>${escapeHtml(entry.room_code)} - ${escapeHtml(entry.room_building)}</span>
      ${entry.locked ? '<span class="locked-badge">🔒 Locked</span>' : ""}
      ${lockBtn}
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
  const role = state.currentUser?.role;
  if (!["administrator", "coordinator", "facility_manager"].includes(role)) {
    byId("reports").style.display = "none";
    return;
  }

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

function renderChangeRequests() {
  const changeReqSection = byId("change-requests");
  if (!changeReqSection) return;

  const role = state.currentUser?.role;
  let html = `
    <div class="section-heading">
      <div>
        <p class="eyebrow">Workflow</p>
        <h2>Change Requests</h2>
      </div>
    </div>
  `;

  if (["teacher", "coordinator"].includes(role)) {
    html += `
      <div class="form-section">
        <h3>Submit New Request</h3>
        <form id="changeRequestForm" class="inline-form">
          <input type="text" id="changeReason" placeholder="Reason for change" required />
          <select id="changeTargetType">
            <option value="teacher">Teacher</option>
            <option value="room">Room</option>
            <option value="timing">Timing</option>
          </select>
          <button type="submit" class="button primary">Submit Request</button>
        </form>
      </div>
    `;
  }

  html += `
    <div class="requests-list" id="requestsList">
      ${state.changeRequests.map(req => `
        <div class="request-card">
          <strong>${escapeHtml(req.requester_name)} (${escapeHtml(req.requester_role)})</strong>
          <span>${escapeHtml(req.reason)}</span>
          <span class="pill ${req.status}">${req.status}</span>
          ${role === "administrator" ? `
            <div class="request-actions">
              <button data-request-id="${req.id}" data-status="approved" class="button small approve-btn">Approve</button>
              <button data-request-id="${req.id}" data-status="rejected" class="button small reject-btn">Reject</button>
            </div>
          ` : ""}
        </div>
      `).join("")}
    </div>
  `;

  changeReqSection.innerHTML = html;

  if (["teacher", "coordinator"].includes(role)) {
    byId("changeRequestForm")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api.submitChangeRequest(state.currentUser.id, byId("changeTargetType").value, 0, byId("changeReason").value);
        byId("changeReason").value = "";
        const resp = await api.getChangeRequests();
        state.changeRequests = resp.changeRequests || [];
        renderChangeRequests();
      } catch (err) {
        console.error("Error submitting request:", err);
      }
    });
  }

  if (role === "administrator") {
    document.querySelectorAll(".approve-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const reqId = parseInt(e.target.dataset.requestId);
        try {
          await api.updateChangeRequestStatus(reqId, "approved");
          const resp = await api.getChangeRequests();
          state.changeRequests = resp.changeRequests || [];
          renderChangeRequests();
        } catch (err) {
          console.error("Error updating request:", err);
        }
      });
    });

    document.querySelectorAll(".reject-btn").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const reqId = parseInt(e.target.dataset.requestId);
        try {
          await api.updateChangeRequestStatus(reqId, "rejected");
          const resp = await api.getChangeRequests();
          state.changeRequests = resp.changeRequests || [];
          renderChangeRequests();
        } catch (err) {
          console.error("Error updating request:", err);
        }
      });
    });
  }
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
