import { z } from "zod";
import { prisma } from "../../utils/prisma";
import { verifyRefreshToken, signAccessToken, signRefreshToken } from "../../utils/jwt";

const schema = z.object({ refreshToken: z.string() });

export default defineEventHandler(async (event) => {
  const body   = await readBody(event);
  const parsed = schema.safeParse(body);
  if (!parsed.success) throw createError({ statusCode: 422, message: "Token requerido" });

  const { refreshToken } = parsed.data;

  const stored = await prisma.refreshToken.findUnique({ where: { token: refreshToken } });
  if (!stored || stored.isRevoked || stored.expiresAt < new Date()) {
    throw createError({ statusCode: 401, message: "Refresh token inválido" });
  }

  let payload;
  try {
    payload = await verifyRefreshToken(refreshToken);
  } catch {
    throw createError({ statusCode: 401, message: "Refresh token expirado" });
  }

  // Rotate: revoke old, issue new pair
  await prisma.refreshToken.update({ where: { id: stored.id }, data: { isRevoked: true } });

  const user = await prisma.user.findUnique({ where: { id: payload.sub } });
  if (!user || !user.isActive) throw createError({ statusCode: 401, message: "Usuario inactivo" });

  const tokenPayload = { sub: user.id, email: user.email, role: user.role };
  const [accessToken, newRefresh] = await Promise.all([
    signAccessToken(tokenPayload),
    signRefreshToken(tokenPayload),
  ]);

  await prisma.refreshToken.create({
    data: {
      token:     newRefresh,
      userId:    user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
    },
  });

  return { accessToken, refreshToken: newRefresh };
});
