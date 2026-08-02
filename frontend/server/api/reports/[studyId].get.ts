import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

export default defineEventHandler(async (event) => {
  const auth    = getAuthUser(event);
  const studyId = getRouterParam(event, "studyId")!;
  const config  = useRuntimeConfig();

  const study = await prisma.study.findFirst({
    where: { id: studyId, deletedAt: null },
    include: {
      patient:    true,
      capturedBy: { select: { firstName: true, lastName: true, role: true } },
      images:     true,
      analysis: {
        include: { abcde: true, prediction: true },
      },
    },
  });

  if (!study)          throw createError({ statusCode: 404, message: "Estudio no encontrado" });
  if (!study.analysis) throw createError({ statusCode: 400, message: "El estudio aún no ha sido analizado" });

  // Construir URLs absolutas para que Python las descargue
  const host = getRequestHeader(event, "host") ?? "localhost:3000";
  const baseUrl = `http://${host}`;
  const imageUrls: Record<string, string> = {};
  for (const img of study.images) {
    imageUrls[img.type] = `${baseUrl}${img.storagePath}`;
  }

  const pdfResponse = await $fetch<{ pdf_base64: string }>(
    `${config.pythonAiUrl}/report/generate`,
    {
      method:  "POST",
      body:    { study, image_urls: imageUrls },
      timeout: 30_000,
    }
  );

  await auditLog(event, "EXPORT", "studies", studyId, auth.userId);

  setResponseHeader(event, "Content-Type", "application/pdf");
  setResponseHeader(event, "Content-Disposition", `attachment; filename="reporte-${studyId.slice(0, 8)}.pdf"`);
  return Buffer.from(pdfResponse.pdf_base64, "base64");
});
