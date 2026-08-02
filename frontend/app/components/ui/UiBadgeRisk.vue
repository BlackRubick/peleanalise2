<template>
  <span :class="classes">
    <span class="w-1.5 h-1.5 rounded-full mr-1.5" :class="dotColor" />
    {{ label }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ risk?: string | null }>();

const riskMap: Record<string, { label: string; cls: string; dot: string }> = {
  BENIGNO:    { label: "Benigno",    cls: "badge-benigno",    dot: "bg-emerald-500" },
  SOSPECHOSO: { label: "Sospechoso", cls: "badge-sospechoso", dot: "bg-amber-500" },
  MALIGNO:    { label: "Maligno",    cls: "badge-maligno",    dot: "bg-red-500" },
};

const current = computed(() => riskMap[props.risk ?? ""] ?? { label: "Sin análisis", cls: "badge bg-gray-100 text-gray-500", dot: "bg-gray-400" });
const classes = computed(() => `badge flex items-center ${current.value.cls}`);
const label   = computed(() => current.value.label);
const dotColor = computed(() => current.value.dot);
</script>
