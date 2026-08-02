import { writeFile, mkdir } from "fs/promises";
import { existsSync } from "fs";
import { join } from "path";
import { v4 as uuidv4 } from "uuid";

const UPLOADS_DIR = join(process.cwd(), "public", "uploads");

export async function saveFile(
  buffer: Buffer,
  originalName: string,
  folder = "images"
): Promise<{ path: string; filename: string; publicUrl: string }> {
  const dir = join(UPLOADS_DIR, folder);
  if (!existsSync(dir)) await mkdir(dir, { recursive: true });

  const ext      = originalName.split(".").pop() ?? "jpg";
  const filename = `${uuidv4()}.${ext}`;
  const filePath = join(dir, filename);

  await writeFile(filePath, buffer);

  const publicUrl = `/uploads/${folder}/${filename}`;
  return { path: filePath, filename, publicUrl };
}

export function getPublicUrl(storagePath: string): string {
  // storagePath guardado en DB es relativo: "uploads/images/uuid.jpg"
  return `/${storagePath}`;
}
