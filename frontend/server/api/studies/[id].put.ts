import { z } from "zod";
import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

const schema = z.object({
  lesionType:       z.enum(["MELANOMA","NEVUS","CARCINOMA_BASOCELULAR","CARCINOMA_ESPINOCELULAR","QUERATOSIS_ACTINCA","DERMATOFIBROMA","LESION_VASCULAR","OTRO"]).optional(),
  anatomicLocation: z.string().min(2).max(200).optional(),
  clinicalComments: z.string().max(2000).optional().nullable(),
  studyDate:        z.string().optional(),
});

export default defineEventHandler(async (event) => {
  const auth = getAuthUser(event);
  const id   = getRouterParam(event, "id")!;
  const body = await readBody(event);
  const data = schema.parse(body);

  const update: Record<string, unknown> = { ...data };
  if (data.studyDate) update.studyDate = new Date(data.studyDate);

  const study = await prisma.study.update({
    where: { id, deletedAt: null },
    data:  update,
    include: {
      patient:   { select: { firstName: true, lastName: true } },
      capturedBy: { select: { firstName: true, lastName: true } },
    },
  });

  await auditLog(event, "UPDATE", "studies", id, auth.userId);
  return study;
});
