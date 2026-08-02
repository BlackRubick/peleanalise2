<template>
  <div v-if="pending" class="flex items-center justify-center py-20 text-gray-400">
    Cargando paciente...
  </div>
  <div v-else-if="!patient" class="text-center py-20 text-gray-400">
    Paciente no encontrado
  </div>
  <div v-else class="space-y-6">

    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div class="flex items-center gap-3">
        <NuxtLink to="/patients" class="btn-secondary btn-sm">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          Pacientes
        </NuxtLink>
        <div>
          <h1 class="page-title">{{ patient.firstName }} {{ patient.lastName }}</h1>
          <p class="page-subtitle">{{ sexLabel }} · {{ ageLabel }}</p>
        </div>
      </div>
      <button class="btn-primary" @click="openEdit = true">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
        </svg>
        Editar
      </button>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Info del paciente -->
      <div class="space-y-4">
        <div class="card">
          <div class="card-header">
            <h3 class="font-semibold text-gray-900">Información personal</h3>
          </div>
          <div class="card-body space-y-3 text-sm">
            <InfoRow label="CURP" :value="patient.curp ?? '—'" mono />
            <InfoRow label="Teléfono" :value="patient.phone ?? '—'" />
            <InfoRow label="Correo" :value="patient.email ?? '—'" />
            <InfoRow label="Fecha de nac." :value="formatDate(patient.birthDate)" />
            <InfoRow label="Registrado" :value="formatDate(patient.createdAt)" />
            <div v-if="patient.address">
              <p class="text-xs text-gray-400 mb-0.5">Dirección</p>
              <p class="text-gray-700">{{ patient.address }}</p>
            </div>
            <div v-if="patient.observations">
              <p class="text-xs text-gray-400 mb-0.5">Observaciones</p>
              <p class="text-gray-700 text-xs leading-relaxed">{{ patient.observations }}</p>
            </div>
          </div>
        </div>

        <!-- Acción rápida -->
        <NuxtLink :to="`/studies/new?patientId=${patient.id}`" class="btn-primary w-full justify-center">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Nuevo estudio
        </NuxtLink>
      </div>

      <!-- Estudios del paciente -->
      <div class="lg:col-span-2 space-y-4">
        <div class="card">
          <div class="card-header">
            <h3 class="font-semibold text-gray-900">Estudios clínicos</h3>
            <span class="badge bg-brand-50 text-brand-700">{{ patient.studies?.length ?? 0 }}</span>
          </div>
          <div class="table-wrapper border-0 rounded-none">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tipo de lesión</th>
                  <th>Localización</th>
                  <th>Riesgo</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!patient.studies?.length">
                  <td colspan="6" class="py-10 text-center text-gray-400">
                    <svg class="w-8 h-8 text-gray-200 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                    </svg>
                    <p class="text-sm">Sin estudios registrados</p>
                    <NuxtLink :to="`/studies/new?patientId=${patient.id}`"
                      class="inline-flex items-center gap-1 mt-2 text-xs text-brand-600 font-medium hover:underline">
                      Crear primer estudio
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                      </svg>
                    </NuxtLink>
                  </td>
                </tr>
                <tr v-for="s in patient.studies" :key="s.id">
                  <td class="whitespace-nowrap">{{ formatDate(s.studyDate) }}</td>
                  <td>{{ s.lesionType }}</td>
                  <td class="text-gray-600">{{ s.anatomicLocation }}</td>
                  <td><UiBadgeRisk :risk="s.riskLevel" /></td>
                  <td>
                    <span v-if="s.isProcessed" class="badge bg-emerald-50 text-emerald-700">Procesado</span>
                    <span v-else class="badge bg-gray-100 text-gray-500">Pendiente</span>
                  </td>
                  <td class="text-right">
                    <NuxtLink :to="`/studies/${s.id}`"
                      class="text-brand-600 hover:text-brand-700 text-xs font-medium">
                      Ver →
                    </NuxtLink>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <PatientFormModal
      v-model="openEdit"
      :patient="patientForEdit"
      @saved="onSaved"
    />

  </div>
</template>

<script setup lang="ts">
import { useNotification } from '~/composables/useNotification'
import { useApiFetch } from '~/composables/useApiFetch'
import type { Patient } from '~/stores/patients'

definePageMeta({ title: 'Detalle de Paciente', middleware: 'auth' })

const route  = useRoute()
const notif  = useNotification()
const id     = route.params.id as string
const openEdit = ref(false)

type PatientDetail = Patient & {
  studies: Array<{
    id: string; studyDate: string; lesionType: string; anatomicLocation: string
    riskLevel: string | null; isProcessed: boolean
    images: Array<{ storagePath: string; type: string }>
  }>
}

const { data: patient, pending, refresh } = await useAsyncData<PatientDetail>(
  `patient-${id}`,
  () => useApiFetch<PatientDetail>(`/api/patients/${id}`),
  { lazy: true }
)

const patientForEdit = computed(() => patient.value ?? null)

const sexLabel = computed(() => {
  const map: Record<string, string> = { MASCULINO: 'Masculino', FEMENINO: 'Femenino', OTRO: 'Otro' }
  return map[patient.value?.sex ?? ''] ?? '—'
})

const ageLabel = computed(() => {
  if (!patient.value?.birthDate) return ''
  const birth = new Date(patient.value.birthDate)
  const age   = Math.floor((Date.now() - birth.getTime()) / (365.25 * 24 * 60 * 60 * 1000))
  return `${age} años`
})

function formatDate(d: string | undefined) {
  if (!d) return '—'
  return new Intl.DateTimeFormat('es-MX', { dateStyle: 'medium' }).format(new Date(d))
}

async function onSaved() {
  openEdit.value = false
  await refresh()
  notif.success('Paciente actualizado correctamente')
}
</script>
