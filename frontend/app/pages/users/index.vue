<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <input v-model="search" type="text" class="input w-64" placeholder="Buscar usuario..." @input="debouncedFetch" />
      <button class="btn-primary" @click="openModal = true">+ Nuevo usuario</button>
    </div>

    <div class="card">
      <div class="table-wrapper border-0 rounded-none">
        <table>
          <thead>
            <tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th>Último acceso</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-if="loading"><td colspan="6" class="py-10 text-center text-gray-400">Cargando...</td></tr>
            <tr v-for="u in users" :key="u.id">
              <td class="font-medium">{{ u.firstName }} {{ u.lastName }}</td>
              <td>{{ u.email }}</td>
              <td>
                <span :class="{
                  'badge-admin': u.role === 'ADMIN',
                  'badge-doctor': u.role === 'DOCTOR',
                  'badge-capturista': u.role === 'CAPTURISTA',
                }" class="badge">{{ u.role }}</span>
              </td>
              <td>
                <span :class="u.isActive ? 'badge bg-emerald-50 text-emerald-700' : 'badge bg-gray-100 text-gray-500'">
                  {{ u.isActive ? "Activo" : "Inactivo" }}
                </span>
              </td>
              <td class="text-xs text-gray-400">{{ u.lastLoginAt ? formatDate(u.lastLoginAt) : "Nunca" }}</td>
              <td>
                <div class="flex gap-2">
                  <button class="btn btn-ghost btn-sm" @click="editUser(u)">Editar</button>
                  <button class="btn btn-ghost btn-sm text-red-500" @click="confirmDelete(u)">Eliminar</button>
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

    <!-- User Modal -->
    <UiModal v-model="openModal" :title="editingUser ? 'Editar usuario' : 'Nuevo usuario'">
      <form @submit.prevent="saveUser" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div><label class="label">Nombre(s)</label><input v-model="form.firstName" class="input" required /></div>
          <div><label class="label">Apellidos</label><input v-model="form.lastName" class="input" required /></div>
        </div>
        <div><label class="label">Correo</label><input v-model="form.email" type="email" class="input" :disabled="!!editingUser" required /></div>
        <div><label class="label">Contraseña {{ editingUser ? "(dejar en blanco para no cambiar)" : "*" }}</label>
          <input v-model="form.password" type="password" class="input" :required="!editingUser" minlength="8" /></div>
        <div><label class="label">Rol</label>
          <select v-model="form.role" class="input" required>
            <option value="ADMIN">Administrador</option>
            <option value="DOCTOR">Médico</option>
            <option value="CAPTURISTA">Capturista</option>
          </select>
        </div>
        <div v-if="editingUser" class="flex items-center gap-2">
          <input id="isActive" v-model="form.isActive" type="checkbox" class="rounded border-gray-300" />
          <label for="isActive" class="text-sm text-gray-700">Usuario activo</label>
        </div>
      </form>
      <template #footer>
        <button class="btn-secondary" @click="closeModal">Cancelar</button>
        <button class="btn-primary" :disabled="saving" @click="saveUser">{{ saving ? "Guardando..." : "Guardar" }}</button>
      </template>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from "@vueuse/core";
import { useApiFetch } from "~/composables/useApiFetch";
import { useNotification } from "~/composables/useNotification";
import { useRBAC } from "~/composables/useRBAC";

definePageMeta({ title: "Usuarios", middleware: "auth" });

const notif   = useNotification();
const { can } = useRBAC();
const search  = ref("");
const loading = ref(false);
const saving  = ref(false);
const openModal     = ref(false);
const editingUser   = ref<Record<string, unknown> | null>(null);
const users = ref<Record<string, unknown>[]>([]);
const meta  = ref({ page: 1, pages: 1, total: 0, limit: 15 });

const form = reactive({
  firstName: "", lastName: "", email: "", password: "",
  role: "CAPTURISTA", isActive: true,
});

const debouncedFetch = useDebounceFn(() => fetchPage(1), 400);

async function fetchPage(page: number) {
  loading.value = true;
  try {
    const res = await useApiFetch<{ data: Record<string, unknown>[]; meta: typeof meta.value }>("/api/users", {
      query: { page, search: search.value || undefined },
    });
    users.value = res.data;
    meta.value  = res.meta;
  } finally {
    loading.value = false;
  }
}

function editUser(u: Record<string, unknown>) {
  editingUser.value = u;
  Object.assign(form, { firstName: u.firstName, lastName: u.lastName, email: u.email, password: "", role: u.role, isActive: u.isActive });
  openModal.value = true;
}

function closeModal() {
  openModal.value = false;
  editingUser.value = null;
  Object.assign(form, { firstName: "", lastName: "", email: "", password: "", role: "CAPTURISTA", isActive: true });
}

async function saveUser() {
  saving.value = true;
  try {
    if (editingUser.value) {
      const body: Record<string, unknown> = { ...form };
      if (!body.password) delete body.password;
      await useApiFetch(`/api/users/${editingUser.value.id}`, { method: "PUT", body });
    } else {
      await useApiFetch("/api/users", { method: "POST", body: form });
    }
    notif.success("Usuario guardado");
    closeModal();
    fetchPage(1);
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } };
    notif.error("Error", e?.data?.message);
  } finally {
    saving.value = false;
  }
}

async function confirmDelete(u: Record<string, unknown>) {
  if (!confirm(`¿Eliminar usuario ${u.email}?`)) return;
  try {
    await useApiFetch(`/api/users/${u.id}`, { method: "DELETE" });
    notif.success("Usuario eliminado");
    fetchPage(1);
  } catch {
    notif.error("Error al eliminar");
  }
}

function formatDate(d: string) {
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium", timeStyle: "short" }).format(new Date(d));
}

onMounted(() => fetchPage(1));
</script>
