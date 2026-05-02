export const state = {
  currentUser: null,
  masterData: {
    teachers: [],
    rooms: [],
    sections: [],
    courses: [],
    timeslots: [],
    holidays: [],
    preferences: [],
    users: []
  },
  latestTimetable: null,
  reports: {
    room_utilization: [],
    teacher_load: []
  },
  changeRequests: [],
  selectedSection: "all"
};

export function setBootstrap(payload) {
  state.masterData = payload.masterData;
  state.latestTimetable = payload.latestTimetable;
  state.reports = payload.reports;
}

export function setGenerated(payload) {
  state.latestTimetable = payload.latestTimetable;
  state.reports = payload.reports;
}

export function login(user) {
  state.currentUser = user;
  localStorage.setItem("currentUser", JSON.stringify(user));
}

export function logout() {
  state.currentUser = null;
  localStorage.removeItem("currentUser");
}

export function loadUserFromStorage() {
  const stored = localStorage.getItem("currentUser");
  if (stored) {
    state.currentUser = JSON.parse(stored);
  }
}

export function setChangeRequests(requests) {
  state.changeRequests = requests;
}
