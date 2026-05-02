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

function getRoleLabel(role) {
  const map = {
    administrator: "Timetable Manager",
    coordinator: "Department Coordinator",
    teacher: "Teacher",
    student: "Student",
    facility_manager: "Facility Manager"
  };
  return map[role] || role;
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// LOGIN
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export function renderLoginScreen() {
  const selector = document.getElementById('userSelector');
  const loginBtn  = document.getElementById('loginBtn');
  if (!selector || !loginBtn) return;

  // Pre-select remembered role
  const rememberedId = localStorage.getItem('remembered_role_id');
  if (rememberedId) {
    const remembered = selector.querySelector(`[data-user-id="${rememberedId}"]`);
    if (remembered) {
      remembered.classList.add('selected');
      loginBtn.disabled = false;
    }
  }

  // Single delegated click â€” remove old one first to prevent stacking
  const existing = selector._loginDelegate;
  if (existing) selector.removeEventListener('click', existing);

  const delegate = function(e) {
    const card = e.target.closest('.role-card');
    if (!card) return;
    selector.querySelectorAll('.role-card').forEach(o => o.classList.remove('selected'));
    card.classList.add('selected');
    localStorage.setItem('remembered_role_id', card.getAttribute('data-user-id'));
    loginBtn.disabled = false;
  };

  selector.addEventListener('click', delegate);
  selector._loginDelegate = delegate;
}

export function updateRoleBadge(user) {
  const badge = document.getElementById("roleBadge");
  const name = document.getElementById("loginRoleName");
  if (!badge || !name) return;
  name.textContent = getRoleLabel(user.role);
  badge.setAttribute("data-role", user.role);
  badge.hidden = false;
}

export function selectUserByIndex(idx) {
  const options = document.querySelectorAll(".role-card");
  options.forEach(opt => opt.classList.remove("selected"));
  if (idx >= 0 && idx < options.length) {
    options[idx].classList.add("selected");
  }
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// MAIN RENDER ORCHESTRATOR
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export function renderAll() {
  renderNav();
  renderStats();
  renderStatus();
  renderFilter();
  renderTimetable();
  renderRoleSpecificSections();
  renderReports();
  renderChangeRequests();
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// NAV â€” role-based visibility
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

export function renderNav() {
  const role = state.currentUser?.role;
  const rules = {
    "#dashboard":       ["administrator", "coordinator", "teacher", "student", "facility_manager"],
    "#timetable":       ["administrator", "coordinator", "teacher", "student"],
    "#change-requests": ["administrator", "coordinator", "teacher"],
    "#master-data":     ["administrator"],
    "#reports":         ["administrator", "coordinator", "facility_manager"],
  };

  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    const allowed = rules[href];
    link.style.display = (!allowed || allowed.includes(role)) ? "" : "none";
  });
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// ROLE-SPECIFIC SECTIONS
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

function renderRoleSpecificSections() {
  const role = state.currentUser?.role;

  const sectVisibility = {
    "master-data":     role === "administrator",
    "change-requests": ["administrator", "coordinator", "teacher"].includes(role),
    "reports":         ["administrator", "coordinator", "facility_manager"].includes(role),
  };
  for (const [id, show] of Object.entries(sectVisibility)) {
    const el = byId(id);
    if (el) el.style.display = show ? "" : "none";
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

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// ROLE-SPECIFIC VIEWS
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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
    if (!lookup.has(key)) lookup.set(key, []);
    lookup.get(key).push(entry);
  }

  const header = `<tr><th class="slot-label">Time</th>${days.map((day) => `<th>${day}</th>`).join("")}</tr>`;
  const rows = timeslots.map((slot) => {
    const cells = days.map((day) => {
      const key = `${day}|${slot.start_time}|${slot.end_time}`;
      const chips = (lookup.get(key) || []).map(classChip).join("");
      return `<td>${chips}</td>`;
    }).join("");
    return `<tr><th class="slot-label">${slot.start_time}<br>${slot.end_time}</th>${cells}</tr>`;
  }).join("");
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
    if (!lookup.has(key)) lookup.set(key, []);
    lookup.get(key).push(entry);
  }

  const header = `<tr><th class="slot-label">Time</th>${days.map((day) => `<th>${day}</th>`).join("")}</tr>`;
  const rows = timeslots.map((slot) => {
    const cells = days.map((day) => {
      const key = `${day}|${slot.start_time}|${slot.end_time}`;
      const chips = (lookup.get(key) || []).map(classChip).join("");
      return `<td>${chips}</td>`;
    }).join("");
    return `<tr><th class="slot-label">${slot.start_time}<br>${slot.end_time}</th>${cells}</tr>`;
  }).join("");
  grid.innerHTML = header + rows;
}

function renderFacilityRoomReport() {
  const roomReport = byId("facilityRoomReport");
  const rooms = state.masterData.rooms;
  const utilization = state.reports.room_utilization;

  roomReport.innerHTML = utilization.map((room) => {
    const fullRoom = rooms.find(r => r.code === room.code);
    const pct = fullRoom ? Math.round((room.used_slots / (fullRoom.capacity * 5)) * 100) : 0;
    return `
      <div class="report-row">
        <div>
          <strong>${escapeHtml(room.code)} - ${escapeHtml(room.building)}</strong>
          <span>${room.capacity} capacity, ${room.used_slots} used slots</span>
        </div>
        <div style="min-width: 100px;">
          <span style="font-weight: bold;">${pct}%</span>
        </div>
      </div>
    `;
  }).join("");
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// DASHBOARD â€” stats + status
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// TIMETABLE â€” admin/coordinator full grid
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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
  if (["teacher", "student"].includes(role)) return;

  const grid = byId("timetableGrid");
  const latest = state.latestTimetable;
  const timeslots = state.masterData.timeslots.filter((slot, index, all) => {
    return all.findIndex((item) => item.start_time === slot.start_time && item.end_time === slot.end_time) === index;
  });
  const entries = (latest?.entries || []).filter((entry) => {
    if (entry.status !== "placed") return false;
    return state.selectedSection === "all" || entry.section_name === state.selectedSection;
  });

  const lookup = new Map();
  for (const entry of entries) {
    const key = `${entry.day}|${entry.start_time}|${entry.end_time}`;
    if (!lookup.has(key)) lookup.set(key, []);
    lookup.get(key).push(entry);
  }

  const header = `<tr><th class="slot-label">Time</th>${days.map((day) => `<th>${day}</th>`).join("")}</tr>`;
  const rows = timeslots.map((slot) => {
    const cells = days.map((day) => {
      const key = `${day}|${slot.start_time}|${slot.end_time}`;
      const chips = (lookup.get(key) || []).map(classChip).join("");
      return `<td>${chips}</td>`;
    }).join("");
    return `<tr><th class="slot-label">${slot.start_time}<br>${slot.end_time}</th>${cells}</tr>`;
  }).join("");
  grid.innerHTML = header + rows;

  // Lock buttons for admin
  setTimeout(() => {
    if (state.currentUser?.role === "administrator") {
      document.querySelectorAll(".lock-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          const entryId = parseInt(e.target.dataset.entryId);
          const isLocked = e.target.dataset.locked === "1";
          try {
            if (isLocked) { await api.unlockEntry(entryId); }
            else { await api.lockEntry(entryId); }
            const payload = await api.bootstrap();
            setBootstrap(payload);
            renderAll();
          } catch (err) { console.error("Error toggling lock:", err); }
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
      ${entry.locked ? '<span class="locked-badge">ðŸ”’ Locked</span>' : ""}
      ${lockBtn}
    </div>
  `;
}

function renderUnplaced() {
  const latest = state.latestTimetable;
  const unplaced = (latest?.entries || []).filter((entry) => entry.status === "unplaced");
  byId("unplacedList").innerHTML = unplaced
    .map((entry) => `<div class="notice">${escapeHtml(entry.course_code)} for ${escapeHtml(entry.section_name)} could not be placed.</div>`)
    .join("");
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// MASTER DATA â€” admin only
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

function renderMasterData() {
  const role = state.currentUser?.role;
  if (role !== "administrator") return;

  // â”€â”€ Teachers â”€â”€
  byId("coursesList").innerHTML = `
    <div class="add-form" id="addTeacherForm">
      <input class="input" id="tName" placeholder="Name" />
      <input class="input" id="tDept" placeholder="Department" />
      <button class="button primary small" id="addTeacherBtn">+ Add</button>
    </div>
  ` + state.masterData.teachers.map(t => `
    <div class="record">
      <div><strong>${escapeHtml(t.name)}</strong><span>${escapeHtml(t.department)} Â· max ${t.max_daily_load}/day</span></div>
      <button class="button small danger del-teacher" data-id="${t.id}">ðŸ—‘</button>
    </div>
  `).join("");

  byId("addTeacherBtn")?.addEventListener("click", async () => {
    const name = byId("tName").value.trim();
    const dept = byId("tDept").value.trim();
    if (!name || !dept) return;
    await api.addTeacher(name, dept);
    await reloadAndRender();
  });
  document.querySelectorAll(".del-teacher").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this teacher?")) return;
      await api.deleteTeacher(parseInt(btn.dataset.id));
      await reloadAndRender();
    });
  });

  // â”€â”€ Rooms â”€â”€
  byId("roomsList").innerHTML = `
    <div class="add-form" id="addRoomForm">
      <input class="input" id="rCode" placeholder="Code (e.g. R101)" />
      <input class="input" id="rBldg" placeholder="Building" />
      <input class="input" id="rCap" placeholder="Capacity" type="number" />
      <button class="button primary small" id="addRoomBtn">+ Add</button>
    </div>
  ` + state.masterData.rooms.map(r => `
    <div class="record">
      <div><strong>${escapeHtml(r.code)} Â· ${escapeHtml(r.building)}</strong><span>${r.capacity} seats Â· ${escapeHtml(r.room_type)} Â· floor ${r.floor}</span></div>
      <button class="button small danger del-room" data-id="${r.id}">ðŸ—‘</button>
    </div>
  `).join("");

  byId("addRoomBtn")?.addEventListener("click", async () => {
    const code = byId("rCode").value.trim();
    const bldg = byId("rBldg").value.trim();
    const cap = parseInt(byId("rCap").value) || 30;
    if (!code || !bldg) return;
    await api.addRoom(code, bldg, 0, cap, "lecture");
    await reloadAndRender();
  });
  document.querySelectorAll(".del-room").forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm("Delete this room?")) return;
      await api.deleteRoom(parseInt(btn.dataset.id));
      await reloadAndRender();
    });
  });

  // â”€â”€ Preferences â”€â”€
  byId("preferencesList").innerHTML = state.masterData.preferences.map(pref => `
    <div class="record">
      <strong>${escapeHtml(pref.label)}</strong>
      <span>${pref.enabled ? "Enabled" : "Disabled"} Â· weight ${pref.weight}</span>
    </div>
  `).join("");
}

async function reloadAndRender() {
  const { setBootstrap: sb } = await import("./state.js");
  const payload = await api.bootstrap();
  sb(payload);
  const { renderAll: ra } = await import("./render.js");
  ra();
}

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// REPORTS
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

function renderReports() {
  const role = state.currentUser?.role;
  if (!["administrator", "coordinator", "facility_manager"].includes(role)) {
    const el = byId("reports");
    if (el) el.style.display = "none";
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

// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
// CHANGE REQUESTS
// â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

function renderChangeRequests() {
  const section = byId("change-requests");
  if (!section || section.style.display === "none") return;

  const role = state.currentUser?.role;
  const formWrapper = byId("changeRequestFormWrapper");
  const listEl      = byId("requestsList");
  if (!formWrapper || !listEl) return;

  if (["teacher", "coordinator"].includes(role)) {
    formWrapper.innerHTML = `
      <div class="form-section">
        <h3>Submit a Change Request</h3>
        <div class="guide-tip small">Select what needs changing, describe the reason, and set urgency.</div>
        <form id="changeRequestForm" class="cr-form">
          <div class="cr-form-row">
            <label>Type</label>
            <select id="changeTargetType" class="select">
              <option value="teacher">Teacher availability</option>
              <option value="room">Room assignment</option>
              <option value="timing">Class timing</option>
            </select>
          </div>
          <div class="cr-form-row">
            <label>Urgency</label>
            <div class="radio-group">
              <label><input type="radio" name="urgency" value="normal" checked /> Normal</label>
              <label><input type="radio" name="urgency" value="urgent" /> Urgent</label>
            </div>
          </div>
          <div class="cr-form-row">
            <label>Reason</label>
            <input type="text" id="changeReason" class="input" placeholder="Why is this change needed?" required />
          </div>
          <div class="cr-form-row">
            <label>Preferred alternative</label>
            <input type="text" id="changePrefAlt" class="input" placeholder="e.g. Move to Monday 10am (optional)" />
          </div>
          <button type="submit" class="button primary">Submit Request</button>
        </form>
      </div>
    `;
    byId("changeRequestForm")?.addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = e.target.querySelector("button[type=submit]");
      btn.disabled = true; btn.textContent = "Submitting...";
      try {
        const urgency = e.target.querySelector('input[name="urgency"]:checked')?.value || "normal";
        await api.submitChangeRequest(
          state.currentUser.id, byId("changeTargetType").value, 0,
          byId("changeReason").value, urgency, byId("changePrefAlt").value
        );
        byId("changeReason").value = "";
        byId("changePrefAlt").value = "";
        const resp = await api.getChangeRequests();
        state.changeRequests = resp.changeRequests || [];
        renderChangeRequestList(role);
      } catch (err) { console.error(err); }
      finally { btn.disabled = false; btn.textContent = "Submit Request"; }
    });
  } else {
    formWrapper.innerHTML = "";
  }

  renderChangeRequestList(role);
}

function renderChangeRequestList(role) {
  const listEl = byId("requestsList");
  if (!listEl) return;
  const requests = state.changeRequests;
  if (!requests.length) { listEl.innerHTML = '<p class="empty-state">No change requests yet.</p>'; return; }

  listEl.innerHTML = requests.map(req => {
    const urgentBadge = req.urgency === "urgent" ? '<span class="pill-urgent">Urgent</span>' : "";
    const prefLine = req.preferred_alternative ? '<p class="req-pref">Preferred: ' + escapeHtml(req.preferred_alternative) + '</p>' : "";
    const coordLine = req.coordinator_note ? '<p class="req-coord-note">Coordinator note: ' + escapeHtml(req.coordinator_note) + '</p>' : "";
    const adminLine = req.admin_response ? '<p class="req-admin-resp">Admin response: ' + escapeHtml(req.admin_response) + '</p>' : "";

    let actions = "";
    if (role === "coordinator" && !req.coordinator_note) {
      actions = '<div class="coord-note-inline"><input class="input coord-note-input" placeholder="Add recommendation..." /><button class="button small coord-note-btn" data-rid="' + req.id + '">Vouch</button></div>';
    }
    if (role === "administrator" && req.status === "pending") {
      actions = '<div class="admin-action-inline"><input class="input admin-resp-input" placeholder="Response note (optional)" /><button data-request-id="' + req.id + '" class="button small approve-btn">Approve</button><button data-request-id="' + req.id + '" class="button small danger reject-btn">Reject</button></div>';
    }

    return '<div class="request-card" data-status="' + req.status + '">' +
      '<div class="request-card__meta"><strong>' + escapeHtml(req.requester_name || "Unknown") + '</strong>' +
      '<span class="pill-role">' + escapeHtml(req.requester_role || "") + '</span>' +
      '<span class="req-target">to ' + escapeHtml(req.target_type || "") + '</span>' + urgentBadge + '</div>' +
      '<p class="request-card__reason">' + escapeHtml(req.reason) + '</p>' +
      prefLine + coordLine + adminLine +
      '<div class="request-card__footer"><span class="status-badge status-' + req.status + '">' + req.status + '</span>' +
      (req.created_at ? '<span class="req-date">' + new Date(req.created_at).toLocaleDateString() + '</span>' : "") +
      actions + '</div></div>';
  }).join("");

  if (role === "coordinator") {
    listEl.querySelectorAll(".coord-note-btn").forEach(function(btn) {
      btn.addEventListener("click", async function() {
        var input = btn.parentElement.querySelector(".coord-note-input");
        if (!input.value.trim()) return;
        btn.disabled = true;
        await api.addCoordinatorNote(parseInt(btn.dataset.rid), input.value.trim());
        var resp = await api.getChangeRequests();
        state.changeRequests = resp.changeRequests || [];
        renderChangeRequestList(role);
      });
    });
  }
  if (role === "administrator") {
    listEl.querySelectorAll(".approve-btn").forEach(function(btn) {
      btn.addEventListener("click", async function() {
        var respInput = btn.parentElement.querySelector(".admin-resp-input");
        btn.disabled = true;
        await api.updateChangeRequestStatus(parseInt(btn.dataset.requestId), "approved", respInput ? respInput.value : "");
        var resp = await api.getChangeRequests();
        state.changeRequests = resp.changeRequests || [];
        renderChangeRequestList(role);
      });
    });
    listEl.querySelectorAll(".reject-btn").forEach(function(btn) {
      btn.addEventListener("click", async function() {
        var respInput = btn.parentElement.querySelector(".admin-resp-input");
        btn.disabled = true;
        await api.updateChangeRequestStatus(parseInt(btn.dataset.requestId), "rejected", respInput ? respInput.value : "");
        var resp = await api.getChangeRequests();
        state.changeRequests = resp.changeRequests || [];
        renderChangeRequestList(role);
      });
    });
  }
}

