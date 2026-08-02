import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware(async (to) => {
  const auth = useAuthStore();

  if (!auth.isAuthenticated) {
    const refreshToken = import.meta.client ? localStorage.getItem("refreshToken") : null;
    if (refreshToken) {
      try {
        await auth.refresh();
        await auth.fetchMe();
      } catch {
        auth.clear();
        return navigateTo("/auth/login");
      }
    } else {
      return navigateTo("/auth/login");
    }
  }
});
