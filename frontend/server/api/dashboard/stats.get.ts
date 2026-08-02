import { prisma } from "../../utils/prisma";

export default defineEventHandler(async (event) => {
  const [
    totalPatients,
    totalStudies,
    benigno,
    sospechoso,
    maligno,
    recentStudies,
    monthlyData,
  ] = await Promise.all([
    prisma.patient.count({ where: { deletedAt: null } }),
    prisma.study.count({ where: { deletedAt: null } }),
    prisma.study.count({ where: { riskLevel: "BENIGNO",    deletedAt: null } }),
    prisma.study.count({ where: { riskLevel: "SOSPECHOSO", deletedAt: null } }),
    prisma.study.count({ where: { riskLevel: "MALIGNO",    deletedAt: null } }),
    prisma.study.findMany({
      where:   { deletedAt: null },
      include: {
        patient:  { select: { firstName: true, lastName: true } },
        images:   { where: { type: "ORIGINAL" }, take: 1 },
        analysis: { include: { prediction: true } },
      },
      orderBy: { studyDate: "desc" },
      take: 8,
    }),
    // Last 12 months grouped by month
    prisma.$queryRaw<Array<{ month: string; count: bigint; risk: string }>>`
      SELECT
        DATE_FORMAT(studyDate, '%Y-%m') AS month,
        riskLevel AS risk,
        COUNT(*) AS count
      FROM studies
      WHERE deletedAt IS NULL
        AND studyDate >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
      GROUP BY month, riskLevel
      ORDER BY month ASC
    `,
  ]);

  return {
    stats: {
      totalPatients,
      totalStudies,
      benigno,
      sospechoso,
      maligno,
      pendingAnalysis: totalStudies - benigno - sospechoso - maligno,
    },
    recentStudies,
    monthly: monthlyData.map((r) => ({ ...r, count: Number(r.count) })),
  };
});
