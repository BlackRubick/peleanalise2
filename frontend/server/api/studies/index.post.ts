import { z } from "zod";
import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

const schema = z.object({
  patientId:        z.string().uuid(),
  recordId:         z.string().uuid().optional(),
  lesionType:       z.enum(["MELANOMA","NEVUS","CARCINOMA_BASOCELULAR","CARCINOMA_ESPINOCELULAR","QUERATOSIS_ACTINCA","DERMATOFIBROMA","LESION_VASCULAR","OTRO"]).default("OTRO"),
  anatomicLocation: z.string().min(2).max(200),
  clinicalComments: z.string().max(2000).optional(),
  studyDate:        z.string().optional(),
});

export default defineEventHandler(async (event) => {
  const auth = getAuthUser(event);
  const body = await readBody(event);
  const data = schema.parse(body);

  const study = await prisma.study.create({
    data: {
      ...data,
      capturedById: auth.userId,
      studyDate:    data.studyDate ? new Date(data.studyDate) : new Date(),
    },
    include: {
      patient: { select: { firstName: true, lastName: true } },
    },
  });

  await auditLog(event, "CREATE", "studies", study.id, auth.userId, { patientId: data.patientId });
  return study;
});
