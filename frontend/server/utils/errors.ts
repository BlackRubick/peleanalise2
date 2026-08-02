import { H3Error, createError } from "h3";

export const errors = {
  unauthorized:  () => createError({ statusCode: 401, message: "No autenticado" }),
  forbidden:     () => createError({ statusCode: 403, message: "Sin permisos" }),
  notFound:      (r = "Recurso") => createError({ statusCode: 404, message: `${r} no encontrado` }),
  conflict:      (m: string) => createError({ statusCode: 409, message: m }),
  badRequest:    (m: string) => createError({ statusCode: 400, message: m }),
  internal:      (m = "Error interno del servidor") => createError({ statusCode: 500, message: m }),
  validation:    (m: string) => createError({ statusCode: 422, message: m }),
};

export function handlePrismaError(err: unknown): H3Error {
  const e = err as { code?: string; meta?: { target?: string[] } };
  if (e?.code === "P2002") {
    const field = e.meta?.target?.[0] ?? "campo";
    return errors.conflict(`El ${field} ya existe`);
  }
  if (e?.code === "P2025") {
    return errors.notFound();
  }
  console.error("[Prisma]", err);
  return errors.internal();
}
