<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <div class="flex items-center gap-3">
      <NuxtLink to="/patients" class="btn-secondary btn-sm">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Volver
      </NuxtLink>
      <h1 class="page-title">Nuevo paciente</h1>
    </div>

    <div class="card">
      <div class="card-header">
        <h2 class="font-semibold text-gray-900">Datos del paciente</h2>
      </div>
      <div class="card-body">
        <form @submit.prevent="submit" class="grid grid-cols-2 gap-4">
          <div>
            <label class="label">Nombre(s) *</label>
            <input v-model="form.firstName" class="input" :class="{ 'input-error': errors.firstName }"
              placeholder="María" required />
            <p v-if="errors.firstName" class="field-error">{{ errors.firstName }}</p>
          </div>
          <div>
            <label class="label">Apellidos *</label>
            <input v-model="form.lastName" class="input" placeholder="González López" required />
          </div>
          <div>
            <label class="label">Sexo *</label>
            <select v-model="form.sex" class="input" required>
              <option value="">Seleccionar...</option>
              <option value="MASCULINO">Masculino</option>
              <option value="FEMENINO">Femenino</option>
              <option value="OTRO">Otro</option>
            </select>
          </div>
          <div>
            <label class="label">Fecha de nacimiento *</label>
            <input v-model="form.birthDate" type="date" class="input" required />
          </div>
          <div>
            <label class="label">CURP</label>
            <input v-model="form.curp" class="input font-mono text-sm"
              placeholder="GOML890101HDFNZS03" maxlength="18" />
          </div>
          <div>
            <label class="label">Teléfono</label>
            <input v-model="form.phone" type="tel" class="input" placeholder="55 1234 5678" />
          </div>
          <div class="col-span-2">
            <label class="label">Correo electrónico</label>
            <input v-model="form.email" type="email" class="input" placeholder="paciente@correo.mx" />
          </div>
          <div class="col-span-2">
            <label class="label">Dirección</label>
            <input v-model="form.address" class="input" placeholder="Calle, colonia, ciudad, CP" />
          </div>
          <div class="col-span-2">
            <label class="label">Observaciones</label>
            <textarea v-model="form.observations" class="input h-24 resize-none"
              placeholder="Antecedentes, alergias, notas..." />
          </div>

          <Transition name="fade">
            <div v-if="serverError" class="col-span-2 flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 rounded-lg">
              <svg class="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p class="text-sm text-red-700">{{ serverError }}</p>
            </div>
          </Transition>

          <div class="col-span-2 flex justify-end gap-3 pt-2">
            <NuxtLink to="/patients" class="btn-secondary">Cancelar</NuxtLink>
            <button type="submit" class="btn-primary" :disabled="saving">
              <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ saving ? 'Guardando...' : 'Crear paciente' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePatientsStore } from '~/stores/patients'
import { useNotification } from '~/composables/useNotification'

definePageMeta({ title: 'Nuevo Paciente', middleware: 'auth' })

const store  = usePatientsStore()
const notif  = useNotification()
const router = useRouter()

const saving      = ref(false)
const serverError = ref('')

const form = reactive({
  firstName:    '',
  lastName:     '',
  sex:          '',
  birthDate:    '',
  curp:         '',
  phone:        '',
  email:        '',
  address:      '',
  observations: '',
})

const errors = reactive<Record<string, string>>({ firstName: '' })

async function submit() {
  serverError.value = ''
  errors.firstName  = ''

  if (!form.firstName || !form.lastName || !form.sex || !form.birthDate) {
    errors.firstName = 'Nombre, apellidos, sexo y fecha de nacimiento son requeridos'
    return
  }

  saving.value = true
  try {
    const patient = await store.create(form as Parameters<typeof store.create>[0])
    notif.success('Paciente creado', `${form.firstName} ${form.lastName} registrado correctamente`)
    router.push(`/patients/${patient.id}`)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    serverError.value = e?.data?.message ?? 'Error al crear el paciente'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
