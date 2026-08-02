import { prisma } from "../../utils/prisma";

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, "id")!;

  const study = await prisma.study.findFirst({
    where: { id, deletedAt: null },
    include: {
      patient:    true,
      capturedBy: { select: { firstName: true, lastName: true, role: true } },
      images:     true,
      analysis: {
        include: {
          abcde:      true,
          prediction: true,
        },
      },
    },
  });

  if (!study) throw createError({ statusCode: 404, message: "Estudio no encontrado" });

  // storagePath ya es una URL pública (/uploads/...) — no requiere presigned URL
  return study;
});
