import { getRequestHeader, setResponseHeader } from "h3";
import { extractBearerToken, verifyAccessToken } from "../utils/jwt";

export default defineEventHandler(async (event) => {
  const url = getRequestURL(event).pathname;

  // Only protect /api/** except /api/auth/**
  if (!url.startsWith("/api/") || url.startsWith("/api/auth/")) return;

  const authHeader = getRequestHeader(event, "authorization");
  const token      = extractBearerToken(authHeader);

  if (!token) {
    throw createError({ statusCode: 401, message: "Token requerido" });
  }

  try {
    const payload = await verifyAccessToken(token);
    event.context.auth = {
      userId: payload.sub,
      email:  payload.email,
      role:   payload.role,
    };
  } catch {
    throw createError({ statusCode: 401, message: "Token inválido o expirado" });
  }
});
