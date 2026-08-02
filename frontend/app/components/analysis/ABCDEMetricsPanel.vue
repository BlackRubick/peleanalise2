<template>
  <div class="space-y-4">
    <!-- Score total -->
    <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
      <div class="text-2xl font-bold text-brand-700">{{ abcde?.totalScore?.toFixed(2) ?? "—" }}</div>
      <div>
        <p class="text-xs text-gray-500">Score ABCDE total</p>
        <p class="text-[10px] text-gray-400">Mayor score = mayor riesgo</p>
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <!-- Asymmetry -->
      <div class="p-3 border border-gray-100 rounded-xl">
        <p class="text-xs font-bold text-gray-500 uppercase mb-2">A — Asimetría</p>
        <p class="text-xl font-semibold text-gray-800">{{ abcde?.asymmetryScore?.toFixed(3) ?? "—" }}</p>
        <div class="mt-2 text-xs text-gray-400 space-y-0.5">
          <div class="flex justify-between"><span>Horizontal</span><span>{{ abcde?.asymmetryH?.toFixed(3) }}</span></div>
          <div class="flex justify-between"><span>Vertical</span><span>{{ abcde?.asymmetryV?.toFixed(3) }}</span></div>
        </div>
      </div>

      <!-- Border -->
      <div class="p-3 border border-gray-100 rounded-xl">
        <p class="text-xs font-bold text-gray-500 uppercase mb-2">B — Bordes</p>
        <p class="text-xl font-semibold text-gray-800">{{ abcde?.borderScore?.toFixed(3) ?? "—" }}</p>
        <div class="mt-2 text-xs text-gray-400 space-y-0.5">
          <div class="flex justify-between"><span>Perímetro</span><span>{{ abcde?.perimeter?.toFixed(1) }}px</span></div>
          <div class="flex justify-between"><span>Compacidad</span><span>{{ abcde?.compactness?.toFixed(3) }}</span></div>
          <div class="flex justify-between"><span>Rugosidad</span><span>{{ abcde?.rugosity?.toFixed(3) }}</span></div>
        </div>
      </div>

      <!-- Color -->
      <div class="p-3 border border-gray-100 rounded-xl">
        <p class="text-xs font-bold text-gray-500 uppercase mb-2">C — Color</p>
        <p class="text-xl font-semibold text-gray-800">{{ abcde?.colorScore?.toFixed(3) ?? "—" }}</p>
        <div class="mt-2 flex gap-1">
          <div class="w-4 h-4 rounded-full border" :style="{ backgroundColor: rgbColor }" />
          <span class="text-xs text-gray-400">Media RGB: {{ abcde?.meanR?.toFixed(0) }}, {{ abcde?.meanG?.toFixed(0) }}, {{ abcde?.meanB?.toFixed(0) }}</span>
        </div>
        <p class="text-xs text-gray-400 mt-1">Varianza cromática: {{ abcde?.colorVariance?.toFixed(3) }}</p>
      </div>

      <!-- Diameter -->
      <div class="p-3 border border-gray-100 rounded-xl">
        <p class="text-xs font-bold text-gray-500 uppercase mb-2">D — Diámetro</p>
        <p class="text-xl font-semibold text-gray-800">{{ abcde?.diameterMm?.toFixed(2) ?? "—" }} <span class="text-sm font-normal text-gray-400">mm</span></p>
        <div class="mt-2 text-xs text-gray-400 space-y-0.5">
          <div class="flex justify-between"><span>Píxeles</span><span>{{ abcde?.diameterPx?.toFixed(1) }}px</span></div>
          <div class="flex justify-between"><span>Escala</span><span>{{ abcde?.pixelPerMm?.toFixed(2) }}px/mm</span></div>
        </div>
        <div v-if="(abcde?.diameterMm ?? 0) >= 6" class="mt-2 text-xs font-medium text-amber-600">
          ⚠️ Diámetro ≥ 6mm (criterio de riesgo)
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ abcde?: Record<string, number> | null }>();
const rgbColor = computed(() => {
  if (!props.abcde) return "#888";
  return `rgb(${Math.round(props.abcde.meanR)},${Math.round(props.abcde.meanG)},${Math.round(props.abcde.meanB)})`;
});
</script>
