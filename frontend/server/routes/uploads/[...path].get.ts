import { readFile } from "fs/promises";
import { join, extname, normalize } from "path";

const MIME: Record<string, string> = {
  ".jpg":  "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png":  "image/png",
  ".webp": "image/webp",
  ".gif":  "image/gif",
};

export default defineEventHandler(async (event) => {
  const param    = getRouterParam(event, "path") ?? "";
  // Prevent path traversal
  const safe     = normalize(param).replace(/^(\.\.(\/|\\|$))+/, "");
  const filePath = join(process.cwd(), "public", "uploads", ...safe.split("/"));

  try {
    const buffer      = await readFile(filePath);
    const contentType = MIME[extname(filePath).toLowerCase()] ?? "application/octet-stream";
    setHeader(event, "Content-Type", contentType);
    setHeader(event, "Cache-Control", "no-cache");
    return buffer;
  } catch {
    throw createError({ statusCode: 404, message: "Imagen no encontrada" });
  }
});
