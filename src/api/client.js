import axios from "axios";
import { mockResponse } from "./mockData";

const USE_MOCK = true; // flip to false when backend is running
const BASE = "http://localhost:8000";

const http = axios.create({ baseURL: BASE, timeout: 15000 });

export const api = {
  async analyze(text) {
    if (USE_MOCK) return mockResponse;
    try {
      const res = await http.post("/api/analyze", { text });
      return res.data;
    } catch (err) {
      console.warn("Backend unreachable, falling back to mock:", err.message);
      return mockResponse;
    }
  },

  async events() {
    if (USE_MOCK) return [];
    try {
      const res = await http.get("/api/events");
      return res.data.events;
    } catch {
      return [];
    }
  },
};