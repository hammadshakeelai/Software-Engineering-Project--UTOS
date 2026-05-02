import { api } from "./api.js";
import { renderAll, renderLoginScreen, updateRoleBadge } from "./render.js";
import { setBootstrap, setGenerated, state, login, logout, loadUserFromStorage, setChangeRequests } from "./state.js";

const appShell    = document.getElementById("appShell");
const loginScreen = document.getElementById("loginScreen");
const loginBtn    = document.getElementById("loginBtn");
const logoutBtn   = document.getElementById("logoutBtn");
const refreshBtn  = document.getElementById("refreshBtn");
const generateBtn = document.getElementById("generateBtn");
const publishBtn  = document.getElementById("publishBtn");
const viewFilter  = document.getElementById("viewFilter");

// ─── RBAC: role data ─────────────────────────────────────────────────────────
// Maps data-user-id on the login cards → user objects.
// Coordinator (id=5) maps to role "coordinator" in the DB seed.
const staticUsers = [
  { id: 1, name: "Timetable Admin",       role: "administrator"   },
  { id: 5, name: "Department Coordinator",role: "coordinator"     },
  { id: 2, name: "Dr. Ayesha Khan",       role: "teacher",  teacher_id: 1 },
  { id: 3, name: "BSAI-4A Student",       role: "student",  section_id: 1 },
  { id: 4, name: "Facility Manager",      role: "facility_manager"},
];

async function loadLogin() {
  state.masterData.users = staticUsers;
  renderLoginScreen();
}

async function handleLogin() {
  const currentActive = document.querySelector(".role-card.selected");
  if (!currentActive) return;

  const userId = parseInt(currentActive.getAttribute("data-user-id"));
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
  loadLogin();
}

/** Apply role-specific topbar, button visibility, and guide banner. */
function applyRoleUI(user) {
  const role = user.role;

  // ── Update role badge in sidebar ─────────────────────────────────────────
  updateRoleBadge(user);

  // ── Topbar title ──────────────────────────────────────────────────────────
  const titleMap = {
    administrator:    "Schedule Control Center",
    coordinator:      "Department Overview",
    teacher:          "My Teaching Schedule",
    student:          "My Section Timetable",
    facility_manager: "Room & Facility Dashboard",
  };
  document.getElementById("topbarTitle").textContent = titleMap[role] ?? "UTOS";

  // ── Action buttons ────────────────────────────────────────────────────────
  generateBtn.hidden = role !== "administrator";
  publishBtn.hidden  = true;   // revealed only after generation by admin

  // ── Guide banner ──────────────────────────────────────────────────────────
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

  const banner     = document.getElementById("roleBanner");
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
    // Re-apply role UI after render in case renderAll reset anything
    if (state.currentUser) applyRoleUI(state.currentUser);
    // Show publish button only for admin after a timetable exists
    if (state.currentUser?.role === "administrator" && state.latestTimetable) {
      publishBtn.hidden = false;
    }
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
  } finally {
    setBusy(generateBtn, false);
  }
}

async function publish() {
  if (!state.latestTimetable) return;
  setBusy(publishBtn, true);
  try {
    await api.publishTimetable(state.latestTimetable.id);
    state.latestTimetable.status = "published";
    renderAll();
  } finally {
    setBusy(publishBtn, false);
  }
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
publishBtn?.addEventListener("click", publish);
viewFilter.addEventListener("change", (event) => {
  state.selectedSection = event.target.value;
  renderAll();
});

document.querySelectorAll(".nav-link").forEach((link) => {
  link.addEventListener("click", () => {
    document.querySelectorAll(".nav-link").forEach((item) => item.classList.remove("active"));
    link.classList.add("active");
  });
});
