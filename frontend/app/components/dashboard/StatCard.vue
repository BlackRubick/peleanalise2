<template>
  <div class="card px-5 py-5">
    <div class="flex items-start justify-between mb-4">
      <div :class="['w-9 h-9 rounded-lg flex items-center justify-center shrink-0', bg]">
        <slot name="icon" />
      </div>
    </div>
    <div v-if="loading" class="space-y-2">
      <div class="skeleton h-7 w-20" />
      <div class="skeleton h-3 w-24" />
    </div>
    <template v-else>
      <p :class="['text-2xl font-bold tabular-nums tracking-tight', valueColor]">
        {{ value.toLocaleString('es-MX') }}
      </p>
      <p class="text-xs text-gray-500 mt-1 font-medium uppercase tracking-wide">{{ title }}</p>
    </template>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title:      string
  value:      number
  bg:         string
  valueColor: string
  loading?:   boolean
}>()
</script>
