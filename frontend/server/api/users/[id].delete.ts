import { prisma } from "../../utils/prisma";
import { requireRoles, getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

export default defineEventHandler(async (event) => {
  requireRoles(event, "ADMIN");
  const auth = getAuthUser(event);
  const id   = getRouterParam(event, "id")!;

  if (id === auth.userId) {
    throw createError({ statusCode: 400, message: "No puedes eliminar tu propia cuenta" });
  }

  await prisma.user.update({ where: { id }, data: { deletedAt: new Date() } });
  await auditLog(event, "DELETE", "users", id, auth.userId);
  return { message: "Usuario eliminado" };
});
