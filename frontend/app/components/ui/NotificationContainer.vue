<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80">
      <TransitionGroup name="notif">
        <div
          v-for="n in notifications"
          :key="n.id"
          class="flex items-start gap-3 p-4 rounded-xl shadow-lg border text-sm"
          :class="styles[n.type].container"
        >
          <span class="text-lg leading-none shrink-0" :class="styles[n.type].icon">{{ icons[n.type] }}</span>
          <div class="flex-1">
            <p class="font-semibold" :class="styles[n.type].title">{{ n.title }}</p>
            <p v-if="n.message" class="text-xs mt-0.5 opacity-80">{{ n.message }}</p>
          </div>
          <button @click="remove(n.id)" class="opacity-50 hover:opacity-100 transition-opacity">✕</button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useNotification } from "~/composables/useNotification";

const { notifications, remove } = useNotification();

const icons = { success: "✓", error: "✕", warning: "⚠", info: "ℹ" };

const styles = {
  success: { container: "bg-emerald-50 border-emerald-200",  icon: "text-emerald-500", title: "text-emerald-800" },
  error:   { container: "bg-red-50 border-red-200",          icon: "text-red-500",     title: "text-red-800" },
  warning: { container: "bg-amber-50 border-amber-200",      icon: "text-amber-500",   title: "text-amber-800" },
  info:    { container: "bg-blue-50 border-blue-200",        icon: "text-blue-500",    title: "text-blue-800" },
};
</script>

<style scoped>
.notif-enter-active { transition: all 0.3s ease; }
.notif-leave-active { transition: all 0.2s ease; }
.notif-enter-from   { transform: translateX(100%); opacity: 0; }
.notif-leave-to     { transform: translateX(100%); opacity: 0; }
</style>
