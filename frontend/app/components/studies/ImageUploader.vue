<template>
  <div
    class="border-2 border-dashed border-gray-200 rounded-xl p-4 text-center hover:border-brand-400 transition-colors cursor-pointer"
    :class="{ 'border-brand-500 bg-brand-50': dragOver }"
    @dragover.prevent="dragOver = true"
    @dragleave="dragOver = false"
    @drop.prevent="onDrop"
    @click="fileInput?.click()"
  >
    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="hidden"
      @change="onFileChange"
    />
    <div v-if="!uploading">
      <svg class="w-7 h-7 text-gray-300 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
      </svg>
      <p class="text-sm text-gray-500 font-medium">Arrastra una imagen o haz clic</p>
      <p class="text-xs text-gray-400 mt-1">JPEG, PNG o WebP · máx. 20 MB</p>
    </div>
    <div v-else class="flex items-center justify-center gap-2 text-sm text-brand-600">
      <span class="w-4 h-4 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      Subiendo imagen...
    </div>
  </div>
</template>

<script setup lang="ts">
import { useNotification } from "~/composables/useNotification";
import { useAuthStore }    from "~/stores/auth";

const props = defineProps<{ studyId: string }>();
const emit  = defineEmits(["uploaded"]);

const notif     = useNotification();
const auth      = useAuthStore();
const fileInput = ref<HTMLInputElement | null>(null);
const dragOver  = ref(false);
const uploading = ref(false);

async function doUpload(fd: FormData): Promise<void> {
  if (!auth.accessToken) await auth.refresh();
  await $fetch("/api/images/upload", {
    method:  "POST",
    body:    fd,
    headers: { Authorization: `Bearer ${auth.accessToken}` },
  });
}

async function uploadFile(file: File) {
  if (file.size > 20 * 1024 * 1024) {
    notif.error("Imagen demasiado grande", "Máximo 20MB");
    return;
  }
  uploading.value = true;
  try {
    const fd = new FormData();
    fd.append("studyId", props.studyId);
    fd.append("image", file);
    try {
      await doUpload(fd);
    } catch (err: unknown) {
      const e = err as { status?: number; statusCode?: number };
      if ((e?.status ?? e?.statusCode) === 401) {
        await auth.refresh();
        await doUpload(fd);
      } else {
        throw err;
      }
    }
    emit("uploaded");
    notif.success("Imagen subida correctamente");
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } };
    notif.error("Error al subir la imagen", e?.data?.message ?? "Intenta de nuevo");
  } finally {
    uploading.value = false;
  }
}

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (file) uploadFile(file);
}

function onDrop(e: DragEvent) {
  dragOver.value = false;
  const file = e.dataTransfer?.files?.[0];
  if (file) uploadFile(file);
}
</script>
