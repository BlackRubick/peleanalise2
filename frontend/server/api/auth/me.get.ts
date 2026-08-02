import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";

export default defineEventHandler(async (event) => {
  const auth = getAuthUser(event);
  const user = await prisma.user.findUnique({
    where:  { id: auth.userId },
    select: { id: true, email: true, firstName: true, lastName: true, role: true, avatarUrl: true, lastLoginAt: true },
  });
  if (!user) throw createError({ statusCode: 404, message: "Usuario no encontrado" });
  return user;
});
