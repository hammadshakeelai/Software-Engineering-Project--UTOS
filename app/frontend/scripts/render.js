import { state, setBootstrap, setNotifications, setVersions } from "./state.js";
import { api } from "./api.js";

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

// Teacher/student views replace the #timetable section's markup, so keep the
// original (filter + admin grid) to restore when a staff role logs back in.
const DEFAULT_TIMETABLE_HTML = document.getElementById("timetable")?.innerHTML ?? "";

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
    facility_manager: "Facility Manager",
    system_admin: "System Administrator"
  };
  return map[role] || role;
}

// ═════════════════════════════════════════════════════════════════════════════
// TOASTS
// ═════════════════════════════════════════════════════════════════════════════

export function toast(message, type = "info") {
  const container = byId("toastContainer");
  if (!container) return;
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = message;
  container.appendChild(el);
  setTimeout(() => el.classList.add("show"), 10);
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.remove(), 300);
  }, 4000);
}

async function guarded(action, successMessage) {
  try {
    await action();
    if (successMessage) toast(successMessage, "success");
  } catch (err) {
    console.error(err);
    toast(err.message || "Something went wrong", "error");
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// LOGIN
// ═════════════════════════════════════════════════════════════════════════════

const LOGIN_ROLES = ["administrator", "coordinator", "teacher", "student", "facility_manager"];

export function renderLoginScreen() {
  const selector = byId("userSelector");
  const loginBtn = byId("loginBtn");
  const accountRow = byId("accountPickRow");
  const accountList = byId("accountList");
  const accountSearch = byId("accountSearch");
  if (!selector || !loginBtn) return;

  // One card per role; picking a role lists every account with that role
  // (FR-09: each teacher/student signs in as themselves).
  const cards = [];
  for (const role of LOGIN_ROLES) {
    const count = state.masterData.users.filter(u => u.role === role).length;
    if (count) {
      cards.push(`
        <button type="button" class="role-card" data-role="${role}">
          <strong>${escapeHtml(getRoleLabel(role))}</strong>
          <span>${count === 1 ? "1 account" : `${count} accounts`}</span>
        </button>
      `);
    }
  }
  selector.innerHTML = cards.join("");

  let roleUsers = [];

  function drawAccountList(query) {
    const q = query.trim().toLowerCase();
    const filtered = q ? roleUsers.filter(u => u.name.toLowerCase().includes(q)) : roleUsers;
    accountList.innerHTML = filtered.length
      ? filtered.map(u => `
          <button type="button" class="account-option ${String(u.id) === accountList.dataset.selectedId ? "selected" : ""}" data-user-id="${u.id}">
            <strong>${escapeHtml(u.name)}</strong>
            <span>${escapeHtml(u.email || "")}</span>
          </button>
        `).join("")
      : '<p class="empty-state">No account matches that name.</p>';
  }

  function pickAccount(userId) {
    accountList.dataset.selectedId = String(userId ?? "");
    accountList.querySelectorAll(".account-option").forEach(option => {
      option.classList.toggle("selected", option.dataset.userId === accountList.dataset.selectedId);
    });
    loginBtn.disabled = !accountList.dataset.selectedId;
  }

  function selectRole(role, card) {
    selector.querySelectorAll(".role-card").forEach(o => o.classList.remove("selected"));
    card.classList.add("selected");
    localStorage.setItem("remembered_role", role);
    roleUsers = state.masterData.users.filter(u => u.role === role);
    accountSearch.value = "";
    accountRow.hidden = roleUsers.length <= 1;
    accountList.dataset.selectedId = "";
    drawAccountList("");
    pickAccount(roleUsers[0]?.id);
  }

  const rememberedRole = localStorage.getItem("remembered_role");
  if (rememberedRole) {
    const remembered = selector.querySelector(`[data-role="${rememberedRole}"]`);
    if (remembered) selectRole(rememberedRole, remembered);
  }

  const existing = selector._loginDelegate;
  if (existing) selector.removeEventListener("click", existing);
  const delegate = function (e) {
    const card = e.target.closest(".role-card");
    if (!card) return;
    selectRole(card.getAttribute("data-role"), card);
  };
  selector.addEventListener("click", delegate);
  selector._loginDelegate = delegate;

  const existingAccount = accountList._accountDelegate;
  if (existingAccount) accountList.removeEventListener("click", existingAccount);
  const accountDelegate = function (e) {
    const option = e.target.closest(".account-option");
    if (option) pickAccount(parseInt(option.dataset.userId));
  };
  accountList.addEventListener("click", accountDelegate);
  accountList._accountDelegate = accountDelegate;

  const existingSearch = accountSearch._searchDelegate;
  if (existingSearch) accountSearch.removeEventListener("input", existingSearch);
  const searchDelegate = function () {
    drawAccountList(accountSearch.value);
  };
  accountSearch.addEventListener("input", searchDelegate);
  accountSearch._searchDelegate = searchDelegate;
}

export function updateRoleBadge(user) {
  const badge = byId("roleBadge");
  const name = byId("loginRoleName");
  if (!badge || !name) return;
  name.textContent = getRoleLabel(user.role);
  badge.setAttribute("data-role", user.role);
  badge.hidden = false;
}

// ═════════════════════════════════════════════════════════════════════════════
// MAIN RENDER ORCHESTRATOR
// ═════════════════════════════════════════════════════════════════════════════

export function renderAll() {
  renderNav();
  renderStats();
  renderStatus();
  // Role sections first: they own the #timetable markup (restore or replace),
  // so the filter and grid render against the right DOM.
  renderRoleSpecificSections();
  renderFilter();
  renderTimetable();
  renderReports();
  renderChangeRequests();
  renderVersions();
  renderNotificationBadge();
}

// ═════════════════════════════════════════════════════════════════════════════
// NAV — role-based visibility
// ═════════════════════════════════════════════════════════════════════════════

export function renderNav() {
  const role = state.currentUser?.role;
  const rules = {
    "#dashboard":       ["administrator", "coordinator", "teacher", "student", "facility_manager"],
    "#timetable":       ["administrator", "coordinator", "teacher", "student"],
    "#change-requests": ["administrator", "coordinator", "teacher"],
    "#master-data":     ["administrator"],
    "#versions":        ["administrator", "coordinator"],
    "#reports":         ["administrator", "coordinator", "facility_manager"],
  };

  document.querySelectorAll(".nav-link").forEach(link => {
    const href = link.getAttribute("href");
    const allowed = rules[href];
    link.style.display = (!allowed || allowed.includes(role)) ? "" : "none";
  });
}

// ═════════════════════════════════════════════════════════════════════════════
// ROLE-SPECIFIC SECTIONS
// ═════════════════════════════════════════════════════════════════════════════

function renderRoleSpecificSections() {
  const role = state.currentUser?.role;

  const sectVisibility = {
    "master-data":     role === "administrator",
    "versions":        ["administrator", "coordinator"].includes(role),
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
    // A previous teacher/student session may have replaced the timetable
    // section; restore the default filter + grid markup for staff roles.
    if (!byId("viewFilter")) {
      byId("timetable").innerHTML = DEFAULT_TIMETABLE_HTML;
    }
    renderMasterData();
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// ROLE-SPECIFIC VIEWS
// ═════════════════════════════════════════════════════════════════════════════

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
  renderPersonalTimetable("teacherTimetableGrid", entry => entry.teacher_id === state.currentUser?.teacher_id);
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
  renderPersonalTimetable("studentTimetableGrid", entry => entry.section_id === state.currentUser?.section_id);
}

function renderPersonalTimetable(gridId, matches) {
  const grid = byId(gridId);
  // Teachers and students only ever see the published version (FR-08.4b),
  // never an in-progress draft.
  const published = state.publishedTimetable;
  const timeslots = uniqueTimeslots();
  const entries = (published?.entries || []).filter(entry => entry.status === "placed" && matches(entry));

  if (!entries.length) {
    grid.innerHTML = `<tr><td><div class="notice">No published timetable for you yet. Check back after the administrator publishes one.</div></td></tr>`;
    return;
  }
  grid.innerHTML = buildGrid(entries, timeslots);
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
  byId("facilityRoomReport").innerHTML = state.reports.room_utilization.map(room => `
    <div class="report-row">
      <div>
        <strong>${escapeHtml(room.code)} - ${escapeHtml(room.building)}</strong>
        <span>${room.capacity} capacity · ${room.used_slots} used slots · ${escapeHtml(room.status || "")}</span>
      </div>
      <div style="min-width: 100px;">
        <span style="font-weight: bold;">${room.utilization_pct ?? 0}%</span>
      </div>
    </div>
  `).join("");
}

// ═════════════════════════════════════════════════════════════════════════════
// DASHBOARD — stats + status
// ═════════════════════════════════════════════════════════════════════════════

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
  const role = state.currentUser?.role;
  // Teachers and students see the published timetable's status, not draft internals.
  const latest = ["teacher", "student"].includes(role) ? state.publishedTimetable : state.latestTimetable;
  if (!latest) {
    const message = ["teacher", "student"].includes(role)
      ? "No timetable has been published yet."
      : "No generated timetable yet.";
    byId("statusPanel").innerHTML = `<div class="status-line warning"><span>${message}</span><span class="pill">${["teacher", "student"].includes(role) ? "awaiting publish" : "Draft needed"}</span></div>`;
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

// ═════════════════════════════════════════════════════════════════════════════
// TIMETABLE — admin/coordinator full grid
// ═════════════════════════════════════════════════════════════════════════════

function uniqueTimeslots() {
  return state.masterData.timeslots.filter((slot, index, all) => {
    return all.findIndex(item => item.start_time === slot.start_time && item.end_time === slot.end_time) === index;
  });
}

function buildGrid(entries, timeslots) {
  const lookup = new Map();
  for (const entry of entries) {
    const key = `${entry.day}|${entry.start_time}|${entry.end_time}`;
    if (!lookup.has(key)) lookup.set(key, []);
    lookup.get(key).push(entry);
  }
  const header = `<tr><th class="slot-label">Time</th>${days.map(day => `<th>${day}</th>`).join("")}</tr>`;
  const rows = timeslots.map(slot => {
    const cells = days.map(day => {
      const key = `${day}|${slot.start_time}|${slot.end_time}`;
      const chips = (lookup.get(key) || []).map(classChip).join("");
      return `<td>${chips}</td>`;
    }).join("");
    return `<tr><th class="slot-label">${slot.start_time}<br>${slot.end_time}</th>${cells}</tr>`;
  }).join("");
  return header + rows;
}

function renderFilter() {
  const filter = byId("viewFilter");
  if (!filter) return; // teacher/student views have no section filter
  const current = filter.value || state.selectedSection;
  filter.innerHTML = [
    `<option value="all">All sections</option>`,
    ...state.masterData.sections.map(
      section => `<option value="${section.name}">${escapeHtml(section.name)}</option>`
    )
  ].join("");
  filter.value = current;
}

function renderTimetable() {
  const role = state.currentUser?.role;
  if (["teacher", "student"].includes(role)) return;

  const grid = byId("timetableGrid");
  if (!grid) return;
  const latest = state.latestTimetable;
  const entries = (latest?.entries || []).filter(entry => {
    if (entry.status !== "placed") return false;
    return state.selectedSection === "all" || entry.section_name === state.selectedSection;
  });
  grid.innerHTML = buildGrid(entries, uniqueTimeslots());

  if (role === "administrator") {
    grid.querySelectorAll(".lock-btn").forEach(btn => {
      btn.addEventListener("click", async e => {
        const entryId = parseInt(e.target.dataset.entryId);
        const isLocked = e.target.dataset.locked === "1";
        await guarded(async () => {
          if (isLocked) await api.unlockEntry(entryId);
          else await api.lockEntry(entryId);
          setBootstrap(await api.bootstrap());
          renderAll();
        }, isLocked ? "Entry unlocked" : "Entry locked — it will survive re-optimization");
      });
    });
  }

  renderUnplaced();
}

function classChip(entry) {
  const role = state.currentUser?.role;
  const lockBtn = role === "administrator"
    ? `<button class="lock-btn" data-entry-id="${entry.id}" data-locked="${entry.locked}">${entry.locked ? "Unlock" : "Lock"}</button>`
    : "";

  return `
    <div class="class-chip ${entry.locked ? "chip-locked" : ""}" data-entry-id="${entry.id}">
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
  const unplaced = (latest?.entries || []).filter(entry => entry.status === "unplaced");
  const list = byId("unplacedList");
  if (!list) return;
  if (!unplaced.length) {
    list.innerHTML = "";
    return;
  }
  list.innerHTML = `<h3 class="unplaced-heading">⚠️ ${unplaced.length} session${unplaced.length === 1 ? "" : "s"} could not be placed</h3>`
    + unplaced.map(entry => `
        <div class="notice notice-unplaced">
          <strong>${escapeHtml(entry.course_code)} — ${escapeHtml(entry.course_title)}</strong>
          for <strong>${escapeHtml(entry.section_name)}</strong> (${escapeHtml(entry.teacher_name)})
          ${entry.reason ? `<span class="unplaced-reason">${escapeHtml(entry.reason)}</span>` : ""}
        </div>
      `).join("");
}

// ═════════════════════════════════════════════════════════════════════════════
// MASTER DATA — admin only
// ═════════════════════════════════════════════════════════════════════════════

function recordRow(main, sub, category, id, editable = true) {
  const editBtn = editable
    ? `<button class="button small edit-${category}" data-id="${id}" title="Edit">✎</button>`
    : "";
  return `
    <div class="record">
      <div><strong>${main}</strong><span>${sub}</span></div>
      <div class="record-actions">
        ${editBtn}
        <button class="button small danger del-${category}" data-id="${id}" title="Delete">🗑</button>
      </div>
    </div>
  `;
}

function bindDelete(selector, confirmText, deleteFn) {
  document.querySelectorAll(selector).forEach(btn => {
    btn.addEventListener("click", async () => {
      if (!confirm(confirmText)) return;
      await guarded(async () => {
        await deleteFn(parseInt(btn.dataset.id));
        await reloadAndRender();
      }, "Deleted");
    });
  });
}

/** Switch an add-form into edit mode for one record. */
function enterEditMode(saveBtnId, recordId) {
  const btn = byId(saveBtnId);
  btn.dataset.editId = recordId;
  btn.textContent = "💾 Save";
}

function takeEditId(saveBtnId) {
  const btn = byId(saveBtnId);
  const editId = btn.dataset.editId ? parseInt(btn.dataset.editId) : null;
  delete btn.dataset.editId;
  return editId;
}

function renderMasterData() {
  const role = state.currentUser?.role;
  if (role !== "administrator") return;
  const data = state.masterData;

  // ── Teachers ──
  byId("teachersList").innerHTML = `
    <div class="add-form">
      <input class="input" id="tName" placeholder="Name" />
      <input class="input" id="tDept" placeholder="Department" />
      <input class="input" id="tLoad" placeholder="Max/day" type="number" min="1" value="4" />
      <button class="button primary small" id="addTeacherBtn">+ Add</button>
    </div>
  ` + data.teachers.map(t =>
    recordRow(escapeHtml(t.name), `${escapeHtml(t.department)} · max ${t.max_daily_load}/day`, "teacher", t.id)
  ).join("");

  byId("addTeacherBtn")?.addEventListener("click", () => guarded(async () => {
    const name = byId("tName").value.trim();
    const dept = byId("tDept").value.trim();
    if (!name || !dept) throw new Error("Teacher name and department are required");
    const load = parseInt(byId("tLoad").value) || 4;
    const editId = takeEditId("addTeacherBtn");
    if (editId) await api.updateTeacher(editId, name, dept, load);
    else await api.addTeacher(name, dept, load);
    await reloadAndRender();
  }, "Teacher saved"));
  document.querySelectorAll(".edit-teacher").forEach(btn => {
    btn.addEventListener("click", () => {
      const t = data.teachers.find(x => x.id === parseInt(btn.dataset.id));
      if (!t) return;
      byId("tName").value = t.name;
      byId("tDept").value = t.department;
      byId("tLoad").value = t.max_daily_load;
      enterEditMode("addTeacherBtn", t.id);
    });
  });
  bindDelete(".del-teacher", "Delete this teacher?", api.deleteTeacher);

  // ── Rooms ──
  byId("roomsList").innerHTML = `
    <div class="add-form">
      <input class="input" id="rCode" placeholder="Code (e.g. R101)" />
      <input class="input" id="rBldg" placeholder="Building" />
      <input class="input" id="rCap" placeholder="Capacity" type="number" min="1" />
      <select class="select" id="rType">
        <option value="lecture">Lecture</option>
        <option value="lab">Lab</option>
        <option value="auditorium">Auditorium</option>
      </select>
      <button class="button primary small" id="addRoomBtn">+ Add</button>
    </div>
  ` + data.rooms.map(r =>
    recordRow(`${escapeHtml(r.code)} · ${escapeHtml(r.building)}`, `${r.capacity} seats · ${escapeHtml(r.room_type)} · floor ${r.floor}`, "room", r.id)
  ).join("");

  byId("addRoomBtn")?.addEventListener("click", () => guarded(async () => {
    const code = byId("rCode").value.trim();
    const bldg = byId("rBldg").value.trim();
    const cap = parseInt(byId("rCap").value);
    if (!code || !bldg || !cap) throw new Error("Room code, building, and capacity are required");
    const editId = takeEditId("addRoomBtn");
    if (editId) {
      const existing = data.rooms.find(x => x.id === editId);
      await api.updateRoom(editId, code, bldg, existing?.floor ?? 0, cap, byId("rType").value, existing?.features ?? "");
    } else {
      await api.addRoom(code, bldg, 0, cap, byId("rType").value);
    }
    await reloadAndRender();
  }, "Room saved"));
  document.querySelectorAll(".edit-room").forEach(btn => {
    btn.addEventListener("click", () => {
      const r = data.rooms.find(x => x.id === parseInt(btn.dataset.id));
      if (!r) return;
      byId("rCode").value = r.code;
      byId("rBldg").value = r.building;
      byId("rCap").value = r.capacity;
      byId("rType").value = r.room_type;
      enterEditMode("addRoomBtn", r.id);
    });
  });
  bindDelete(".del-room", "Delete this room?", api.deleteRoom);

  // ── Sections ──
  byId("sectionsList").innerHTML = `
    <div class="add-form">
      <input class="input" id="sName" placeholder="Name (e.g. BSAI-4A)" />
      <input class="input" id="sDept" placeholder="Department" />
      <input class="input" id="sSize" placeholder="Size" type="number" min="1" />
      <button class="button primary small" id="addSectionBtn">+ Add</button>
    </div>
  ` + data.sections.map(s =>
    recordRow(escapeHtml(s.name), `${escapeHtml(s.department)} · ${s.size} students`, "section", s.id)
  ).join("");

  byId("addSectionBtn")?.addEventListener("click", () => guarded(async () => {
    const name = byId("sName").value.trim();
    const dept = byId("sDept").value.trim();
    const size = parseInt(byId("sSize").value);
    if (!name || !dept || !size) throw new Error("Section name, department, and size are required");
    const editId = takeEditId("addSectionBtn");
    if (editId) await api.updateSection(editId, name, dept, size);
    else await api.addSection(name, dept, size);
    await reloadAndRender();
  }, "Section saved"));
  document.querySelectorAll(".edit-section").forEach(btn => {
    btn.addEventListener("click", () => {
      const s = data.sections.find(x => x.id === parseInt(btn.dataset.id));
      if (!s) return;
      byId("sName").value = s.name;
      byId("sDept").value = s.department;
      byId("sSize").value = s.size;
      enterEditMode("addSectionBtn", s.id);
    });
  });
  bindDelete(".del-section", "Delete this section?", api.deleteSection);

  // ── Courses ──
  const teacherOptions = data.teachers.map(t => `<option value="${t.id}">${escapeHtml(t.name)}</option>`).join("");
  const sectionOptions = data.sections.map(s => `<option value="${s.id}">${escapeHtml(s.name)}</option>`).join("");
  byId("coursesList").innerHTML = `
    <div class="add-form">
      <input class="input" id="cCode" placeholder="Code (e.g. SE-301)" />
      <input class="input" id="cTitle" placeholder="Title" />
      <select class="select" id="cTeacher">${teacherOptions}</select>
      <select class="select" id="cSection">${sectionOptions}</select>
      <input class="input" id="cSessions" placeholder="Sessions/wk" type="number" min="1" value="2" />
      <select class="select" id="cRoomType">
        <option value="lecture">Lecture room</option>
        <option value="lab">Lab</option>
        <option value="auditorium">Auditorium</option>
      </select>
      <button class="button primary small" id="addCourseBtn">+ Add</button>
    </div>
  ` + data.courses.map(c =>
    recordRow(`${escapeHtml(c.code)} · ${escapeHtml(c.title)}`,
      `${escapeHtml(c.teacher_name)} → ${escapeHtml(c.section_name)} · ${c.weekly_sessions}×/wk · ${escapeHtml(c.required_room_type)}`,
      "course", c.id)
  ).join("");

  byId("addCourseBtn")?.addEventListener("click", () => guarded(async () => {
    const code = byId("cCode").value.trim();
    const title = byId("cTitle").value.trim();
    if (!code || !title) throw new Error("Course code and title are required");
    const args = [code, title, parseInt(byId("cTeacher").value), parseInt(byId("cSection").value),
      parseInt(byId("cSessions").value) || 2, byId("cRoomType").value];
    const editId = takeEditId("addCourseBtn");
    if (editId) await api.updateCourse(editId, ...args);
    else await api.addCourse(...args);
    await reloadAndRender();
  }, "Course saved"));
  document.querySelectorAll(".edit-course").forEach(btn => {
    btn.addEventListener("click", () => {
      const c = data.courses.find(x => x.id === parseInt(btn.dataset.id));
      if (!c) return;
      byId("cCode").value = c.code;
      byId("cTitle").value = c.title;
      byId("cTeacher").value = c.teacher_id;
      byId("cSection").value = c.section_id;
      byId("cSessions").value = c.weekly_sessions;
      byId("cRoomType").value = c.required_room_type;
      enterEditMode("addCourseBtn", c.id);
    });
  });
  bindDelete(".del-course", "Delete this course?", api.deleteCourse);

  // ── Holidays ──
  byId("holidaysList").innerHTML = `
    <div class="add-form">
      <input class="input" id="hName" placeholder="Name (e.g. Seminar day)" />
      <select class="select" id="hDay">${days.map(d => `<option>${d}</option>`).join("")}</select>
      <button class="button primary small" id="addHolidayBtn">+ Add</button>
    </div>
  ` + data.holidays.map(h =>
    recordRow(escapeHtml(h.name), escapeHtml(h.day), "holiday", h.id, false)
  ).join("");

  byId("addHolidayBtn")?.addEventListener("click", () => guarded(async () => {
    const name = byId("hName").value.trim();
    if (!name) throw new Error("Holiday name is required");
    await api.addHoliday(name, byId("hDay").value);
    await reloadAndRender();
  }, "Holiday added"));
  bindDelete(".del-holiday", "Remove this holiday?", api.deleteHoliday);

  // ── Timeslots ──
  byId("timeslotsList").innerHTML = `
    <div class="add-form">
      <select class="select" id="tsDay">${days.map(d => `<option>${d}</option>`).join("")}</select>
      <input class="input" id="tsStart" placeholder="Start (HH:MM)" />
      <input class="input" id="tsEnd" placeholder="End (HH:MM)" />
      <label class="check-inline"><input type="checkbox" id="tsMorning" /> Morning</label>
      <button class="button primary small" id="addTimeslotBtn">+ Add</button>
    </div>
  ` + data.timeslots.map(ts =>
    recordRow(`${escapeHtml(ts.day)} ${escapeHtml(ts.start_time)}–${escapeHtml(ts.end_time)}`,
      `${ts.is_morning ? "morning" : "afternoon"}${ts.is_last_slot ? " · last slot" : ""}`,
      "timeslot", ts.id, false)
  ).join("");

  byId("addTimeslotBtn")?.addEventListener("click", () => guarded(async () => {
    const start = byId("tsStart").value.trim();
    const end = byId("tsEnd").value.trim();
    if (!/^\d{2}:\d{2}$/.test(start) || !/^\d{2}:\d{2}$/.test(end)) {
      throw new Error("Start and end must be in HH:MM format");
    }
    if (end <= start) throw new Error("End time must be after start time");
    const maxOrder = Math.max(0, ...state.masterData.timeslots.map(t => t.sort_order));
    await api.addTimeslot(byId("tsDay").value, start, end, maxOrder + 1, byId("tsMorning").checked ? 1 : 0, 0);
    await reloadAndRender();
  }, "Timeslot added"));
  bindDelete(".del-timeslot", "Delete this timeslot?", api.deleteTimeslot);

  // ── Preferences (FR-03.14: enable/disable + weight) ──
  byId("preferencesList").innerHTML = data.preferences.map(pref => `
    <div class="record pref-record">
      <div>
        <strong>${escapeHtml(pref.label)}</strong>
        <span class="pref-controls">
          <label class="check-inline">
            <input type="checkbox" class="pref-enabled" data-id="${pref.id}" ${pref.enabled ? "checked" : ""} /> Enabled
          </label>
          weight
          <input type="number" class="input pref-weight" data-id="${pref.id}" min="0" max="10" value="${pref.weight}" />
          <button class="button small pref-save" data-id="${pref.id}">Save</button>
        </span>
      </div>
    </div>
  `).join("");

  document.querySelectorAll(".pref-save").forEach(btn => {
    btn.addEventListener("click", () => guarded(async () => {
      const id = btn.dataset.id;
      const enabled = document.querySelector(`.pref-enabled[data-id="${id}"]`).checked;
      const weight = parseInt(document.querySelector(`.pref-weight[data-id="${id}"]`).value);
      if (Number.isNaN(weight) || weight < 0 || weight > 10) throw new Error("Weight must be between 0 and 10");
      await api.updatePreference(parseInt(id), enabled, weight);
      await reloadAndRender();
    }, "Preference saved — takes effect on the next generation run"));
  });

  renderAvailabilityEditor();
}

// ── Teacher availability editor (per-teacher per-slot toggle grid) ──

async function renderAvailabilityEditor() {
  const editor = byId("availabilityEditor");
  if (!editor) return;
  const teachers = state.masterData.teachers;
  if (!teachers.length) {
    editor.innerHTML = '<p class="empty-state">Add a teacher first.</p>';
    return;
  }

  const previous = editor.querySelector("#availTeacher")?.value;
  editor.innerHTML = `
    <div class="add-form">
      <select class="select" id="availTeacher">
        ${teachers.map(t => `<option value="${t.id}">${escapeHtml(t.name)}</option>`).join("")}
      </select>
      <button class="button primary small" id="availSaveBtn">Save availability</button>
    </div>
    <div id="availGrid"></div>
  `;
  const teacherSelect = byId("availTeacher");
  if (previous) teacherSelect.value = previous;

  async function drawGrid() {
    const teacherId = parseInt(teacherSelect.value);
    const { availability } = await api.getTeacherAvailability(teacherId);
    const unavailable = new Set(availability.filter(a => !a.is_available).map(a => a.timeslot_id));
    const slots = state.masterData.timeslots;
    const periods = uniqueTimeslots();

    const header = `<tr><th class="slot-label">Time</th>${days.map(d => `<th>${d}</th>`).join("")}</tr>`;
    const rows = periods.map(period => {
      const cells = days.map(day => {
        const slot = slots.find(s => s.day === day && s.start_time === period.start_time && s.end_time === period.end_time);
        if (!slot) return "<td></td>";
        const checked = unavailable.has(slot.id) ? "" : "checked";
        return `<td class="avail-cell"><label><input type="checkbox" class="avail-toggle" data-slot-id="${slot.id}" ${checked} /></label></td>`;
      }).join("");
      return `<tr><th class="slot-label">${period.start_time}<br>${period.end_time}</th>${cells}</tr>`;
    }).join("");
    byId("availGrid").innerHTML = `<div class="table-wrap"><table class="timetable-grid avail-grid">${header}${rows}</table></div>`;
  }

  teacherSelect.addEventListener("change", () => guarded(drawGrid));
  byId("availSaveBtn").addEventListener("click", () => guarded(async () => {
    const teacherId = parseInt(teacherSelect.value);
    const unavailable = [...document.querySelectorAll(".avail-toggle:not(:checked)")]
      .map(input => parseInt(input.dataset.slotId));
    await api.setTeacherAvailability(teacherId, unavailable);
  }, "Availability saved — takes effect on the next generation run"));

  await guarded(drawGrid);
}

async function reloadAndRender() {
  setBootstrap(await api.bootstrap());
  renderAll();
}

// ═════════════════════════════════════════════════════════════════════════════
// VERSIONS — list, publish, compare (FR-08, FR-11, FR-14)
// ═════════════════════════════════════════════════════════════════════════════

export async function refreshVersions() {
  const role = state.currentUser?.role;
  if (!["administrator", "coordinator"].includes(role)) return;
  try {
    const { versions } = await api.getVersions();
    setVersions(versions);
    renderVersions();
  } catch (err) {
    console.error(err);
  }
}

function renderVersions() {
  const role = state.currentUser?.role;
  const listEl = byId("versionsList");
  if (!listEl || !["administrator", "coordinator"].includes(role)) return;
  const versions = state.versions;

  if (!versions.length) {
    listEl.innerHTML = '<p class="empty-state">No versions yet. Generate a draft first.</p>';
  } else {
    listEl.innerHTML = versions.map(v => `
      <div class="record version-record">
        <div>
          <strong>#${v.id} · ${escapeHtml(v.name)}</strong>
          <span>score ${v.score} · ${v.hard_conflicts} hard conflicts · ${v.unplaced_count} unplaced · ${v.entry_count} entries</span>
        </div>
        <div class="version-actions">
          <span class="status-badge status-${escapeHtml(v.status)}">${escapeHtml(v.status)}</span>
          ${role === "administrator" && v.status === "draft"
            ? `<button class="button small primary publish-version-btn" data-id="${v.id}">Publish</button>`
            : ""}
        </div>
      </div>
    `).join("");

    listEl.querySelectorAll(".publish-version-btn").forEach(btn => {
      btn.addEventListener("click", () => guarded(async () => {
        await api.publishTimetable(parseInt(btn.dataset.id));
        await reloadAndRender();
        await refreshVersions();
      }, "Timetable published — teachers and students have been notified"));
    });
  }

  const options = versions.map(v => `<option value="${v.id}">#${v.id} (${escapeHtml(v.status)})</option>`).join("");
  const selectA = byId("compareA");
  const selectB = byId("compareB");
  const keepA = selectA.value;
  const keepB = selectB.value;
  selectA.innerHTML = options;
  selectB.innerHTML = options;
  if (keepA) selectA.value = keepA;
  if (keepB) selectB.value = keepB;

  const compareBtn = byId("compareBtn");
  if (!compareBtn._bound) {
    compareBtn._bound = true;
    compareBtn.addEventListener("click", () => guarded(async () => {
      const a = parseInt(byId("compareA").value);
      const b = parseInt(byId("compareB").value);
      if (!a || !b) throw new Error("Pick two versions to compare");
      const diff = await api.compareVersions(a, b);
      renderCompareResult(diff);
    }));
  }
}

function renderCompareResult(diff) {
  const el = byId("compareResult");
  const describe = entry =>
    `${escapeHtml(entry.event_uid || entry.course_code)} — ${escapeHtml(entry.day || "unplaced")} ${escapeHtml(entry.start_time || "")} in ${escapeHtml(entry.room_code || "no room")}`;

  const changedRows = diff.changed.map(change => `
    <div class="report-row">
      <span>${escapeHtml(change.event_uid)}</span>
      <span>${escapeHtml(change.before.day || "unplaced")} ${escapeHtml(change.before.start_time || "")} ${escapeHtml(change.before.room_code || "")}
        → ${escapeHtml(change.after.day || "unplaced")} ${escapeHtml(change.after.start_time || "")} ${escapeHtml(change.after.room_code || "")}</span>
    </div>
  `).join("");

  el.innerHTML = `
    <div class="guide-tip">
      Comparing <strong>#${diff.version_a}</strong> → <strong>#${diff.version_b}</strong>:
      ${diff.totals.changed} moved · ${diff.totals.added} added · ${diff.totals.removed} removed · ${diff.unchanged_count} unchanged
    </div>
    ${changedRows || (diff.totals.added || diff.totals.removed ? "" : '<p class="empty-state">No differences between these versions.</p>')}
    ${diff.added.map(entry => `<div class="report-row"><span>Added</span><span>${describe(entry)}</span></div>`).join("")}
    ${diff.removed.map(entry => `<div class="report-row"><span>Removed</span><span>${describe(entry)}</span></div>`).join("")}
  `;
}

// ═════════════════════════════════════════════════════════════════════════════
// NOTIFICATIONS (FR-13)
// ═════════════════════════════════════════════════════════════════════════════

export async function refreshNotifications() {
  if (!state.currentUser?.id) return;
  try {
    setNotifications(await api.getNotifications(state.currentUser.id));
    renderNotificationBadge();
    renderNotificationList();
  } catch (err) {
    console.error(err);
  }
}

function renderNotificationBadge() {
  const badge = byId("notifBadge");
  if (!badge) return;
  badge.hidden = !state.unreadCount;
  badge.textContent = state.unreadCount;
}

export function renderNotificationList() {
  const listEl = byId("notifList");
  if (!listEl) return;
  if (!state.notifications.length) {
    listEl.innerHTML = '<p class="empty-state">No notifications yet.</p>';
    return;
  }
  listEl.innerHTML = state.notifications.map(item => `
    <div class="notif-item ${item.read ? "" : "unread"}" data-id="${item.id}">
      <strong>${escapeHtml(item.title)}</strong>
      <span>${escapeHtml(item.message)}</span>
      <small>${escapeHtml(item.category)} · ${formatTimestamp(item.created_at)}</small>
    </div>
  `).join("");

  listEl.querySelectorAll(".notif-item.unread").forEach(el => {
    el.addEventListener("click", () => guarded(async () => {
      await api.markNotificationRead(parseInt(el.dataset.id));
      await refreshNotifications();
    }));
  });
}

// ═════════════════════════════════════════════════════════════════════════════
// REPORTS (FR-21)
// ═════════════════════════════════════════════════════════════════════════════

function renderReports() {
  const role = state.currentUser?.role;
  if (!["administrator", "coordinator", "facility_manager"].includes(role)) {
    const el = byId("reports");
    if (el) el.style.display = "none";
    return;
  }
  if (role === "facility_manager") return; // facility manager has its own view

  byId("roomReport").innerHTML = state.reports.room_utilization.map(room => `
    <div class="report-row ${room.status === "peak" ? "row-warning" : ""}">
      <span>${escapeHtml(room.code)} - ${escapeHtml(room.building)} - ${room.capacity} seats
        ${room.status === "free" ? '<span class="pill">free</span>' : ""}
        ${room.status === "peak" ? '<span class="pill-urgent">peak</span>' : ""}</span>
      <span>${room.used_slots} slots · ${room.utilization_pct ?? 0}%</span>
    </div>
  `).join("");

  byId("teacherReport").innerHTML = state.reports.teacher_load.map(teacher => `
    <div class="report-row ${teacher.overloaded ? "row-warning" : ""}">
      <span>${escapeHtml(teacher.name)} - ${escapeHtml(teacher.department)}
        ${teacher.overloaded ? '<span class="pill-urgent">over daily limit</span>' : ""}</span>
      <span>${teacher.assigned_sessions} sessions · busiest day ${teacher.busiest_day_load}/${teacher.max_daily_load}</span>
    </div>
  `).join("");

  const gaps = state.reports.section_gaps || [];
  byId("gapReport").innerHTML = gaps.length
    ? gaps.map(gap => `
        <div class="report-row">
          <span>${escapeHtml(gap.section_name)} · ${escapeHtml(gap.day)}</span>
          <span>${gap.gap_periods} free period${gap.gap_periods === 1 ? "" : "s"} between classes</span>
        </div>
      `).join("")
    : '<p class="empty-state">No gaps — every section has compact days.</p>';

  renderAuditLog(role);
}

async function renderAuditLog(role) {
  const section = byId("auditSection");
  if (!section) return;
  if (role !== "administrator") {
    section.style.display = "none";
    return;
  }
  section.style.display = "";
  try {
    const { auditLog } = await api.getAuditLog();
    byId("auditReport").innerHTML = auditLog.length
      ? auditLog.slice(0, 25).map(item => `
          <div class="report-row">
            <span><strong>${escapeHtml(item.actor_name || "system")}</strong> ${escapeHtml(item.action)} ${escapeHtml(item.entity_type)}${item.entity_id ? " #" + item.entity_id : ""}</span>
            <span>${formatTimestamp(item.created_at)}</span>
          </div>
        `).join("")
      : '<p class="empty-state">No audited actions yet.</p>';
  } catch (err) {
    console.error(err);
  }
}

function formatTimestamp(value) {
  if (!value) return "";
  // SQLite CURRENT_TIMESTAMP is UTC in "YYYY-MM-DD HH:MM:SS" form.
  const date = new Date(value.replace(" ", "T") + "Z");
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

// ═════════════════════════════════════════════════════════════════════════════
// CHANGE REQUESTS
// ═════════════════════════════════════════════════════════════════════════════

function renderChangeRequests() {
  const section = byId("change-requests");
  if (!section || section.style.display === "none") return;

  const role = state.currentUser?.role;
  const formWrapper = byId("changeRequestFormWrapper");
  const listEl = byId("requestsList");
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
    byId("changeRequestForm")?.addEventListener("submit", async e => {
      e.preventDefault();
      const btn = e.target.querySelector("button[type=submit]");
      btn.disabled = true;
      btn.textContent = "Submitting...";
      await guarded(async () => {
        const reason = byId("changeReason").value.trim();
        if (!reason) throw new Error("Please describe the reason for the change");
        const urgency = e.target.querySelector('input[name="urgency"]:checked')?.value || "normal";
        await api.submitChangeRequest(
          state.currentUser.id, byId("changeTargetType").value, 0,
          reason, urgency, byId("changePrefAlt").value
        );
        byId("changeReason").value = "";
        byId("changePrefAlt").value = "";
        const resp = await api.getChangeRequests();
        state.changeRequests = resp.changeRequests || [];
        renderChangeRequestList(role);
      }, "Change request submitted — reviewers have been notified");
      btn.disabled = false;
      btn.textContent = "Submit Request";
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
    if (role === "administrator" && req.status === "approved") {
      actions = '<div class="admin-action-inline"><button data-request-id="' + req.id + '" class="button small primary reopt-btn">Re-generate with this change</button></div>';
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

  async function refreshList() {
    const resp = await api.getChangeRequests();
    state.changeRequests = resp.changeRequests || [];
    renderChangeRequestList(role);
  }

  if (role === "coordinator") {
    listEl.querySelectorAll(".coord-note-btn").forEach(btn => {
      btn.addEventListener("click", () => guarded(async () => {
        const input = btn.parentElement.querySelector(".coord-note-input");
        if (!input.value.trim()) throw new Error("Write a recommendation first");
        btn.disabled = true;
        await api.addCoordinatorNote(parseInt(btn.dataset.rid), input.value.trim());
        await refreshList();
      }, "Recommendation added"));
    });
  }
  if (role === "administrator") {
    listEl.querySelectorAll(".approve-btn").forEach(btn => {
      btn.addEventListener("click", () => guarded(async () => {
        const respInput = btn.parentElement.querySelector(".admin-resp-input");
        btn.disabled = true;
        await api.updateChangeRequestStatus(parseInt(btn.dataset.requestId), "approved", respInput ? respInput.value : "");
        await refreshList();
      }, "Request approved — requester notified"));
    });
    listEl.querySelectorAll(".reject-btn").forEach(btn => {
      btn.addEventListener("click", () => guarded(async () => {
        const respInput = btn.parentElement.querySelector(".admin-resp-input");
        btn.disabled = true;
        await api.updateChangeRequestStatus(parseInt(btn.dataset.requestId), "rejected", respInput ? respInput.value : "");
        await refreshList();
      }, "Request rejected — requester notified"));
    });
    listEl.querySelectorAll(".reopt-btn").forEach(btn => {
      btn.addEventListener("click", () => guarded(async () => {
        btn.disabled = true;
        btn.textContent = "Re-optimizing…";
        const payload = await api.reoptimizeTimetable();
        await api.updateChangeRequestStatus(parseInt(btn.dataset.requestId), "implemented", "Applied via re-optimization");
        setBootstrap(await api.bootstrap());
        await refreshList();
        renderAll();
        await refreshVersions();
        const d = payload.disruption || {};
        toast(`Re-optimized: ${d.changed ?? 0} moved, ${d.unchanged ?? 0} unchanged, ${d.locked_preserved ?? 0} locked preserved`, "success");
      }));
    });
  }
}
