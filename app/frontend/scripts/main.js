import { api } from "./api.js";
import { renderAll, renderLoginScreen, renderNav } from "./render.js";
import { setBootstrap, setGenerated, state, login, logout, loadUserFromStorage, setChangeRequests } from "./state.js";

const appShell = document.querySelector(".app-shell");
const loginScreen = document.getElementById("loginScreen");
const userSelect = document.getElementById("userSelect");
const loginBtn = document.getElementById("loginBtn");
const logoutBtn = document.getElementById("logoutBtn");
const refreshBtn = document.getElementById("refreshBtn");
const generateBtn = document.getElementById("generateBtn");
const publishBtn = document.getElementById("publishBtn");
const viewFilter = document.getElementById("viewFilter");

async function loadLogin() {
  try {
    const resp = await api.getUsers();
    state.masterData.users = resp.users;
    renderLoginScreen();
  } catch (error) {
    console.error("Failed to load users:", error);
  }
}

async function handleLogin() {
  const userId = parseInt(userSelect.value);
  const user = state.masterData.users.find(u => u.id === userId);
  if (user) {
    login(user);
    appShell.style.display = "flex";
    loginScreen.style.display = "none";
    renderNav();
    await load();
  }
}

function handleLogout() {
  logout();
  loginScreen.style.display = "flex";
  appShell.style.display = "none";
  loadLogin();
}

async function load() {
  setBusy(refreshBtn, true);
  try {
    const payload = await api.bootstrap();
    setBootstrap(payload);
    const changeReqResp = await api.getChangeRequests();
    setChangeRequests(changeReqResp.changeRequests || []);
    renderAll();
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
  button.textContent = busy ? "Working..." : button.dataset.originalText;
}

loadUserFromStorage();
if (state.currentUser) {
  appShell.style.display = "flex";
  loginScreen.style.display = "none";
  renderNav();
  load().catch((error) => {
    document.body.innerHTML = `<main class="workspace"><section class="section-band"><h1>Unable to start UI</h1><p>${error.message}</p></section></main>`;
  });
} else {
  appShell.style.display = "none";
  loginScreen.style.display = "flex";
  loadLogin().catch((error) => {
    document.body.innerHTML = `<main class="workspace"><section class="section-band"><h1>Unable to load login</h1><p>${error.message}</p></section></main>`;
  });
}

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
