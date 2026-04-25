import { api } from "./api.js";
import { renderAll } from "./render.js";
import { setBootstrap, setGenerated, state } from "./state.js";

const refreshBtn = document.getElementById("refreshBtn");
const generateBtn = document.getElementById("generateBtn");
const viewFilter = document.getElementById("viewFilter");

async function load() {
  setBusy(refreshBtn, true);
  try {
    const payload = await api.bootstrap();
    setBootstrap(payload);
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

function setBusy(button, busy) {
  button.disabled = busy;
  button.dataset.originalText ??= button.textContent;
  button.textContent = busy ? "Working..." : button.dataset.originalText;
}

refreshBtn.addEventListener("click", load);
generateBtn.addEventListener("click", generate);
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

load().catch((error) => {
  document.body.innerHTML = `<main class="workspace"><section class="section-band"><h1>Unable to start UI</h1><p>${error.message}</p></section></main>`;
});
