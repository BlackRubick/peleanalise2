<template>
  <aside class="w-56 bg-slate-900 flex flex-col shrink-0 h-full">
    <!-- Logo -->
    <div class="flex items-center gap-3 px-4 h-14 shrink-0 border-b border-slate-800">
      <div class="w-7 h-7 bg-indigo-500 rounded-lg flex items-center justify-center shrink-0">
        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </div>
      <div>
        <p class="text-white text-sm font-bold leading-none">PeleAnálise</p>
        <p class="text-slate-400 text-[10px] mt-0.5">Dermatología</p>
      </div>
    </div>

    <!-- Nav -->
    <nav class="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
      <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider px-3 pb-2">General</p>

      <NuxtLink to="/dashboard" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
        </svg>
        Dashboard
      </NuxtLink>

      <NuxtLink to="/patients" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        Pacientes
      </NuxtLink>

      <NuxtLink to="/studies" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/>
        </svg>
        Estudios
      </NuxtLink>

      <NuxtLink to="/analysis" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
        </svg>
        Análisis IA
      </NuxtLink>

      <NuxtLink to="/reports" class="nav-item" active-class="nav-active">
        <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        Reportes
      </NuxtLink>

      <template v-if="auth.isAdmin">
        <p class="text-[10px] font-semibold text-slate-500 uppercase tracking-wider px-3 pt-5 pb-2">Administración</p>
        <NuxtLink to="/users" class="nav-item" active-class="nav-active">
          <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          Usuarios
        </NuxtLink>
      </template>
    </nav>

    <!-- User -->
    <div class="p-3 border-t border-slate-800 shrink-0">
      <div class="flex items-center gap-3 px-2 py-2 rounded-lg">
        <div class="w-7 h-7 rounded-full bg-indigo-500 flex items-center justify-center text-white text-[10px] font-bold shrink-0">
          {{ initials }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold text-slate-200 truncate">{{ auth.fullName }}</p>
          <p class="text-[10px] text-slate-500 truncate">{{ roleLabel }}</p>
        </div>
        <button
          class="p-1.5 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
          title="Cerrar sesión"
          @click="auth.logout()"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore()
const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return `${u.firstName[0]}${u.lastName[0]}`.toUpperCase()
})
const roleLabel = computed(() => {
  const map: Record<string, string> = { ADMIN: 'Administrador', DOCTOR: 'Médico', CAPTURISTA: 'Capturista' }
  return map[auth.user?.role ?? ''] ?? ''
})
</script>

<style scoped>
.nav-item {
  @apply flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-slate-400
         hover:bg-slate-800 hover:text-slate-100 transition-all duration-100;
}
.nav-active {
  @apply bg-indigo-600 text-white hover:bg-indigo-600 hover:text-white;
}
</style>
