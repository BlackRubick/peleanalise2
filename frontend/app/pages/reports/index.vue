<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="page-title">Reportes PDF</h1>
        <p class="page-subtitle">Descarga informes clínicos completos para estudios analizados por IA.</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3">
      <div class="relative">
        <input v-model="search" type="text" class="input pl-9 w-64" placeholder="Buscar paciente o lesión..."
          @input="debouncedFetch" />
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400"
          fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
      <select v-model="riskFilter" class="input w-44" @change="fetchPage(1)">
        <option value="">Todos los riesgos</option>
        <option value="BENIGNO">Benigno</option>
        <option value="SOSPECHOSO">Sospechoso</option>
        <option value="MALIGNO">Maligno</option>
      </select>
    </div>

    <!-- Table -->
    <div class="card">
      <div class="table-wrapper border-0 rounded-none">
        <table>
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Fecha estudio</th>
              <th>Tipo de lesión</th>
              <th>Localización</th>
              <th>Riesgo</th>
              <th>Confianza</th>
              <th>Capturado por</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="8" class="py-10 text-center text-gray-400">Cargando...</td>
            </tr>
            <tr v-else-if="!studies.length">
              <td colspan="8" class="py-12 text-center">
                <svg class="w-10 h-10 text-gray-200 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <p class="text-sm text-gray-400">No hay reportes disponibles todavía</p>
                <p class="text-xs text-gray-300 mt-1">Los reportes aparecen cuando un estudio ha sido analizado por la IA</p>
              </td>
            </tr>
            <tr v-for="s in studies" :key="s.id">
              <td>
                <div class="flex items-center gap-2.5">
                  <div class="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-[10px] font-bold shrink-0">
                    {{ s.patient.firstName[0] }}{{ s.patient.lastName[0] }}
                  </div>
                  <div>
                    <p class="font-medium text-gray-900 text-sm">{{ s.patient.firstName }} {{ s.patient.lastName }}</p>
                  </div>
                </div>
              </td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(s.studyDate) }}</td>
              <td class="text-sm text-gray-700">{{ s.lesionType }}</td>
              <td class="text-sm text-gray-600">{{ s.anatomicLocation }}</td>
              <td><UiBadgeRisk :risk="s.riskLevel" /></td>
              <td class="text-sm tabular-nums">
                <span class="font-semibold" :class="confidenceColor(s.riskLevel)">
                  {{ pct(s.analysis?.prediction?.probability) }}%
                </span>
              </td>
              <td class="text-sm text-gray-500">
                {{ s.capturedBy.firstName }} {{ s.capturedBy.lastName }}
              </td>
              <td class="text-right">
                <div class="flex items-center justify-end gap-2">
                  <NuxtLink :to="`/studies/${s.id}`" class="btn btn-ghost btn-sm">
                    Ver
                  </NuxtLink>
                  <button
                    class="btn btn-secondary btn-sm"
                    :disabled="downloading"
                    :title="`Descargar reporte de ${s.patient.firstName} ${s.patient.lastName}`"
                    @click="downloadPdf(s.id, `${s.patient.firstName} ${s.patient.lastName}`)"
                  >
                    <svg v-if="downloading" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    PDF
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="px-4 border-t border-gray-100">
        <UiPagination
          :page="meta.page" :pages="meta.pages"
          :total="meta.total" :limit="meta.limit"
          @change="fetchPage"
        />
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useDebounceFn }   from '@vueuse/core'
import { useApiFetch }     from '~/composables/useApiFetch'
import { useDownloadPdf }  from '~/composables/useDownloadPdf'

definePageMeta({ title: 'Reportes PDF', middleware: 'auth' })

type Prediction = { probability: number }
type Analysis   = { prediction?: Prediction }
type Study = {
  id: string; studyDate: string; lesionType: string; anatomicLocation: string
  riskLevel: string | null
  patient:    { firstName: string; lastName: string }
  capturedBy: { firstName: string; lastName: string }
  analysis?:  Analysis
}

const { downloadPdf, downloading } = useDownloadPdf()

const search     = ref('')
const riskFilter = ref('')
const loading    = ref(false)
const studies    = ref<Study[]>([])
const meta       = ref({ page: 1, pages: 1, total: 0, limit: 15 })

const debouncedFetch = useDebounceFn(() => fetchPage(1), 400)

async function fetchPage(page: number) {
  loading.value = true
  try {
    const query: Record<string, unknown> = { page, limit: 15, isProcessed: true }
    if (search.value)     query.search    = search.value
    if (riskFilter.value) query.riskLevel = riskFilter.value

    const res = await useApiFetch<{ data: Study[]; meta: typeof meta.value }>('/api/studies', { query })
    studies.value = res.data
    meta.value    = res.meta
  } finally {
    loading.value = false
  }
}

function pct(prob: number | undefined) {
  return Math.round((prob ?? 0) * 100)
}

function confidenceColor(risk: string | null) {
  if (risk === 'BENIGNO')    return 'text-emerald-600'
  if (risk === 'SOSPECHOSO') return 'text-amber-600'
  if (risk === 'MALIGNO')    return 'text-red-600'
  return 'text-gray-500'
}

function formatDate(d: string) {
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' }).format(new Date(d))
}

onMounted(() => fetchPage(1))
</script>
