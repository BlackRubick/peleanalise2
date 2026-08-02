import { SignJWT, jwtVerify, type JWTPayload } from "jose";

export interface TokenPayload extends JWTPayload {
  sub: string;
  email: string;
  role: string;
  type: "access" | "refresh";
}

function getSecrets() {
  const config = useRuntimeConfig();
  return {
    access:  new TextEncoder().encode(config.jwtSecret),
    refresh: new TextEncoder().encode(config.jwtRefreshSecret),
  };
}

export async function signAccessToken(payload: Omit<TokenPayload, "type" | "iat" | "exp">) {
  const { access } = getSecrets();
  return new SignJWT({ ...payload, type: "access" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("15m")
    .sign(access);
}

export async function signRefreshToken(payload: Omit<TokenPayload, "type" | "iat" | "exp">) {
  const { refresh } = getSecrets();
  return new SignJWT({ ...payload, type: "refresh" })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(refresh);
}

export async function verifyAccessToken(token: string): Promise<TokenPayload> {
  const { access } = getSecrets();
  const { payload } = await jwtVerify(token, access);
  return payload as TokenPayload;
}

export async function verifyRefreshToken(token: string): Promise<TokenPayload> {
  const { refresh } = getSecrets();
  const { payload } = await jwtVerify(token, refresh);
  return payload as TokenPayload;
}

export function extractBearerToken(authHeader: string | undefined): string | null {
  if (!authHeader?.startsWith("Bearer ")) return null;
  return authHeader.slice(7);
}
