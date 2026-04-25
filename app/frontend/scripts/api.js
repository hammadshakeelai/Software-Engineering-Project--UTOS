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
  }
};
