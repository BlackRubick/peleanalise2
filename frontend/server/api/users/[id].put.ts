import { z } from "zod";
import bcrypt from "bcryptjs";
import { prisma } from "../../utils/prisma";
import { requireRoles, getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

const schema = z.object({
  firstName: z.string().min(2).max(100).optional(),
  lastName:  z.string().min(2).max(100).optional(),
  role:      z.enum(["ADMIN", "DOCTOR", "CAPTURISTA"]).optional(),
  isActive:  z.boolean().optional(),
  password:  z.string().min(8).optional(),
});

export default defineEventHandler(async (event) => {
  requireRoles(event, "ADMIN");
  const auth = getAuthUser(event);
  const id   = getRouterParam(event, "id")!;
  const body = await readBody(event);
  const data = schema.parse(body);

  const updateData: Record<string, unknown> = { ...data };
  delete updateData.password;
  if (data.password) {
    updateData.password = await bcrypt.hash(data.password, 12);
  }

  const user = await prisma.user.update({
    where:  { id, deletedAt: null },
    data:   updateData,
    select: { id: true, email: true, firstName: true, lastName: true, role: true, isActive: true },
  });

  await auditLog(event, "UPDATE", "users", id, auth.userId);
  return user;
});
