import { PrismaClient } from "@prisma/client";

// Singleton para evitar múltiples instancias en hot-reload de desarrollo
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log: process.env.NODE_ENV === "development"
      ? ["query", "warn", "error"]
      : ["warn", "error"],
  });

if (process.env.NODE_ENV !== "production") {
  globalForPrisma.prisma = prisma;
}
