<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="relative">
          <input v-model="search" type="text" class="input pl-9 w-64" placeholder="Buscar estudio..." @input="debouncedFetch" />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <select v-model="riskFilter" class="input w-40" @change="fetchPage(1)">
          <option value="">Todos los riesgos</option>
          <option value="BENIGNO">Benigno</option>
          <option value="SOSPECHOSO">Sospechoso</option>
          <option value="MALIGNO">Maligno</option>
        </select>
      </div>
      <NuxtLink to="/studies/new" class="btn-primary">+ Nuevo estudio</NuxtLink>
    </div>

    <div class="card">
      <div class="table-wrapper border-0 rounded-none">
        <table>
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Fecha</th>
              <th>Tipo de lesión</th>
              <th>Localización</th>
              <th>Riesgo</th>
              <th>Estado</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="7" class="py-10 text-center text-gray-400">Cargando...</td></tr>
            <tr v-else-if="!studies.length"><td colspan="7" class="py-10 text-center text-gray-400">Sin estudios</td></tr>
            <tr v-for="s in studies" :key="s.id">
              <td class="font-medium">{{ s.patient.firstName }} {{ s.patient.lastName }}</td>
              <td class="whitespace-nowrap">{{ formatDate(s.studyDate) }}</td>
              <td>{{ s.lesionType }}</td>
              <td class="text-gray-600">{{ s.anatomicLocation }}</td>
              <td><UiBadgeRisk :risk="s.riskLevel" /></td>
              <td>
                <span v-if="s.isProcessed" class="badge bg-emerald-50 text-emerald-700">Procesado</span>
                <span v-else class="badge bg-gray-100 text-gray-500">Pendiente</span>
              </td>
              <td class="text-right">
                <div class="flex items-center justify-end gap-2">
                  <NuxtLink :to="`/studies/${s.id}`" class="btn btn-ghost btn-sm">Ver</NuxtLink>
                  <button
                    v-if="can('patients:delete')"
                    class="btn btn-ghost btn-sm text-red-500"
                    @click="askDelete(s)"
                  >Eliminar</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="px-4 border-t border-gray-100">
        <UiPagination :page="meta.page" :pages="meta.pages" :total="meta.total" :limit="meta.limit" @change="fetchPage" />
      </div>
    </div>

    <!-- Confirm delete modal -->
    <UiModal v-model="deleteModal" title="Eliminar estudio" size="sm">
      <p class="text-sm text-gray-600">
        ¿Eliminar el estudio de <strong>{{ deletingStudy?.patient.firstName }} {{ deletingStudy?.patient.lastName }}</strong>?
        Esta acción no se puede deshacer.
      </p>
      <template #footer>
        <button class="btn-secondary" @click="deleteModal = false">Cancelar</button>
        <button class="btn-danger" :disabled="deleting" @click="doDelete">
          {{ deleting ? 'Eliminando...' : 'Eliminar' }}
        </button>
      </template>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn }   from "@vueuse/core";
import { useApiFetch }     from "~/composables/useApiFetch";
import { useNotification } from "~/composables/useNotification";
import { useRBAC }         from "~/composables/useRBAC";

definePageMeta({ title: "Estudios", middleware: "auth" });

type Study = {
  id: string; studyDate: string; lesionType: string; anatomicLocation: string
  riskLevel: string | null; isProcessed: boolean
  patient: { firstName: string; lastName: string }
}

const notif   = useNotification();
const { can } = useRBAC();

const search     = ref("");
const riskFilter = ref("");
const loading    = ref(false);
const studies    = ref<Study[]>([]);
const meta       = ref({ page: 1, pages: 1, total: 0, limit: 15 });

const deleteModal    = ref(false);
const deletingStudy  = ref<Study | null>(null);
const deleting       = ref(false);

const debouncedFetch = useDebounceFn(() => fetchPage(1), 400);

async function fetchPage(page: number) {
  loading.value = true;
  try {
    const res = await useApiFetch<{ data: Study[]; meta: typeof meta.value }>("/api/studies", {
      query: { page, search: search.value || undefined, riskLevel: riskFilter.value || undefined },
    });
    studies.value = res.data;
    meta.value    = res.meta;
  } finally {
    loading.value = false;
  }
}

function askDelete(s: Study) {
  deletingStudy.value = s;
  deleteModal.value   = true;
}

async function doDelete() {
  if (!deletingStudy.value) return;
  deleting.value = true;
  try {
    await useApiFetch(`/api/studies/${deletingStudy.value.id}`, { method: "DELETE" });
    notif.success("Estudio eliminado");
    deleteModal.value = false;
    fetchPage(meta.value.page);
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } };
    notif.error("Error al eliminar", e?.data?.message);
  } finally {
    deleting.value = false;
  }
}

function formatDate(d: string) {
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(new Date(d));
}

onMounted(() => fetchPage(1));
</script>
