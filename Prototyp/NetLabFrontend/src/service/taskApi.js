// src/services/taskApi.js
import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export default {
  getTasks() {
    return api.get("/tasks");
  },
  createTask(taskTitle) {
    return api.post("/tasks", { title: taskTitle });
  },
  updateTask(taskId, updatedData) {
    return api.put(`/tasks/${taskId}`, updatedData);
  },
};
