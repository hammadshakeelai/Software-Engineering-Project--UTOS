export const state = {
  masterData: {
    teachers: [],
    rooms: [],
    sections: [],
    courses: [],
    timeslots: [],
    holidays: [],
    preferences: []
  },
  latestTimetable: null,
  reports: {
    room_utilization: [],
    teacher_load: []
  },
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
