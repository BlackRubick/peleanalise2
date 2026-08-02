import type { H3Event } from "h3";
import { getRequestHeader } from "h3";
import { prisma } from "./prisma";
import type { AuditAction } from "@prisma/client";

export async function auditLog(
  event: H3Event,
  action: AuditAction,
  resource: string,
  resourceId?: string,
  userId?: string,
  metadata?: Record<string, unknown>
) {
  try {
    const ip        = getRequestHeader(event, "x-forwarded-for")
      ?? getRequestHeader(event, "x-real-ip")
      ?? event.node.req.socket.remoteAddress;
    const userAgent = getRequestHeader(event, "user-agent");

    await prisma.auditLog.create({
      data: {
        userId:     userId ?? null,
        action,
        resource,
        resourceId: resourceId ?? null,
        metadata:   metadata ?? null,
        ipAddress:  ip?.split(",")[0]?.trim() ?? null,
        userAgent:  userAgent ?? null,
      },
    });
  } catch {
    // Audit failures must never break the main flow
  }
}
