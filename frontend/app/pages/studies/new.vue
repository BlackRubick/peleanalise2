<template>
  <div class="max-w-2xl mx-auto space-y-6">
    <div class="flex items-center gap-3">
      <NuxtLink to="/studies" class="btn-secondary btn-sm">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        Volver
      </NuxtLink>
      <h1 class="page-title">Nuevo estudio</h1>
    </div>

    <div class="card">
      <div class="card-header">
        <h2 class="font-semibold text-gray-900">Datos del estudio</h2>
      </div>
      <div class="card-body">
        <form @submit.prevent="submit" class="space-y-5">

          <!-- Selección de paciente -->
          <div>
            <label class="label">Paciente *</label>
            <div class="relative">
              <div class="relative">
                <input
                  v-model="patientSearch"
                  type="text"
                  class="input pl-9"
                  :class="{ 'input-error': errors.patientId }"
                  placeholder="Buscar paciente por nombre o CURP..."
                  autocomplete="off"
                  @input="onPatientSearch"
                  @focus="showDropdown = true"
                  @blur="hideDropdown"
                />
                <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
                </svg>
                <svg v-if="searchingPatients" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 animate-spin text-gray-400"
                  fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
              </div>

              <!-- Dropdown de resultados -->
              <div
                v-if="showDropdown && patientResults.length > 0"
                class="absolute z-20 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden"
              >
                <button
                  v-for="p in patientResults"
                  :key="p.id"
                  type="button"
                  class="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors border-b border-gray-50 last:border-0"
                  @mousedown.prevent="selectPatient(p)"
                >
                  <div class="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-brand-700 text-xs font-bold shrink-0">
                    {{ p.firstName[0] }}{{ p.lastName[0] }}
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ p.firstName }} {{ p.lastName }}</p>
                    <p class="text-xs text-gray-400">{{ p.curp ?? 'Sin CURP' }} · {{ p.sex }}</p>
                  </div>
                </button>
              </div>
              <div
                v-if="showDropdown && patientSearch.length >= 2 && patientResults.length === 0 && !searchingPatients"
                class="absolute z-20 top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-xl shadow-lg px-4 py-3"
              >
                <p class="text-sm text-gray-400">No se encontraron pacientes</p>
                <NuxtLink to="/patients/new" class="text-xs text-brand-600 font-medium hover:underline">
                  + Registrar nuevo paciente
                </NuxtLink>
              </div>
            </div>

            <!-- Paciente seleccionado -->
            <div v-if="selectedPatient" class="mt-2 flex items-center gap-2 px-3 py-2 bg-brand-50 border border-brand-100 rounded-lg">
              <div class="w-7 h-7 rounded-full bg-brand-200 flex items-center justify-center text-brand-800 text-xs font-bold shrink-0">
                {{ selectedPatient.firstName[0] }}{{ selectedPatient.lastName[0] }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-semibold text-brand-900">{{ selectedPatient.firstName }} {{ selectedPatient.lastName }}</p>
                <p class="text-xs text-brand-600">{{ selectedPatient.curp ?? 'Sin CURP' }}</p>
              </div>
              <button type="button" class="text-brand-400 hover:text-brand-600 transition-colors" @click="clearPatient">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <p v-if="errors.patientId" class="field-error">{{ errors.patientId }}</p>
          </div>

          <!-- Localización anatómica -->
          <div>
            <label class="label">Localización anatómica *</label>
            <input
              v-model="form.anatomicLocation"
              class="input"
              :class="{ 'input-error': errors.anatomicLocation }"
              placeholder="Ej: Dorso de mano derecha, cara, espalda..."
              required
            />
            <p v-if="errors.anatomicLocation" class="field-error">{{ errors.anatomicLocation }}</p>
          </div>

          <!-- Comentarios clínicos -->
          <div>
            <label class="label">Comentarios clínicos</label>
            <textarea
              v-model="form.clinicalComments"
              class="input h-24 resize-none"
              placeholder="Descripción de la lesión, evolución, síntomas asociados..."
            />
          </div>

          <!-- Fecha del estudio -->
          <div>
            <label class="label">Fecha del estudio</label>
            <input v-model="form.studyDate" type="date" class="input w-48" />
          </div>

          <!-- Error del servidor -->
          <Transition name="fade">
            <div v-if="serverError" class="flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 rounded-lg">
              <svg class="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <p class="text-sm text-red-700">{{ serverError }}</p>
            </div>
          </Transition>

          <div class="flex justify-end gap-3 pt-2">
            <NuxtLink to="/studies" class="btn-secondary">Cancelar</NuxtLink>
            <button type="submit" class="btn-primary" :disabled="saving">
              <svg v-if="saving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              {{ saving ? 'Guardando...' : 'Crear estudio' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'
import { useApiFetch }   from '~/composables/useApiFetch'
import { useNotification } from '~/composables/useNotification'

definePageMeta({ title: 'Nuevo Estudio', middleware: 'auth' })

const route  = useRoute()
const router = useRouter()
const notif  = useNotification()

type PatientOption = { id: string; firstName: string; lastName: string; curp?: string; sex: string }

const saving           = ref(false)
const serverError      = ref('')
const patientSearch    = ref('')
const patientResults   = ref<PatientOption[]>([])
const selectedPatient  = ref<PatientOption | null>(null)
const searchingPatients = ref(false)
const showDropdown     = ref(false)

const form = reactive({
  anatomicLocation: '',
  clinicalComments: '',
  studyDate:        new Date().toISOString().slice(0, 10),
})

const errors = reactive({ patientId: '', anatomicLocation: '' })

// Pre-fill patient from query param (coming from patient detail page)
onMounted(async () => {
  const pid = route.query.patientId as string | undefined
  if (pid) {
    try {
      const p = await useApiFetch<PatientOption>(`/api/patients/${pid}`)
      selectPatient(p)
    } catch {}
  }
})

const debouncedSearch = useDebounceFn(async () => {
  if (patientSearch.value.length < 2) {
    patientResults.value = []
    return
  }
  searchingPatients.value = true
  try {
    const res = await useApiFetch<{ data: PatientOption[] }>('/api/patients', {
      query: { search: patientSearch.value, limit: 8 },
    })
    patientResults.value = res.data
  } finally {
    searchingPatients.value = false
  }
}, 350)

function onPatientSearch() {
  selectedPatient.value = null
  showDropdown.value    = true
  debouncedSearch()
}

function selectPatient(p: PatientOption) {
  selectedPatient.value = p
  patientSearch.value   = ''
  patientResults.value  = []
  showDropdown.value    = false
  errors.patientId      = ''
}

function clearPatient() {
  selectedPatient.value = null
  patientSearch.value   = ''
}

function hideDropdown() {
  setTimeout(() => { showDropdown.value = false }, 150)
}

async function submit() {
  serverError.value        = ''
  errors.patientId         = ''
  errors.anatomicLocation  = ''

  if (!selectedPatient.value) {
    errors.patientId = 'Selecciona un paciente'
    return
  }
  if (!form.anatomicLocation.trim()) {
    errors.anatomicLocation = 'La localización anatómica es requerida'
    return
  }

  saving.value = true
  try {
    const study = await useApiFetch<{ id: string }>('/api/studies', {
      method: 'POST',
      body: {
        patientId:        selectedPatient.value.id,
        anatomicLocation: form.anatomicLocation,
        clinicalComments: form.clinicalComments || undefined,
        studyDate:        form.studyDate,
      },
    })
    notif.success('Estudio creado', 'Ahora puedes subir imágenes y ejecutar el análisis IA')
    router.push(`/studies/${study.id}`)
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    serverError.value = e?.data?.message ?? 'Error al crear el estudio'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
