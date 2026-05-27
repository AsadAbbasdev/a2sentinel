import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Auto attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("a2s_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally — logout
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("a2s_token");
      localStorage.removeItem("a2s_user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────────────────
export const authAPI = {
  register: (data: { email: string; password: string; full_name?: string; company?: string }) =>
    api.post("/api/auth/register", data),

  login: (data: { email: string; password: string }) =>
    api.post("/api/auth/login", data),
};

// ─── Scan ────────────────────────────────────────────────────────
export const scanAPI = {
  scan: (data: {
    code: string;
    language?: string;
    include_simulation: boolean;
    include_fix: boolean;
  }) => api.post("/api/scan", data),

  simulate: (data: { code: string; language?: string }) =>
    api.post("/api/scan/simulate", data),

  fix: (data: { code: string; language?: string }) =>
    api.post("/api/scan/fix", data),

  history: (page = 1, per_page = 20) =>
    api.get(`/api/scan/history?page=${page}&per_page=${per_page}`),

  getScan: (scan_id: string) => api.get(`/api/scan/${scan_id}`),
  
  guestScan: (data: { code: string; language?: string }) =>
    api.post("/api/scan/guest", {
      ...data,
      include_simulation: false,
      include_fix: false,
    }),
};

// ─── User ────────────────────────────────────────────────────────
export const userAPI = {
  me: () => api.get("/api/user/me"),
  usage: () => api.get("/api/user/usage"),
};
