import { z } from "zod";
import { prisma } from "../../utils/prisma";

const querySchema = z.object({
  page:        z.coerce.number().min(1).default(1),
  limit:       z.coerce.number().min(1).max(100).default(15),
  patientId:   z.string().uuid().optional(),
  riskLevel:   z.enum(["BENIGNO", "SOSPECHOSO", "MALIGNO"]).optional(),
  isProcessed: z.coerce.boolean().optional(),
  search:      z.string().optional(),
});

export default defineEventHandler(async (event) => {
  const q    = await getValidatedQuery(event, querySchema.parse);
  const skip = (q.page - 1) * q.limit;

  // Full filter (used for table + total count)
  const where: Record<string, unknown> = { deletedAt: null };
  if (q.patientId)                 where.patientId   = q.patientId;
  if (q.riskLevel)                 where.riskLevel   = q.riskLevel;
  if (q.isProcessed !== undefined) where.isProcessed = q.isProcessed;

  const searchClause = q.search ? [
    { anatomicLocation: { contains: q.search } },
    { clinicalComments: { contains: q.search } },
    { patient: { firstName: { contains: q.search } } },
    { patient: { lastName:  { contains: q.search } } },
  ] : undefined;
  if (searchClause) where.OR = searchClause;

  // Stats filter: same as where but WITHOUT riskLevel, for accurate risk breakdown counts
  const statsWhere: Record<string, unknown> = { deletedAt: null };
  if (q.patientId)                 statsWhere.patientId   = q.patientId;
  if (q.isProcessed !== undefined) statsWhere.isProcessed = q.isProcessed;
  if (searchClause)                statsWhere.OR           = searchClause;

  const [studies, total, benigno, sospechoso, maligno] = await Promise.all([
    prisma.study.findMany({
      where,
      include: {
        patient:    { select: { id: true, firstName: true, lastName: true } },
        capturedBy: { select: { firstName: true, lastName: true } },
        images:     { where: { type: "ORIGINAL" }, take: 1 },
        analysis:   { include: { prediction: true, abcde: true } },
      },
      orderBy: { studyDate: "desc" },
      skip,
      take: q.limit,
    }),
    prisma.study.count({ where }),
    prisma.study.count({ where: { ...statsWhere, riskLevel: "BENIGNO" } }),
    prisma.study.count({ where: { ...statsWhere, riskLevel: "SOSPECHOSO" } }),
    prisma.study.count({ where: { ...statsWhere, riskLevel: "MALIGNO" } }),
  ]);

  return {
    data: studies,
    meta: {
      total, page: q.page, limit: q.limit, pages: Math.ceil(total / q.limit),
      benigno, sospechoso, maligno,
    },
  };
});
