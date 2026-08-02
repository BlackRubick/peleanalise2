<template>
  <div class="min-h-screen flex">
    <!-- Panel izquierdo decorativo -->
    <div class="hidden lg:flex lg:w-1/2 bg-brand-700 flex-col justify-between p-12 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-brand-800 via-brand-700 to-brand-600" />
      <div class="absolute inset-0 opacity-10"
        style="background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0); background-size: 40px 40px;" />

      <div class="relative z-10">
        <div class="flex items-center gap-3 mb-12">
          <div class="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <div>
            <h1 class="text-white font-bold text-lg leading-none">PeleAnálise</h1>
            <p class="text-brand-300 text-xs mt-0.5">Sistema Dermatológico</p>
          </div>
        </div>

        <div class="space-y-6 max-w-sm">
          <h2 class="text-3xl font-bold text-white leading-tight">
            Análisis clínico inteligente de lesiones cutáneas
          </h2>
          <p class="text-brand-200 text-sm leading-relaxed">
            Plataforma de soporte clínico con inteligencia artificial para la clasificación
            y seguimiento de lesiones dermatológicas.
          </p>
        </div>
      </div>

      <div class="relative z-10 grid grid-cols-3 gap-4">
        <div v-for="item in features" :key="item.label" class="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
          <p class="text-white font-bold text-xl">{{ item.value }}</p>
          <p class="text-brand-300 text-xs mt-0.5">{{ item.label }}</p>
        </div>
      </div>
    </div>

    <!-- Panel derecho — formulario -->
    <div class="flex-1 flex items-center justify-center p-8 bg-slate-50">
      <div class="w-full max-w-sm">
        <div class="lg:hidden flex items-center gap-2 mb-8">
          <div class="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <span class="font-bold text-gray-900">PeleAnálise</span>
        </div>
        <slot />
        <p class="text-center text-xs text-gray-400 mt-8">
          © {{ new Date().getFullYear() }} PeleAnálise · Uso exclusivo médico
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const features = [
  { value: 'ABCDE', label: 'Análisis automático' },
  { value: 'IA',    label: 'Clasificación neural' },
  { value: 'PDF',   label: 'Reportes clínicos' },
]
</script>
