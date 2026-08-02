<template>
  <div class="space-y-6">

    <!-- Bienvenida + acciones rápidas -->
    <div class="bg-gradient-to-r from-indigo-600 to-indigo-500 rounded-2xl px-6 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <p class="text-indigo-200 text-sm">Bienvenido de vuelta,</p>
        <h1 class="text-white text-xl font-bold mt-0.5">{{ auth.fullName }}</h1>
        <p class="text-indigo-200 text-xs mt-1">{{ today }}</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <NuxtLink to="/patients/new" class="inline-flex items-center gap-2 bg-white text-indigo-700 font-semibold text-xs px-4 py-2 rounded-lg hover:bg-indigo-50 transition-colors">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
          </svg>
          Nuevo paciente
        </NuxtLink>
        <NuxtLink to="/studies/new" class="inline-flex items-center gap-2 bg-indigo-700 text-white font-semibold text-xs px-4 py-2 rounded-lg hover:bg-indigo-800 transition-colors">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo estudio
        </NuxtLink>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">

      <div class="bg-white rounded-xl border border-gray-100 shadow-sm px-4 py-4">
        <div class="flex items-center justify-between mb-3">
          <div class="w-9 h-9 bg-blue-100 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
          </div>
        </div>
        <div v-if="pending"><div class="h-6 w-16 bg-gray-200 rounded animate-pulse mb-1" /><div class="h-3 w-20 bg-gray-100 rounded animate-pulse" /></div>
        <template v-else>
          <p class="text-2xl font-bold text-gray-900 tabular-nums">{{ stats?.totalPatients ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-0.5">Pacientes</p>
        </template>
      </div>

      <div class="bg-white rounded-xl border border-gray-100 shadow-sm px-4 py-4">
        <div class="flex items-center justify-between mb-3">
          <div class="w-9 h-9 bg-violet-100 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
            </svg>
          </div>
        </div>
        <div v-if="pending"><div class="h-6 w-16 bg-gray-200 rounded animate-pulse mb-1" /><div class="h-3 w-20 bg-gray-100 rounded animate-pulse" /></div>
        <template v-else>
          <p class="text-2xl font-bold text-gray-900 tabular-nums">{{ stats?.totalStudies ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-0.5">Estudios</p>
        </template>
      </div>

      <div class="bg-white rounded-xl border border-gray-100 shadow-sm px-4 py-4">
        <div class="flex items-center justify-between mb-3">
          <div class="w-9 h-9 bg-emerald-100 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
        </div>
        <div v-if="pending"><div class="h-6 w-16 bg-gray-200 rounded animate-pulse mb-1" /><div class="h-3 w-20 bg-gray-100 rounded animate-pulse" /></div>
        <template v-else>
          <p class="text-2xl font-bold text-emerald-600 tabular-nums">{{ stats?.benigno ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-0.5">Benignos</p>
        </template>
      </div>

      <div class="bg-white rounded-xl border border-gray-100 shadow-sm px-4 py-4">
        <div class="flex items-center justify-between mb-3">
          <div class="w-9 h-9 bg-amber-100 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
          </div>
        </div>
        <div v-if="pending"><div class="h-6 w-16 bg-gray-200 rounded animate-pulse mb-1" /><div class="h-3 w-20 bg-gray-100 rounded animate-pulse" /></div>
        <template v-else>
          <p class="text-2xl font-bold text-amber-600 tabular-nums">{{ stats?.sospechoso ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-0.5">Sospechosos</p>
        </template>
      </div>

      <div class="bg-white rounded-xl border border-gray-100 shadow-sm px-4 py-4">
        <div class="flex items-center justify-between mb-3">
          <div class="w-9 h-9 bg-red-100 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
        </div>
        <div v-if="pending"><div class="h-6 w-16 bg-gray-200 rounded animate-pulse mb-1" /><div class="h-3 w-20 bg-gray-100 rounded animate-pulse" /></div>
        <template v-else>
          <p class="text-2xl font-bold text-red-600 tabular-nums">{{ stats?.maligno ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-0.5">Malignos</p>
        </template>
      </div>

      <div class="bg-white rounded-xl border border-gray-100 shadow-sm px-4 py-4">
        <div class="flex items-center justify-between mb-3">
          <div class="w-9 h-9 bg-gray-100 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </div>
        </div>
        <div v-if="pending"><div class="h-6 w-16 bg-gray-200 rounded animate-pulse mb-1" /><div class="h-3 w-20 bg-gray-100 rounded animate-pulse" /></div>
        <template v-else>
          <p class="text-2xl font-bold text-gray-700 tabular-nums">{{ stats?.pendingAnalysis ?? 0 }}</p>
          <p class="text-xs text-gray-500 mt-0.5">Pendientes</p>
        </template>
      </div>

    </div>

    <!-- Charts + módulos -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Gráfica mensual -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm lg:col-span-2">
        <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
          <div>
            <p class="text-sm font-semibold text-gray-900">Estudios por mes</p>
            <p class="text-xs text-gray-400 mt-0.5">Últimos 6 meses</p>
          </div>
          <NuxtLink to="/studies" class="text-xs text-indigo-600 font-medium hover:underline">Ver todos</NuxtLink>
        </div>
        <div class="p-5 h-56">
          <StudiesMonthlyChart :data="monthly" />
        </div>
      </div>

      <!-- Módulos de acceso rápido -->
      <div class="bg-white rounded-xl border border-gray-100 shadow-sm">
        <div class="px-5 py-4 border-b border-gray-100">
          <p class="text-sm font-semibold text-gray-900">Acceso rápido</p>
        </div>
        <div class="p-3 space-y-1">
          <NuxtLink v-for="item in quickLinks" :key="item.to" :to="item.to"
            class="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-gray-50 transition-colors group">
            <div :class="['w-9 h-9 rounded-xl flex items-center justify-center shrink-0', item.bg]">
              <component :is="'svg'" class="w-4 h-4" :class="item.color" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon"/>
              </component>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-800 group-hover:text-indigo-600 transition-colors">{{ item.label }}</p>
              <p class="text-xs text-gray-400 truncate">{{ item.desc }}</p>
            </div>
            <svg class="w-3.5 h-3.5 text-gray-300 group-hover:text-indigo-400 transition-colors ml-auto shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
            </svg>
          </NuxtLink>
        </div>
      </div>

    </div>

    <!-- Estudios recientes -->
    <div class="bg-white rounded-xl border border-gray-100 shadow-sm">
      <div class="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <div>
          <p class="text-sm font-semibold text-gray-900">Estudios recientes</p>
          <p class="text-xs text-gray-400 mt-0.5">Últimos registros del sistema</p>
        </div>
        <NuxtLink to="/studies" class="inline-flex items-center gap-1 text-xs font-medium text-indigo-600 hover:text-indigo-700">
          Ver todos
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </NuxtLink>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 border-b border-gray-100">
            <tr>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Paciente</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Fecha</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider hidden md:table-cell">Localización</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider hidden lg:table-cell">Tipo</th>
              <th class="px-5 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Riesgo</th>
              <th class="px-5 py-3"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="pending">
              <td colspan="6" class="py-12 text-center">
                <div class="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
              </td>
            </tr>
            <tr v-else-if="!recentStudies.length">
              <td colspan="6" class="py-12 text-center">
                <svg class="w-10 h-10 text-gray-200 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                </svg>
                <p class="text-sm text-gray-400">No hay estudios registrados aún</p>
                <NuxtLink to="/studies/new" class="inline-flex items-center gap-1 mt-3 text-xs text-indigo-600 font-medium hover:underline">
                  Crear primer estudio
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </NuxtLink>
              </td>
            </tr>
            <template v-else>
              <tr v-for="study in recentStudies" :key="study.id" class="border-t border-gray-50 hover:bg-gray-50/70 transition-colors">
                <td class="px-5 py-3.5">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-[11px] font-bold shrink-0">
                      {{ study.patient.firstName[0] }}{{ study.patient.lastName[0] }}
                    </div>
                    <div>
                      <p class="font-semibold text-gray-900 text-sm">{{ study.patient.firstName }} {{ study.patient.lastName }}</p>
                    </div>
                  </div>
                </td>
                <td class="px-5 py-3.5 text-gray-500 text-sm whitespace-nowrap">{{ formatDate(study.studyDate) }}</td>
                <td class="px-5 py-3.5 text-gray-600 text-sm hidden md:table-cell">{{ study.anatomicLocation }}</td>
                <td class="px-5 py-3.5 text-gray-600 text-sm hidden lg:table-cell">{{ study.lesionType }}</td>
                <td class="px-5 py-3.5"><UiBadgeRisk :risk="study.riskLevel" /></td>
                <td class="px-5 py-3.5 text-right">
                  <NuxtLink :to="'/studies/' + study.id"
                    class="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700">
                    Abrir
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                  </NuxtLink>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
import { useApiFetch } from '~/composables/useApiFetch'

definePageMeta({ title: 'Dashboard', middleware: 'auth' })

const auth = useAuthStore()

type DashboardData = {
  stats: {
    totalPatients: number; totalStudies: number
    benigno: number; sospechoso: number; maligno: number; pendingAnalysis: number
  } | null
  recentStudies: Array<{
    id: string; studyDate: string; lesionType: string; anatomicLocation: string
    riskLevel: string | null
    patient: { firstName: string; lastName: string }
    analysis: { prediction?: { probability: number } } | null
  }>
  monthly: Array<{ month: string; count: number; risk: string }>
}

const { data, pending } = await useAsyncData<DashboardData>(
  'dashboard-stats',
  () => useApiFetch<DashboardData>('/api/dashboard/stats'),
  {
    lazy: true,
    default: (): DashboardData => ({ stats: null, recentStudies: [], monthly: [] }),
  }
)

const stats         = computed(() => data.value?.stats)
const recentStudies = computed(() => data.value?.recentStudies ?? [])
const monthly       = computed(() => data.value?.monthly ?? [])

const today = new Intl.DateTimeFormat('es-MX', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }).format(new Date())

const quickLinks = [
  {
    to: '/patients',
    label: 'Pacientes',
    desc: 'Lista y gestión de pacientes',
    bg: 'bg-blue-100',
    color: 'text-blue-600',
    icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z',
  },
  {
    to: '/studies',
    label: 'Estudios',
    desc: 'Historial de estudios clínicos',
    bg: 'bg-violet-100',
    color: 'text-violet-600',
    icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
  },
  {
    to: '/analysis',
    label: 'Análisis IA',
    desc: 'Clasificación con inteligencia artificial',
    bg: 'bg-indigo-100',
    color: 'text-indigo-600',
    icon: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
  },
  {
    to: '/reports',
    label: 'Reportes PDF',
    desc: 'Generación de informes clínicos',
    bg: 'bg-rose-100',
    color: 'text-rose-600',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  },
]

function formatDate(d: string) {
  return new Intl.DateTimeFormat('es-MX', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(d))
}
</script>
