<template>
  <header class="h-14 bg-white border-b border-gray-100 px-6 flex items-center justify-between shrink-0">
    <div class="flex items-center gap-2 text-sm min-w-0">
      <span class="font-semibold text-gray-800 truncate">{{ pageTitle }}</span>
    </div>
    <div class="flex items-center gap-3 shrink-0">
      <span class="text-xs text-gray-400 hidden md:block">{{ today }}</span>
      <div class="w-px h-4 bg-gray-200" />
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-full bg-indigo-600 flex items-center justify-center text-white text-[10px] font-bold">
          {{ initials }}
        </div>
        <span class="text-xs font-medium text-gray-700 hidden sm:block">{{ auth.fullName }}</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
const route = useRoute()
const auth  = useAuthStore()
const pageTitle = computed(() => String(route.meta.title ?? 'PeleAnálise'))
const today = new Intl.DateTimeFormat('es-MX', { dateStyle: 'long' }).format(new Date())
const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  return `${u.firstName[0]}${u.lastName[0]}`.toUpperCase()
})
</script>
