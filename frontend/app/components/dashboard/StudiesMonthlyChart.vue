<template>
  <Bar :data="chartData" :options="options" />
</template>

<script setup lang="ts">
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps<{
  data: Array<{ month: string; count: number; risk: string }>;
}>();

const chartData = computed(() => {
  const months = [...new Set(props.data.map((d) => d.month))].sort();
  const byRisk = (r: string) =>
    months.map((m) => props.data.find((d) => d.month === m && d.risk === r)?.count ?? 0);

  return {
    labels: months.map((m) => {
      const [y, mo] = m.split("-");
      return new Intl.DateTimeFormat("es-MX", { month: "short", year: "2-digit" }).format(
        new Date(parseInt(y), parseInt(mo) - 1)
      );
    }),
    datasets: [
      { label: "Benigno",    data: byRisk("BENIGNO"),    backgroundColor: "#10b981" },
      { label: "Sospechoso", data: byRisk("SOSPECHOSO"), backgroundColor: "#f59e0b" },
      { label: "Maligno",    data: byRisk("MALIGNO"),    backgroundColor: "#ef4444" },
    ],
  };
});

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: "bottom" as const } },
  scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
};
</script>
