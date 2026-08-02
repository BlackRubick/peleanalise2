import { prisma } from "../../utils/prisma";
import { requireRoles, getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

export default defineEventHandler(async (event) => {
  requireRoles(event, "ADMIN", "DOCTOR");
  const auth = getAuthUser(event);
  const id   = getRouterParam(event, "id")!;

  await prisma.study.update({ where: { id }, data: { deletedAt: new Date() } });
  await auditLog(event, "DELETE", "studies", id, auth.userId);
  return { message: "Estudio eliminado" };
});
