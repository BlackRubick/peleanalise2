import { useAuthStore } from "~/stores/auth";

export function useRBAC() {
  const auth = useAuthStore();

  const can = (action: string): boolean => {
    const role = auth.user?.role;
    const perms: Record<string, string[]> = {
      "users:manage":    ["ADMIN"],
      "patients:delete": ["ADMIN", "DOCTOR"],
      "studies:create":  ["ADMIN", "DOCTOR", "CAPTURISTA"],
      "analysis:run":    ["ADMIN", "DOCTOR", "CAPTURISTA"],
      "reports:export":  ["ADMIN", "DOCTOR"],
    };
    return !!role && (perms[action]?.includes(role) ?? false);
  };

  return { can };
}
