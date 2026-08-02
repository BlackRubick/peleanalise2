<template>
  <div class="flex items-center gap-3 text-xs">
    <span class="w-20 text-gray-500 shrink-0">{{ label }}</span>
    <div class="flex-1 bg-gray-100 rounded-full h-2">
      <div class="h-2 rounded-full transition-all duration-700" :class="color" :style="{ width: `${Math.round(value * 100)}%` }" />
    </div>
    <span class="w-9 text-right font-semibold text-gray-700">{{ Math.round(value * 100) }}%</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: number; color: string }>();
</script>
