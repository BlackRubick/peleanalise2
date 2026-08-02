import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";

export default defineEventHandler(async (event) => {
  getAuthUser(event);
  const id = getRouterParam(event, "id")!;

  const patient = await prisma.patient.findFirst({
    where: { id, deletedAt: null },
    include: {
      medicalRecords: {
        where:   { deletedAt: null },
        include: { doctor: { select: { firstName: true, lastName: true } } },
        orderBy: { consultationDate: "desc" },
      },
      studies: {
        where:   { deletedAt: null },
        include: {
          images:  { where: { type: "ORIGINAL" }, take: 1 },
          analysis: { include: { prediction: true } },
        },
        orderBy: { studyDate: "desc" },
      },
    },
  });

  if (!patient) throw createError({ statusCode: 404, message: "Paciente no encontrado" });
  return patient;
});
