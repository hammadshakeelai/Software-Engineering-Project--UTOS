import { api } from "./api.js";
import {
  renderAll,
  renderLoginScreen,
  renderNotificationList,
  refreshNotifications,
  refreshVersions,
  toast,
  updateRoleBadge
} from "./render.js";
import { setBootstrap, setGenerated, state, login, logout, loadUserFromStorage, setChangeRequests } from "./state.js";

const appShell      = document.getElementById("appShell");
const loginScreen   = document.getElementById("loginScreen");
const loginBtn      = document.getElementById("loginBtn");
const logoutBtn     = document.getElementById("logoutBtn");
const refreshBtn    = document.getElementById("refreshBtn");
const generateBtn   = document.getElementById("generateBtn");
const reoptimizeBtn = document.getElementById("reoptimizeBtn");
const publishBtn    = document.getElementById("publishBtn");
const exportBtn     = document.getElementById("exportBtn");
const printBtn      = document.getElementById("printBtn");
const notifBtn      = document.getElementById("notifBtn");
const notifPanel    = document.getElementById("notifPanel");
const notifCloseBtn = document.getElementById("notifCloseBtn");

function showLoginStatus(message) {
  const selector = document.getElementById("userSelector");
  if (selector) {
    selector.innerHTML = `<div class="login-status">${message}</div>`;
  }
}

async function loadLogin() {
  // Hosted free tiers (Render/Railway) sleep when idle, so the first request
  // can take 30-50s to wake the server and may briefly return 502/503. Retry
  // with a clear "waking up" message instead of looking broken.
  const maxAttempts = 12;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      showLoginStatus(attempt === 1
        ? "Loading…"
        : `Waking up the server… (this can take ~30s on first visit)`);
      const { users } = await api.getUsers();
      state.masterData.users = users;
      renderLoginScreen();
      return;
    } catch (err) {
      if (attempt === maxAttempts) throw err;
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

async function handleLogin() {
  const currentActive = document.querySelector(".role-card.selected");
  const selectedId    = document.getElementById("accountList")?.dataset.selectedId;
  if (!currentActive || !selectedId) return;

  const userId = parseInt(selectedId);
  const user   = state.masterData.users.find(u => u.id === userId);

  if (user) {
    login(user);
    applyRoleUI(user);
    appShell.style.display    = "flex";
    loginScreen.style.display = "none";
    await load();
  }
}

function handleLogout() {
  logout();
  loginScreen.style.display = "flex";
  appShell.style.display    = "none";
  loadLogin().catch(err => toast(err.message, "error"));
}

/** Apply role-specific topbar, button visibility, and guide banner. */
function applyRoleUI(user) {
  const role = user.role;

  updateRoleBadge(user);

  const titleMap = {
    administrator:    "Schedule Control Center",
    coordinator:      "Department Overview",
    teacher:          "My Teaching Schedule",
    student:          "My Section Timetable",
    facility_manager: "Room & Facility Dashboard",
  };
  document.getElementById("topbarTitle").textContent = titleMap[role] ?? "UTOS";

  generateBtn.hidden   = role !== "administrator";
  reoptimizeBtn.hidden = role !== "administrator";
  publishBtn.hidden    = true;   // revealed only when a draft exists, by load()
  exportBtn.hidden     = !["administrator", "coordinator", "teacher", "student"].includes(role);
  printBtn.hidden      = exportBtn.hidden;

  const guides = {
    administrator: {
      icon: "🛠️",
      title: "You are the Timetable Administrator",
      text:  "Generate a timetable draft, review conflicts, lock entries you want to preserve, then publish the final version. Use Master Data to add teachers, rooms, and courses first.",
    },
    coordinator: {
      icon: "📋",
      title: "You are a Department Coordinator",
      text:  "Review the timetable quality and department assignments. Submit change requests if adjustments are needed — the Admin will review and action them.",
    },
    teacher: {
      icon: "👩‍🏫",
      title: "You are a Teacher",
      text:  "View your personal weekly teaching schedule below. If you need a class rescheduled, use the Requests page to submit a change request.",
    },
    student: {
      icon: "🎓",
      title: "You are a Student",
      text:  "Your section's published timetable is shown below. Contact your department coordinator if you spot any issues.",
    },
    facility_manager: {
      icon: "🏢",
      title: "You are the Facility Manager",
      text:  "Monitor room utilization and capacity across all buildings. The Reports section shows which rooms are free, used, or overloaded.",
    },
  };

  const banner      = document.getElementById("roleBanner");
  const bannerIcon  = document.getElementById("roleBannerIcon");
  const bannerTitle = document.getElementById("roleBannerTitle");
  const bannerText  = document.getElementById("roleBannerText");

  const guide = guides[role];
  if (guide) {
    bannerIcon.textContent  = guide.icon;
    bannerTitle.textContent = guide.title;
    bannerText.textContent  = guide.text;
    banner.hidden           = false;
    banner.setAttribute("data-role", role);
  } else {
    banner.hidden = true;
  }
}

async function load() {
  setBusy(refreshBtn, true);
  try {
    const payload = await api.bootstrap();
    setBootstrap(payload);
    const changeReqResp = await api.getChangeRequests();
    setChangeRequests(changeReqResp.changeRequests || []);
    renderAll();
    if (state.currentUser) applyRoleUI(state.currentUser);
    if (state.currentUser?.role === "administrator" && state.latestTimetable) {
      publishBtn.hidden = state.latestTimetable.status !== "draft";
    }
    await refreshNotifications();
    await refreshVersions();
  } catch (err) {
    toast(err.message, "error");
  } finally {
    setBusy(refreshBtn, false);
  }
}

async function generate() {
  setBusy(generateBtn, true);
  try {
    const payload = await api.generateTimetable();
    setGenerated(payload);
    renderAll();
    if (state.currentUser?.role === "administrator") {
      publishBtn.hidden = false;
    }
    await refreshVersions();
    toast(`Draft version ${payload.versionId} generated (score ${payload.latestTimetable.score})`, "success");
  } catch (err) {
    toast(err.message, "error");
  } finally {
    setBusy(generateBtn, false);
  }
}

async function reoptimize() {
  setBusy(reoptimizeBtn, true);
  try {
    const payload = await api.reoptimizeTimetable();
    setGenerated(payload);
    renderAll();
    if (state.currentUser?.role === "administrator") {
      publishBtn.hidden = false;
    }
    await refreshVersions();
    const d = payload.disruption || {};
    toast(`Re-optimized: ${d.changed ?? 0} moved, ${d.unchanged ?? 0} unchanged, ${d.locked_preserved ?? 0} locked preserved`, "success");
  } catch (err) {
    toast(err.message, "error");
  } finally {
    setBusy(reoptimizeBtn, false);
  }
}

async function publish() {
  if (!state.latestTimetable) return;
  setBusy(publishBtn, true);
  try {
    const result = await api.publishTimetable(state.latestTimetable.id);
    await load();
    toast(`Published — ${result.notified ?? 0} users notified`, "success");
    publishBtn.hidden = true;
  } catch (err) {
    toast(err.message, "error");
  } finally {
    setBusy(publishBtn, false);
  }
}

// ─── Export (FR-12): CSV download of the visible timetable ───────────────────
function exportCsv() {
  const role = state.currentUser?.role;
  // Teachers and students export the published timetable; staff export the latest draft.
  const latest = ["teacher", "student"].includes(role) ? state.publishedTimetable : state.latestTimetable;
  if (!latest?.entries?.length) {
    toast("Nothing to export yet — no timetable available", "error");
    return;
  }
  let entries = latest.entries.filter(e => e.status === "placed");
  if (role === "teacher") entries = entries.filter(e => e.teacher_id === state.currentUser.teacher_id);
  if (role === "student") entries = entries.filter(e => e.section_id === state.currentUser.section_id);

  const header = ["Day", "Start", "End", "Course", "Title", "Teacher", "Section", "Room", "Building", "Locked"];
  const quote = value => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const rows = entries.map(e => [
    e.day, e.start_time, e.end_time, e.course_code, e.course_title,
    e.teacher_name, e.section_name, e.room_code, e.room_building, e.locked ? "yes" : "no"
  ].map(quote).join(","));
  const csv = [header.join(","), ...rows].join("\r\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `utos-timetable-v${latest.id}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  toast("Timetable exported as CSV", "success");
}

function setBusy(button, busy) {
  button.disabled = busy;
  button.dataset.originalText ??= button.textContent;
  button.textContent = busy ? "Working…" : button.dataset.originalText;
}

// ─── Boot ─────────────────────────────────────────────────────────────────────
loadUserFromStorage();
if (state.currentUser) {
  applyRoleUI(state.currentUser);
  appShell.style.display    = "flex";
  loginScreen.style.display = "none";
  load().catch((error) => {
    document.body.innerHTML = `<main class="workspace"><section class="section-band"><h1>Unable to start UI</h1><p>${error.message}</p></section></main>`;
  });
} else {
  appShell.style.display    = "none";
  loginScreen.style.display = "flex";
  loadLogin().catch((error) => {
    document.body.innerHTML = `<main class="workspace"><section class="section-band"><h1>Unable to load login</h1><p>${error.message}</p></section></main>`;
  });
}

// ─── Event listeners ─────────────────────────────────────────────────────────
loginBtn.addEventListener("click", handleLogin);
logoutBtn.addEventListener("click", handleLogout);
refreshBtn.addEventListener("click", load);
generateBtn.addEventListener("click", generate);
reoptimizeBtn.addEventListener("click", reoptimize);
publishBtn?.addEventListener("click", publish);
exportBtn.addEventListener("click", exportCsv);
printBtn.addEventListener("click", () => window.print());
notifBtn.addEventListener("click", async () => {
  notifPanel.hidden = !notifPanel.hidden;
  if (!notifPanel.hidden) {
    await refreshNotifications();
    renderNotificationList();
  }
});
notifCloseBtn.addEventListener("click", () => { notifPanel.hidden = true; });
// Delegated: the #viewFilter select is re-created when role views swap the
// timetable section, so a direct listener would be lost.
document.addEventListener("change", (event) => {
  if (event.target?.id === "viewFilter") {
    state.selectedSection = event.target.value;
    renderAll();
  }
});

document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((item) => item.classList.remove("active"));
    link.classList.add("active");
  });
});
