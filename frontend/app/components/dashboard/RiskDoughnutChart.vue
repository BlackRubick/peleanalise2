<template>
  <Doughnut :data="chartData" :options="options" />
</template>

<script setup lang="ts">
import { Doughnut } from "vue-chartjs";
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps<{ benigno: number; sospechoso: number; maligno: number }>();

const chartData = computed(() => ({
  labels:   ["Benigno", "Sospechoso", "Maligno"],
  datasets: [{
    data:            [props.benigno, props.sospechoso, props.maligno],
    backgroundColor: ["#10b981", "#f59e0b", "#ef4444"],
    borderWidth:     2,
    borderColor:     "#fff",
  }],
}));

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: "bottom" as const },
    tooltip: {
      callbacks: {
        label: (ctx: { label: string; raw: unknown; dataset: { data: number[] } }) => {
          const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
          const pct   = total ? Math.round(((ctx.raw as number) / total) * 100) : 0;
          return ` ${ctx.label}: ${ctx.raw} (${pct}%)`;
        },
      },
    },
  },
};
</script>
