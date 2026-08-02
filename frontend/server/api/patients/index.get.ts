import { z } from "zod";
import { prisma } from "../../utils/prisma";

const querySchema = z.object({
  page:   z.coerce.number().min(1).default(1),
  limit:  z.coerce.number().min(1).max(100).default(15),
  search: z.string().optional(),
  sex:    z.enum(["MASCULINO", "FEMENINO", "OTRO"]).optional(),
});

export default defineEventHandler(async (event) => {
  const q    = await getValidatedQuery(event, querySchema.parse);
  const skip = (q.page - 1) * q.limit;

  const where: Record<string, unknown> = { deletedAt: null };
  if (q.sex) where.sex = q.sex;
  if (q.search) {
    where.OR = [
      { firstName: { contains: q.search } },
      { lastName:  { contains: q.search } },
      { curp:      { contains: q.search } },
      { email:     { contains: q.search } },
      { phone:     { contains: q.search } },
    ];
  }

  const [patients, total] = await Promise.all([
    prisma.patient.findMany({
      where,
      select: {
        id: true, firstName: true, lastName: true, sex: true,
        birthDate: true, curp: true, phone: true, email: true,
        createdAt: true,
        _count: { select: { studies: true } },
      },
      orderBy: { createdAt: "desc" },
      skip,
      take: q.limit,
    }),
    prisma.patient.count({ where }),
  ]);

  return {
    data: patients,
    meta: { total, page: q.page, limit: q.limit, pages: Math.ceil(total / q.limit) },
  };
});
