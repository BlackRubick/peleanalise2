import { readFile } from "fs/promises";
import { join }     from "path";
import { prisma }   from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

export default defineEventHandler(async (event) => {
  const auth    = getAuthUser(event);
  const studyId = getRouterParam(event, "studyId")!;
  const config  = useRuntimeConfig();

  const study = await prisma.study.findFirst({
    where:   { id: studyId, deletedAt: null },
    include: { images: { where: { type: "ORIGINAL" }, take: 1 } },
  });

  if (!study) throw createError({ statusCode: 404, message: "Estudio no encontrado" });
  if (!study.images.length) throw createError({ statusCode: 400, message: "El estudio no tiene imágenes" });

  const originalImage = study.images[0];
  // Lee el archivo del disco y mándalo como base64 — evita problemas de servir estáticos en dev
  const filePath    = join(process.cwd(), "public", originalImage.storagePath);
  const imageBuffer = await readFile(filePath);
  const imageBase64 = imageBuffer.toString("base64");

  type AIResponse = {
    prediccion: string;
    probabilidad: number;
    prob_benigno: number;
    prob_sospechoso: number;
    prob_maligno: number;
    model_version: string;
    inference_time_ms: number;
    abcde: {
      asymmetry: { score: number; h: number; v: number; hu_moments: number[] };
      border:    { score: number; perimeter: number; area: number; compactness: number; rugosity: number };
      color:     { score: number; variance: number; mean_r: number; mean_g: number; mean_b: number; std_r: number; std_g: number; std_b: number; histogram: number[] };
      diameter:  { score: number; diameter_px: number; diameter_mm: number; pixel_per_mm: number };
      total_score: number;
    };
    processed_images: { cleaned_path?: string; mask_path?: string; gradcam_path?: string };
  };

  let aiResponse: AIResponse;
  try {
    aiResponse = await $fetch<AIResponse>(
      `${config.pythonAiUrl}/analyze`,
      { method: "POST", body: { image_base64: imageBase64, study_id: studyId }, timeout: 60_000 }
    );
  } catch (err) {
    console.error("[AI Service]", err);
    throw createError({ statusCode: 502, message: "Error al comunicarse con el servicio de IA" });
  }

  const analysis = await prisma.$transaction(async (tx) => {
    const a = await tx.analysis.upsert({
      where:  { studyId },
      create: { studyId },
      update: { processedAt: new Date() },
    });

    await tx.aBCDEMetric.upsert({
      where:  { analysisId: a.id },
      create: {
        analysisId:    a.id,
        asymmetryScore: aiResponse.abcde.asymmetry.score,
        asymmetryH:     aiResponse.abcde.asymmetry.h,
        asymmetryV:     aiResponse.abcde.asymmetry.v,
        huMoments:      aiResponse.abcde.asymmetry.hu_moments,
        borderScore:    aiResponse.abcde.border.score,
        perimeter:      aiResponse.abcde.border.perimeter,
        area:           aiResponse.abcde.border.area,
        compactness:    aiResponse.abcde.border.compactness,
        rugosity:       aiResponse.abcde.border.rugosity,
        colorScore:     aiResponse.abcde.color.score,
        colorVariance:  aiResponse.abcde.color.variance,
        meanR:          aiResponse.abcde.color.mean_r,
        meanG:          aiResponse.abcde.color.mean_g,
        meanB:          aiResponse.abcde.color.mean_b,
        stdR:           aiResponse.abcde.color.std_r,
        stdG:           aiResponse.abcde.color.std_g,
        stdB:           aiResponse.abcde.color.std_b,
        colorHistogram: aiResponse.abcde.color.histogram,
        diameterScore:  aiResponse.abcde.diameter.score,
        diameterPx:     aiResponse.abcde.diameter.diameter_px,
        diameterMm:     aiResponse.abcde.diameter.diameter_mm,
        pixelPerMm:     aiResponse.abcde.diameter.pixel_per_mm,
        totalScore:     aiResponse.abcde.total_score,
      },
      update: {
        asymmetryScore: aiResponse.abcde.asymmetry.score,
        totalScore:     aiResponse.abcde.total_score,
      },
    });

    const riskMap: Record<string, "BENIGNO" | "SOSPECHOSO" | "MALIGNO"> = {
      Benigno: "BENIGNO", BENIGNO: "BENIGNO",
      Sospechoso: "SOSPECHOSO", SOSPECHOSO: "SOSPECHOSO",
      Maligno: "MALIGNO", MALIGNO: "MALIGNO",
    };
    const riskLevel = riskMap[aiResponse.prediccion] ?? "SOSPECHOSO";

    const lesionTypeMap: Record<"BENIGNO" | "SOSPECHOSO" | "MALIGNO", string> = {
      BENIGNO:    "NEVUS",
      SOSPECHOSO: "CARCINOMA_BASOCELULAR",
      MALIGNO:    "MELANOMA",
    };

    await tx.prediction.upsert({
      where:  { analysisId: a.id },
      create: {
        analysisId:      a.id,
        prediction:      riskLevel,
        probability:     aiResponse.probabilidad,
        probBenigno:     aiResponse.prob_benigno,
        probSospechoso:  aiResponse.prob_sospechoso,
        probMaligno:     aiResponse.prob_maligno,
        modelVersion:    aiResponse.model_version,
        inferenceTimeMs: aiResponse.inference_time_ms,
      },
      update: {
        prediction:  riskLevel,
        probability: aiResponse.probabilidad,
      },
    });

    await tx.study.update({
      where: { id: studyId },
      data:  { riskLevel, isProcessed: true, lesionType: lesionTypeMap[riskLevel] },
    });

    return a;
  });

  await auditLog(event, "ANALYZE", "studies", studyId, auth.userId);
  return {
    analysisId:  analysis.id,
    riskLevel:   aiResponse.prediccion,
    probability: aiResponse.probabilidad,
    abcde:       aiResponse.abcde,
  };
});
