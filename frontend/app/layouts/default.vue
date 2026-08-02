<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">
    <AppSidebar />
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
      <AppHeader />
      <main class="flex-1 overflow-y-auto p-6 scrollbar-thin">
        <slot />
      </main>
    </div>
  </div>
</template>
