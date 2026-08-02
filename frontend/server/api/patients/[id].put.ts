import { z } from "zod";
import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";

const schema = z.object({
  firstName:    z.string().min(2).max(100).optional(),
  lastName:     z.string().min(2).max(100).optional(),
  sex:          z.enum(["MASCULINO", "FEMENINO", "OTRO"]).optional(),
  birthDate:    z.string().regex(/^\d{4}-\d{2}-\d{2}$/).optional(),
  curp:         z.preprocess(v => v === "" ? undefined : v, z.string().length(18, "El CURP debe tener exactamente 18 caracteres").toUpperCase().optional()),
  phone:        z.string().max(20).optional(),
  email:        z.string().email().optional().or(z.literal("")),
  address:      z.string().max(500).optional(),
  observations: z.string().max(2000).optional(),
});

export default defineEventHandler(async (event) => {
  const auth = getAuthUser(event);
  const id   = getRouterParam(event, "id")!;
  const body = await readBody(event);
  const data = schema.parse(body);

  const update: Record<string, unknown> = { ...data };
  if (data.birthDate) update.birthDate = new Date(data.birthDate);
  if (data.email === "") update.email = null;

  const patient = await prisma.patient.update({
    where: { id, deletedAt: null },
    data:  update,
  });

  await auditLog(event, "UPDATE", "patients", id, auth.userId);
  return patient;
});
