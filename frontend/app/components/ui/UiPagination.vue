<template>
  <div class="flex items-center justify-between py-3">
    <p class="text-sm text-gray-500">
      Mostrando
      <span class="font-medium">{{ from }}</span>–<span class="font-medium">{{ to }}</span>
      de <span class="font-medium">{{ total }}</span>
    </p>
    <div class="flex items-center gap-1">
      <button class="btn btn-secondary btn-sm" :disabled="page <= 1" @click="$emit('change', page - 1)">
        ←
      </button>
      <button
        v-for="p in visiblePages"
        :key="p"
        class="w-8 h-8 text-xs rounded-md font-medium transition-colors"
        :class="p === page ? 'bg-brand-600 text-white' : 'text-gray-600 hover:bg-gray-100'"
        @click="$emit('change', p)"
      >
        {{ p }}
      </button>
      <button class="btn btn-secondary btn-sm" :disabled="page >= pages" @click="$emit('change', page + 1)">
        →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ page: number; pages: number; total: number; limit: number }>();
defineEmits<{ change: [page: number] }>();

const from = computed(() => Math.min((props.page - 1) * props.limit + 1, props.total));
const to   = computed(() => Math.min(props.page * props.limit, props.total));

const visiblePages = computed(() => {
  const range: number[] = [];
  const start = Math.max(1, props.page - 2);
  const end   = Math.min(props.pages, props.page + 2);
  for (let i = start; i <= end; i++) range.push(i);
  return range;
});
</script>
