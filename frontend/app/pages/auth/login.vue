<template>
  <div>
    <h2 class="text-2xl font-bold text-gray-900 mb-1">Bienvenido</h2>
    <p class="text-sm text-gray-500 mb-7">Ingresa tus credenciales para acceder al sistema</p>

    <form @submit.prevent="handleLogin" class="space-y-5">
      <div>
        <label class="label" for="email">Correo electrónico</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          class="input"
          :class="{ 'input-error': errors.email }"
          placeholder="correo@hospital.mx"
          autocomplete="email"
        />
        <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
      </div>

      <div>
        <label class="label" for="password">Contraseña</label>
        <div class="relative">
          <input
            id="password"
            v-model="form.password"
            :type="showPwd ? 'text' : 'password'"
            class="input pr-10"
            :class="{ 'input-error': errors.password }"
            placeholder="••••••••"
            autocomplete="current-password"
          />
          <button
            type="button"
            class="absolute inset-y-0 right-3 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
            @click="showPwd = !showPwd"
          >
            <svg v-if="showPwd" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
            </svg>
          </button>
        </div>
        <p v-if="errors.password" class="field-error">{{ errors.password }}</p>
      </div>

      <Transition name="fade">
        <div v-if="loginError" class="flex items-start gap-2.5 p-3.5 bg-red-50 border border-red-200 rounded-lg">
          <svg class="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <p class="text-sm text-red-700">{{ loginError }}</p>
        </div>
      </Transition>

      <button type="submit" class="btn-primary w-full btn-lg mt-2" :disabled="loading">
        <svg v-if="loading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <span>{{ loading ? 'Verificando...' : 'Iniciar sesión' }}</span>
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

definePageMeta({ layout: 'auth', middleware: 'guest' })

const auth     = useAuthStore()
const router   = useRouter()
const showPwd  = ref(false)
const loading  = ref(false)
const loginError = ref('')

const form   = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })

async function handleLogin() {
  loginError.value = ''
  errors.email     = ''
  errors.password  = ''

  if (!form.email)    { errors.email    = 'El correo es requerido'; return }
  if (!form.password) { errors.password = 'La contraseña es requerida'; return }

  loading.value = true
  try {
    await auth.login(form.email, form.password)
    router.push('/dashboard')
  } catch (err: unknown) {
    const e = err as { data?: { message?: string }; message?: string }
    loginError.value = e?.data?.message ?? e?.message ?? 'Credenciales incorrectas'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
