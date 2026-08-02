import { z } from "zod";
import { prisma } from "../../utils/prisma";
import { requireRoles } from "../../utils/rbac";

const querySchema = z.object({
  page:   z.coerce.number().min(1).default(1),
  limit:  z.coerce.number().min(1).max(100).default(15),
  search: z.string().optional(),
  role:   z.enum(["ADMIN", "DOCTOR", "CAPTURISTA"]).optional(),
});

export default defineEventHandler(async (event) => {
  requireRoles(event, "ADMIN");

  const q = await getValidatedQuery(event, querySchema.parse);
  const skip = (q.page - 1) * q.limit;

  const where: Record<string, unknown> = { deletedAt: null };
  if (q.role) where.role = q.role;
  if (q.search) {
    where.OR = [
      { firstName: { contains: q.search } },
      { lastName:  { contains: q.search } },
      { email:     { contains: q.search } },
    ];
  }

  const [users, total] = await Promise.all([
    prisma.user.findMany({
      where,
      select: {
        id: true, email: true, firstName: true, lastName: true,
        role: true, isActive: true, lastLoginAt: true, createdAt: true,
      },
      orderBy: { createdAt: "desc" },
      skip,
      take: q.limit,
    }),
    prisma.user.count({ where }),
  ]);

  return {
    data: users,
    meta: { total, page: q.page, limit: q.limit, pages: Math.ceil(total / q.limit) },
  };
});
