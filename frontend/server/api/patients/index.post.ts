import { z } from "zod";
import { prisma } from "../../utils/prisma";
import { getAuthUser } from "../../utils/rbac";
import { auditLog } from "../../utils/audit";
import { handlePrismaError } from "../../utils/errors";

const schema = z.object({
  firstName:    z.string().min(2).max(100),
  lastName:     z.string().min(2).max(100),
  sex:          z.enum(["MASCULINO", "FEMENINO", "OTRO"]),
  birthDate:    z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Formato: YYYY-MM-DD"),
  curp:         z.preprocess(v => v === "" ? undefined : v, z.string().length(18, "El CURP debe tener exactamente 18 caracteres").toUpperCase().optional()),
  phone:        z.string().max(20).optional(),
  email:        z.string().email().optional().or(z.literal("")),
  address:      z.string().max(500).optional(),
  observations: z.string().max(2000).optional(),
});

export default defineEventHandler(async (event) => {
  const auth = getAuthUser(event);
  const body = await readBody(event);
  const data = schema.parse(body);

  try {
    const patient = await prisma.patient.create({
      data: { ...data, birthDate: new Date(data.birthDate), email: data.email || null },
    });
    await auditLog(event, "CREATE", "patients", patient.id, auth.userId);
    return patient;
  } catch (err) {
    throw handlePrismaError(err);
  }
});
