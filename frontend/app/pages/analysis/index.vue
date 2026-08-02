<template>
  <div class="space-y-5">

    <!-- Header stats -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div class="card px-4 py-4 flex items-center gap-3">
        <div class="w-9 h-9 bg-indigo-100 rounded-lg flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-gray-900 tabular-nums">{{ meta.total }}</p>
          <p class="text-xs text-gray-400">Total estudios</p>
        </div>
      </div>
      <div class="card px-4 py-4 flex items-center gap-3">
        <div class="w-9 h-9 bg-emerald-100 rounded-lg flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-emerald-600 tabular-nums">{{ meta.benigno }}</p>
          <p class="text-xs text-gray-400">Benignos</p>
        </div>
      </div>
      <div class="card px-4 py-4 flex items-center gap-3">
        <div class="w-9 h-9 bg-amber-100 rounded-lg flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-amber-600 tabular-nums">{{ meta.sospechoso }}</p>
          <p class="text-xs text-gray-400">Sospechosos</p>
        </div>
      </div>
      <div class="card px-4 py-4 flex items-center gap-3">
        <div class="w-9 h-9 bg-red-100 rounded-lg flex items-center justify-center shrink-0">
          <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div>
          <p class="text-xl font-bold text-red-600 tabular-nums">{{ meta.maligno }}</p>
          <p class="text-xs text-gray-400">Malignos</p>
        </div>
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
      <div class="flex rounded-lg border border-gray-200 bg-white overflow-hidden">
        <button
          v-for="opt in statusOpts" :key="opt.value"
          class="px-3 py-2 text-xs font-medium transition-colors"
          :class="statusFilter === opt.value
            ? 'bg-indigo-600 text-white'
            : 'text-gray-500 hover:bg-gray-50'"
          @click="statusFilter = opt.value; fetchPage(1)"
        >{{ opt.label }}</button>
      </div>
    </div>

    <!-- Table -->
    <div class="card">
      <div class="table-wrapper border-0 rounded-none">
        <table>
          <thead>
            <tr>
              <th>Paciente</th>
              <th>Fecha</th>
              <th>Lesión / Localización</th>
              <th>Riesgo IA</th>
              <th>Confianza</th>
              <th>Score ABCDE</th>
              <th>Estado</th>
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
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
                </svg>
                <p class="text-sm text-gray-400">No se encontraron resultados</p>
              </td>
            </tr>
            <tr v-for="s in studies" :key="s.id">
              <td>
                <div class="flex items-center gap-2.5">
                  <div class="w-7 h-7 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-[10px] font-bold shrink-0">
                    {{ s.patient.firstName[0] }}{{ s.patient.lastName[0] }}
                  </div>
                  <span class="font-medium text-gray-900 text-sm">
                    {{ s.patient.firstName }} {{ s.patient.lastName }}
                  </span>
                </div>
              </td>
              <td class="text-sm text-gray-500 whitespace-nowrap">{{ formatDate(s.studyDate) }}</td>
              <td class="text-sm text-gray-600">
                <span class="font-medium">{{ s.lesionType }}</span>
                <span class="text-gray-400"> · {{ s.anatomicLocation }}</span>
              </td>
              <td>
                <UiBadgeRisk :risk="s.riskLevel" />
              </td>
              <td class="text-sm">
                <template v-if="s.analysis?.prediction">
                  <div class="flex items-center gap-2 min-w-[80px]">
                    <div class="flex-1 bg-gray-100 rounded-full h-1.5">
                      <div
                        class="h-1.5 rounded-full"
                        :class="confidenceColor(s.riskLevel)"
                        :style="{ width: `${Math.round((s.analysis.prediction.probability ?? 0) * 100)}%` }"
                      />
                    </div>
                    <span class="text-xs font-semibold text-gray-700 tabular-nums w-9 text-right">
                      {{ Math.round((s.analysis.prediction.probability ?? 0) * 100) }}%
                    </span>
                  </div>
                </template>
                <span v-else class="text-gray-300 text-xs">—</span>
              </td>
              <td class="text-sm tabular-nums">
                <template v-if="s.analysis?.abcde">
                  <span
                    class="font-semibold"
                    :class="abcdeColor(s.analysis.abcde.totalScore)"
                  >{{ s.analysis.abcde.totalScore?.toFixed(1) ?? '—' }}</span>
                </template>
                <span v-else class="text-gray-300 text-xs">—</span>
              </td>
              <td>
                <span v-if="s.isProcessed" class="badge bg-emerald-50 text-emerald-700">Procesado</span>
                <span v-else class="badge bg-amber-50 text-amber-600">Pendiente</span>
              </td>
              <td class="text-right">
                <NuxtLink :to="`/studies/${s.id}`"
                  class="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700">
                  {{ s.isProcessed ? 'Ver análisis' : 'Analizar' }}
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                  </svg>
                </NuxtLink>
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
import { useDebounceFn } from '@vueuse/core'
import { useApiFetch }   from '~/composables/useApiFetch'

definePageMeta({ title: 'Análisis IA', middleware: 'auth' })

type Prediction = { probability: number; probBenigno: number; probSospechoso: number; probMaligno: number }
type Abcde      = { totalScore: number }
type Analysis   = { prediction?: Prediction; abcde?: Abcde }
type Study = {
  id: string; studyDate: string; lesionType: string; anatomicLocation: string
  riskLevel: string | null; isProcessed: boolean
  patient: { firstName: string; lastName: string }
  analysis?: Analysis
}
type Meta = { page: number; pages: number; total: number; limit: number; benigno: number; sospechoso: number; maligno: number }

const search       = ref('')
const riskFilter   = ref('')
const statusFilter = ref<'' | 'true' | 'false'>('')
const loading      = ref(false)
const studies      = ref<Study[]>([])
const meta         = ref<Meta>({ page: 1, pages: 1, total: 0, limit: 15, benigno: 0, sospechoso: 0, maligno: 0 })

const statusOpts = [
  { label: 'Todos',      value: '' as const },
  { label: 'Procesados', value: 'true' as const },
  { label: 'Pendientes', value: 'false' as const },
]

const debouncedFetch = useDebounceFn(() => fetchPage(1), 400)

async function fetchPage(page: number) {
  loading.value = true
  try {
    const query: Record<string, unknown> = { page, limit: 15 }
    if (search.value)       query.search      = search.value
    if (riskFilter.value)   query.riskLevel   = riskFilter.value
    if (statusFilter.value) query.isProcessed = statusFilter.value

    const res = await useApiFetch<{ data: Study[]; meta: Meta }>('/api/studies', { query })
    studies.value = res.data
    meta.value    = res.meta
  } finally {
    loading.value = false
  }
}

function confidenceColor(risk: string | null) {
  if (risk === 'BENIGNO')    return 'bg-emerald-500'
  if (risk === 'SOSPECHOSO') return 'bg-amber-500'
  if (risk === 'MALIGNO')    return 'bg-red-500'
  return 'bg-gray-400'
}

function abcdeColor(score: number | undefined) {
  if (!score) return 'text-gray-400'
  if (score >= 8)  return 'text-red-600'
  if (score >= 5)  return 'text-amber-600'
  return 'text-emerald-600'
}

function formatDate(d: string) {
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' }).format(new Date(d))
}

onMounted(() => fetchPage(1))
</script>
