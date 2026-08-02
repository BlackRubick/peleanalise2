<template>
  <div class="space-y-4">
    <!-- Toolbar -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="relative">
          <input v-model="search" type="text" class="input pl-9 w-64" placeholder="Buscar paciente..." @input="debouncedFetch" />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
        </div>
        <select v-model="sexFilter" class="input w-40" @change="fetchPage(1)">
          <option value="">Todos</option>
          <option value="MASCULINO">Masculino</option>
          <option value="FEMENINO">Femenino</option>
          <option value="OTRO">Otro</option>
        </select>
      </div>
      <button class="btn-primary" @click="openCreate = true">+ Nuevo paciente</button>
    </div>

    <!-- Table -->
    <div class="card">
      <div class="table-wrapper border-0 rounded-none">
        <table>
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Sexo</th>
              <th>CURP</th>
              <th>Teléfono</th>
              <th>Correo</th>
              <th>Estudios</th>
              <th>Registro</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="store.loading">
              <td colspan="8" class="py-10 text-center text-gray-400">Cargando...</td>
            </tr>
            <tr v-else-if="!store.list.length">
              <td colspan="8" class="py-10 text-center text-gray-400">No se encontraron pacientes</td>
            </tr>
            <tr v-for="p in store.list" :key="p.id">
              <td>
                <NuxtLink :to="`/patients/${p.id}`" class="font-semibold text-gray-900 hover:text-brand-600 transition-colors">
                  {{ p.firstName }} {{ p.lastName }}
                </NuxtLink>
              </td>
              <td class="capitalize">{{ p.sex.toLowerCase() }}</td>
              <td class="font-mono text-xs">{{ p.curp ?? "—" }}</td>
              <td>{{ p.phone ?? "—" }}</td>
              <td>{{ p.email ?? "—" }}</td>
              <td>
                <span class="badge bg-brand-50 text-brand-700">{{ p._count?.studies ?? 0 }}</span>
              </td>
              <td class="text-xs text-gray-400">{{ formatDate(p.createdAt) }}</td>
              <td>
                <div class="flex items-center gap-2">
                  <NuxtLink :to="`/patients/${p.id}`" class="btn btn-ghost btn-sm">Ver</NuxtLink>
                  <button class="btn btn-ghost btn-sm" @click="editPatient(p)">Editar</button>
                  <button v-if="can('patients:delete')" class="btn btn-ghost btn-sm text-red-500" @click="confirmDelete(p)">
                    Eliminar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="px-4 border-t border-gray-100">
        <UiPagination
          :page="store.meta.page"
          :pages="store.meta.pages"
          :total="store.meta.total"
          :limit="store.meta.limit"
          @change="fetchPage"
        />
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <PatientFormModal
      v-model="openCreate"
      :patient="editingPatient"
      @saved="onSaved"
    />

    <!-- Delete Confirm -->
    <UiModal v-model="deleteModal" title="Eliminar paciente" size="sm">
      <p class="text-sm text-gray-600">
        ¿Eliminar a <strong>{{ deletingPatient?.firstName }} {{ deletingPatient?.lastName }}</strong>? Esta acción no se puede deshacer.
      </p>
      <template #footer>
        <button class="btn-secondary" @click="deleteModal = false">Cancelar</button>
        <button class="btn-danger" :disabled="deleting" @click="doDelete">
          {{ deleting ? "Eliminando..." : "Eliminar" }}
        </button>
      </template>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from "@vueuse/core";
import { usePatientsStore, type Patient } from "~/stores/patients";
import { useRBAC } from "~/composables/useRBAC";
import { useNotification } from "~/composables/useNotification";

definePageMeta({ title: "Pacientes", middleware: "auth" });

const store   = usePatientsStore();
const { can } = useRBAC();
const notif   = useNotification();

const search     = ref("");
const sexFilter  = ref("");
const openCreate = ref(false);
const editingPatient = ref<Patient | null>(null);
const deleteModal    = ref(false);
const deletingPatient = ref<Patient | null>(null);
const deleting   = ref(false);

const debouncedFetch = useDebounceFn(() => fetchPage(1), 400);

async function fetchPage(page: number) {
  await store.fetchAll({ page, search: search.value || undefined, sex: sexFilter.value || undefined });
}

function editPatient(p: Patient) {
  editingPatient.value = p;
  openCreate.value     = true;
}

function confirmDelete(p: Patient) {
  deletingPatient.value = p;
  deleteModal.value     = true;
}

async function doDelete() {
  if (!deletingPatient.value) return;
  deleting.value = true;
  try {
    await store.remove(deletingPatient.value.id);
    notif.success("Paciente eliminado");
    deleteModal.value = false;
  } catch {
    notif.error("Error al eliminar");
  } finally {
    deleting.value = false;
  }
}

function onSaved() {
  openCreate.value     = false;
  editingPatient.value = null;
  fetchPage(store.meta.page);
  notif.success("Paciente guardado correctamente");
}

function formatDate(d: string) {
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "short" }).format(new Date(d));
}

onMounted(() => fetchPage(1));
</script>
