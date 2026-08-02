import { defineStore } from "pinia";

interface AuthUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: "ADMIN" | "DOCTOR" | "CAPTURISTA";
  avatarUrl?: string;
}

interface AuthState {
  user:         AuthUser | null;
  accessToken:  string | null;
  refreshToken: string | null;
  loading:      boolean;
}

export const useAuthStore = defineStore("auth", {
  state: (): AuthState => ({
    user:         null,
    accessToken:  null,
    refreshToken: null,
    loading:      false,
  }),

  getters: {
    isAuthenticated: (s) => !!s.user && !!s.accessToken,
    isAdmin:         (s) => s.user?.role === "ADMIN",
    isDoctor:        (s) => s.user?.role === "DOCTOR",
    fullName:        (s) => s.user ? `${s.user.firstName} ${s.user.lastName}` : "",
  },

  actions: {
    async login(email: string, password: string) {
      this.loading = true;
      try {
        const res = await $fetch<{
          accessToken:  string;
          refreshToken: string;
          user:         AuthUser;
        }>("/api/auth/login", {
          method: "POST",
          body:   { email, password },
        });

        this.accessToken  = res.accessToken;
        this.refreshToken = res.refreshToken;
        this.user         = res.user;

        if (import.meta.client) {
          localStorage.setItem("refreshToken", res.refreshToken);
        }
      } finally {
        this.loading = false;
      }
    },

    async logout() {
      try {
        await $fetch("/api/auth/logout", {
          method:  "POST",
          headers: { Authorization: `Bearer ${this.accessToken}` },
          body:    { refreshToken: this.refreshToken },
        });
      } catch {}
      this.clear();
      await navigateTo("/auth/login");
    },

    async refresh() {
      const stored = import.meta.client ? localStorage.getItem("refreshToken") : null;
      if (!stored) throw new Error("No refresh token");

      const res = await $fetch<{ accessToken: string; refreshToken: string }>(
        "/api/auth/refresh",
        { method: "POST", body: { refreshToken: stored } }
      );
      this.accessToken  = res.accessToken;
      this.refreshToken = res.refreshToken;
      localStorage.setItem("refreshToken", res.refreshToken);
    },

    async fetchMe() {
      const user = await $fetch<AuthUser>("/api/auth/me", {
        headers: { Authorization: `Bearer ${this.accessToken}` },
      });
      this.user = user;
    },

    clear() {
      this.user         = null;
      this.accessToken  = null;
      this.refreshToken = null;
      if (import.meta.client) localStorage.removeItem("refreshToken");
    },
  },

  persist: {
    storage: import.meta.client ? localStorage : undefined,
    paths:   ["accessToken", "refreshToken", "user"],
  },
});
