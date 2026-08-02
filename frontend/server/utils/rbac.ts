import type { H3Event } from "h3";
import type { RoleType } from "@prisma/client";

export function requireRoles(event: H3Event, ...roles: RoleType[]) {
  const auth = event.context.auth;
  if (!auth) throw createError({ statusCode: 401, message: "No autenticado" });
  if (!roles.includes(auth.role as RoleType)) {
    throw createError({ statusCode: 403, message: "Sin permisos para esta acción" });
  }
}

export function getAuthUser(event: H3Event) {
  const auth = event.context.auth;
  if (!auth) throw createError({ statusCode: 401, message: "No autenticado" });
  return auth as { userId: string; email: string; role: string };
}
