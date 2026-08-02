import { z } from "zod";
import bcrypt from "bcryptjs";
import { prisma } from "../../utils/prisma";
import { requireRoles, getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";
import { handlePrismaError } from "../../utils/errors";

const schema = z.object({
  email:     z.string().email(),
  password:  z.string().min(8, "Mínimo 8 caracteres"),
  firstName: z.string().min(2).max(100),
  lastName:  z.string().min(2).max(100),
  role:      z.enum(["ADMIN", "DOCTOR", "CAPTURISTA"]),
});

export default defineEventHandler(async (event) => {
  requireRoles(event, "ADMIN");
  const auth = getAuthUser(event);
  const body = await readBody(event);
  const data = schema.parse(body);

  try {
    const hash = await bcrypt.hash(data.password, 12);
    const user = await prisma.user.create({
      data:   { ...data, password: hash },
      select: { id: true, email: true, firstName: true, lastName: true, role: true, isActive: true },
    });

    await auditLog(event, "CREATE", "users", user.id, auth.userId, { email: user.email });
    return user;
  } catch (err) {
    throw handlePrismaError(err);
  }
});
