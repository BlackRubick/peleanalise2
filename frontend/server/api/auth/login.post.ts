import { z } from "zod";
import bcrypt from "bcryptjs";
import { prisma } from "../../utils/prisma";
import { signAccessToken, signRefreshToken } from "../../utils/jwt";
import { auditLog } from "../../utils/audit";

const loginSchema = z.object({
  email:    z.string().email("Email inválido"),
  password: z.string().min(6, "Contraseña demasiado corta"),
});

export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const parsed = loginSchema.safeParse(body);

  if (!parsed.success) {
    throw createError({ statusCode: 422, message: parsed.error.errors[0].message });
  }

  const { email, password } = parsed.data;

  const user = await prisma.user.findFirst({
    where: { email, deletedAt: null, isActive: true },
  });

  if (!user || !(await bcrypt.compare(password, user.password))) {
    throw createError({ statusCode: 401, message: "Credenciales inválidas" });
  }

  const tokenPayload = { sub: user.id, email: user.email, role: user.role };
  const [accessToken, refreshToken] = await Promise.all([
    signAccessToken(tokenPayload),
    signRefreshToken(tokenPayload),
  ]);

  const expiresAt = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
  await prisma.refreshToken.create({
    data: { token: refreshToken, userId: user.id, expiresAt },
  });

  await prisma.user.update({
    where: { id: user.id },
    data: { lastLoginAt: new Date() },
  });

  await auditLog(event, "LOGIN", "users", user.id, user.id);

  return {
    accessToken,
    refreshToken,
    user: {
      id:        user.id,
      email:     user.email,
      firstName: user.firstName,
      lastName:  user.lastName,
      role:      user.role,
    },
  };
});
