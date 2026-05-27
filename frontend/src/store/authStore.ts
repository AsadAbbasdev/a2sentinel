import { create } from "zustand";

interface User {
  id: string;
  email: string;
  full_name: string | null;
  plan: string;
  scans_used: number;
  scans_limit: number;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  loadFromStorage: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  setAuth: (user, token) => {
    localStorage.setItem("a2s_token", token);
    localStorage.setItem("a2s_user", JSON.stringify(user));
    set({ user, token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem("a2s_token");
    localStorage.removeItem("a2s_user");
    set({ user: null, token: null, isAuthenticated: false });
  },

  loadFromStorage: () => {
    const token = localStorage.getItem("a2s_token");
    const userStr = localStorage.getItem("a2s_user");
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({ user, token, isAuthenticated: true });
      } catch {
        localStorage.removeItem("a2s_token");
        localStorage.removeItem("a2s_user");
      }
    }
  },
}));
