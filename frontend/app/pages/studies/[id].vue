<template>
  <div v-if="pending" class="flex items-center justify-center py-20 text-gray-400">
    Cargando estudio...
  </div>
  <div v-else-if="!study" class="text-center py-20 text-gray-400">
    Estudio no encontrado
  </div>
  <div v-else class="space-y-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <div class="flex items-center gap-3 mb-1">
          <NuxtLink to="/studies" class="btn-secondary btn-sm">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
            </svg>
            Estudios
          </NuxtLink>
        </div>
        <h1 class="page-title">Estudio Dermatológico</h1>
        <p class="page-subtitle">
          Paciente:
          <NuxtLink :to="`/patients/${study.patient.id}`" class="text-brand-600 font-medium">
            {{ study.patient.firstName }} {{ study.patient.lastName }}
          </NuxtLink>
          · {{ formatDate(study.studyDate) }}
        </p>
      </div>
      <div class="flex items-center gap-2 flex-wrap justify-end">
        <UiBadgeRisk :risk="study.riskLevel" />
        <button class="btn btn-ghost btn-sm" @click="openEdit = true">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
          </svg>
          Editar
        </button>
        <button v-if="can('patients:delete')" class="btn btn-ghost btn-sm text-red-500" @click="confirmDelete = true">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
          Eliminar
        </button>
        <button
          v-if="!study.analysis"
          class="btn-primary"
          :disabled="analyzing"
          @click="runAnalysis"
        >
          <svg v-if="analyzing" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
          {{ analyzing ? 'Analizando...' : 'Analizar con IA' }}
        </button>
        <button
          v-else
          class="btn-secondary"
          :disabled="downloading"
          @click="downloadPdf(study.id, `${study.patient.firstName} ${study.patient.lastName}`)"
        >
          <svg v-if="downloading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          {{ downloading ? 'Descargando...' : 'Descargar PDF' }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Columna imágenes -->
      <div class="space-y-4">
        <div class="card">
          <div class="card-header">
            <h3 class="font-semibold">Imágenes</h3>
          </div>
          <div class="card-body space-y-4">
            <ImageUploader :study-id="study.id" @uploaded="refresh" />
            <div class="grid grid-cols-2 gap-2">
              <div
                v-for="img in study.images"
                :key="img.id"
                class="relative rounded-lg overflow-hidden aspect-square bg-gray-100"
              >
                <img :src="img.storagePath" class="w-full h-full object-cover" :alt="img.type" />
                <div class="absolute bottom-0 left-0 right-0 bg-black/60 text-white text-[10px] text-center py-1">
                  {{ img.type }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Columna análisis -->
      <div class="lg:col-span-2 space-y-4">
        <template v-if="study.analysis">
          <!-- Predicción IA -->
          <div class="card border-2" :class="predictionBorderClass">
            <div class="card-body">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Predicción IA</p>
                  <p class="text-3xl font-bold" :class="predictionTextClass">
                    {{ predictionLabel }}
                  </p>
                  <p class="text-sm text-gray-500 mt-1">
                    Confianza:
                    <strong>{{ predictionPct }}%</strong>
                    · Modelo v{{ study.analysis.prediction?.modelVersion }}
                  </p>
                </div>
                <div :class="['w-14 h-14 rounded-full flex items-center justify-center', predictionIconBg]">
                  <svg class="w-7 h-7" :class="predictionTextClass" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path v-if="riskLevel === 'BENIGNO'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    <path v-else-if="riskLevel === 'SOSPECHOSO'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                    <path v-else-if="riskLevel === 'MALIGNO'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                    <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                  </svg>
                </div>
              </div>
              <div class="mt-4 space-y-2">
                <ProbBar label="Benigno"    :value="study.analysis.prediction?.probBenigno ?? 0"    color="bg-emerald-500" />
                <ProbBar label="Sospechoso" :value="study.analysis.prediction?.probSospechoso ?? 0" color="bg-amber-500" />
                <ProbBar label="Maligno"    :value="study.analysis.prediction?.probMaligno ?? 0"    color="bg-red-500" />
              </div>
            </div>
          </div>

          <!-- ABCDE -->
          <div class="card">
            <div class="card-header">
              <h3 class="font-semibold">Análisis ABCDE</h3>
            </div>
            <div class="card-body">
              <ABCDEMetricsPanel :abcde="study.analysis.abcde" />
            </div>
          </div>
        </template>

        <!-- Sin análisis -->
        <div v-else class="card border-2 border-dashed border-gray-200">
          <div class="card-body py-12 text-center">
            <svg class="w-10 h-10 text-gray-300 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
            </svg>
            <p class="font-medium text-gray-500">Sin análisis de IA</p>
            <p class="text-sm text-gray-400 mt-1">Sube una imagen y ejecuta el análisis</p>
          </div>
        </div>

        <!-- Datos clínicos -->
        <div class="card">
          <div class="card-header">
            <h3 class="font-semibold">Datos clínicos</h3>
          </div>
          <div class="card-body grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-gray-400">Tipo de lesión</p>
              <p class="font-medium">{{ study.lesionType }}</p>
            </div>
            <div>
              <p class="text-gray-400">Localización</p>
              <p class="font-medium">{{ study.anatomicLocation }}</p>
            </div>
            <div class="col-span-2">
              <p class="text-gray-400">Comentarios</p>
              <p class="font-medium">{{ study.clinicalComments ?? '—' }}</p>
            </div>
            <div>
              <p class="text-gray-400">Capturado por</p>
              <p class="font-medium">
                {{ study.capturedBy.firstName }} {{ study.capturedBy.lastName }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal editar datos clínicos -->
    <UiModal v-model="openEdit" title="Editar datos clínicos">
      <form @submit.prevent="saveEdit" class="space-y-4">
        <div>
          <label class="label">Tipo de lesión</label>
          <select v-model="editForm.lesionType" class="input">
            <option value="MELANOMA">Melanoma</option>
            <option value="NEVUS">Nevus</option>
            <option value="CARCINOMA_BASOCELULAR">Carcinoma Basocelular</option>
            <option value="CARCINOMA_ESPINOCELULAR">Carcinoma Espinocelular</option>
            <option value="QUERATOSIS_ACTINCA">Queratosis Actínica</option>
            <option value="DERMATOFIBROMA">Dermatofibroma</option>
            <option value="LESION_VASCULAR">Lesión Vascular</option>
            <option value="OTRO">Otro</option>
          </select>
        </div>
        <div>
          <label class="label">Localización anatómica *</label>
          <input v-model="editForm.anatomicLocation" class="input" required />
        </div>
        <div>
          <label class="label">Fecha del estudio</label>
          <input v-model="editForm.studyDate" type="date" class="input w-48" />
        </div>
        <div>
          <label class="label">Comentarios clínicos</label>
          <textarea v-model="editForm.clinicalComments" class="input h-24 resize-none"
            placeholder="Descripción de la lesión, evolución, síntomas..." />
        </div>
      </form>
      <template #footer>
        <button class="btn-secondary" @click="openEdit = false">Cancelar</button>
        <button class="btn-primary" :disabled="saving" @click="saveEdit">
          {{ saving ? 'Guardando...' : 'Guardar cambios' }}
        </button>
      </template>
    </UiModal>

    <!-- Modal confirmar eliminación -->
    <UiModal v-model="confirmDelete" title="Eliminar estudio" size="sm">
      <p class="text-sm text-gray-600">
        ¿Eliminar este estudio de <strong>{{ study.patient.firstName }} {{ study.patient.lastName }}</strong>?
        Esta acción no se puede deshacer.
      </p>
      <template #footer>
        <button class="btn-secondary" @click="confirmDelete = false">Cancelar</button>
        <button class="btn-danger" :disabled="deleting" @click="doDelete">
          {{ deleting ? 'Eliminando...' : 'Eliminar' }}
        </button>
      </template>
    </UiModal>
  </div>
</template>

<script setup lang="ts">
import { useNotification }  from '~/composables/useNotification'
import { useApiFetch }      from '~/composables/useApiFetch'
import { useDownloadPdf }   from '~/composables/useDownloadPdf'
import { useRBAC }          from '~/composables/useRBAC'

definePageMeta({ title: 'Detalle de Estudio', middleware: 'auth' })

const route  = useRoute()
const router = useRouter()
const notif  = useNotification()
const { can } = useRBAC()
const { downloadPdf, downloading } = useDownloadPdf()
const id = route.params.id as string

type StudyDetail = {
  id: string; studyDate: string; lesionType: string; anatomicLocation: string
  clinicalComments?: string; riskLevel: string | null; isProcessed: boolean
  patient:    { id: string; firstName: string; lastName: string }
  capturedBy: { firstName: string; lastName: string; role: string }
  images:     Array<{ id: string; storagePath: string; type: string }>
  analysis?: {
    prediction?: {
      prediction: string; probability: number
      probBenigno: number; probSospechoso: number; probMaligno: number
      modelVersion: string
    }
    abcde?: Record<string, number>
  }
}

const { data: study, pending, refresh } = await useAsyncData<StudyDetail>(
  `study-${id}`,
  () => useApiFetch<StudyDetail>(`/api/studies/${id}`),
  { lazy: true }
)

const analyzing    = ref(false)
const openEdit     = ref(false)
const saving       = ref(false)
const confirmDelete = ref(false)
const deleting     = ref(false)

const editForm = reactive({
  lesionType:       '',
  anatomicLocation: '',
  clinicalComments: '',
  studyDate:        '',
})

watch(openEdit, (open) => {
  if (open && study.value) {
    editForm.lesionType       = study.value.lesionType
    editForm.anatomicLocation = study.value.anatomicLocation
    editForm.clinicalComments = study.value.clinicalComments ?? ''
    editForm.studyDate        = study.value.studyDate?.slice(0, 10) ?? ''
  }
})

async function runAnalysis() {
  analyzing.value = true
  try {
    await useApiFetch(`/api/analysis/${id}`, { method: 'POST' })
    await refresh()
    notif.success('Análisis completado', 'El estudio ha sido procesado por la IA')
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    notif.error('Error en el análisis', e?.data?.message)
  } finally {
    analyzing.value = false
  }
}

async function saveEdit() {
  if (!editForm.anatomicLocation.trim()) return
  saving.value = true
  try {
    await useApiFetch(`/api/studies/${id}`, {
      method: 'PUT',
      body: {
        lesionType:       editForm.lesionType,
        anatomicLocation: editForm.anatomicLocation,
        clinicalComments: editForm.clinicalComments || null,
        studyDate:        editForm.studyDate || undefined,
      },
    })
    await refresh()
    openEdit.value = false
    notif.success('Estudio actualizado')
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    notif.error('Error al guardar', e?.data?.message)
  } finally {
    saving.value = false
  }
}

async function doDelete() {
  deleting.value = true
  try {
    await useApiFetch(`/api/studies/${id}`, { method: 'DELETE' })
    notif.success('Estudio eliminado')
    router.push('/studies')
  } catch (err: unknown) {
    const e = err as { data?: { message?: string } }
    notif.error('Error al eliminar', e?.data?.message)
  } finally {
    deleting.value = false
  }
}

const riskLevel = computed(() => study.value?.riskLevel ?? '')

const predictionLabel = computed(() => {
  const map: Record<string, string> = {
    BENIGNO:    'Benigno',
    SOSPECHOSO: 'Sospechoso',
    MALIGNO:    'Maligno',
  }
  return map[riskLevel.value] ?? riskLevel.value
})

const predictionBorderClass = computed(() => {
  if (riskLevel.value === 'BENIGNO')    return 'border-emerald-200 bg-emerald-50/30'
  if (riskLevel.value === 'SOSPECHOSO') return 'border-amber-200 bg-amber-50/30'
  if (riskLevel.value === 'MALIGNO')    return 'border-red-200 bg-red-50/30'
  return 'border-gray-200'
})

const predictionTextClass = computed(() => {
  if (riskLevel.value === 'BENIGNO')    return 'text-emerald-600'
  if (riskLevel.value === 'SOSPECHOSO') return 'text-amber-600'
  if (riskLevel.value === 'MALIGNO')    return 'text-red-600'
  return 'text-gray-600'
})

const predictionIconBg = computed(() => {
  if (riskLevel.value === 'BENIGNO')    return 'bg-emerald-100'
  if (riskLevel.value === 'SOSPECHOSO') return 'bg-amber-100'
  if (riskLevel.value === 'MALIGNO')    return 'bg-red-100'
  return 'bg-gray-100'
})

const predictionPct = computed(() => {
  const prob = study.value?.analysis?.prediction?.probability ?? 0
  return Math.round(prob * 100)
})

function formatDate(d: string) {
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'long' }).format(new Date(d))
}
</script>
