<template>
  <div>
    <p class="text-xs text-gray-400 mb-0.5">{{ label }}</p>
    <p :class="['text-gray-800 font-medium', mono ? 'font-mono text-xs' : 'text-sm']">{{ value }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string; value: string; mono?: boolean }>()
</script>
