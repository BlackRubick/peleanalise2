import { z } from "zod";
import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

const schema = z.object({ refreshToken: z.string().optional() });

export default defineEventHandler(async (event) => {
  const auth = getAuthUser(event);
  const body = await readBody(event);
  const { refreshToken } = schema.parse(body);

  if (refreshToken) {
    await prisma.refreshToken.updateMany({
      where: { token: refreshToken, userId: auth.userId },
      data:  { isRevoked: true },
    });
  } else {
    // Revoke all sessions
    await prisma.refreshToken.updateMany({
      where: { userId: auth.userId, isRevoked: false },
      data:  { isRevoked: true },
    });
  }

  await auditLog(event, "LOGOUT", "users", auth.userId, auth.userId);
  return { message: "Sesión cerrada" };
});
