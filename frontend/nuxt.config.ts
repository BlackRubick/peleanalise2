export default defineNuxtConfig({
  devtools: { enabled: true },

  srcDir: 'app/',
  serverDir: './server',

  modules: [
    "@nuxtjs/tailwindcss",
    "@pinia/nuxt",
    "@vueuse/nuxt",
    "@nuxt/image",
  ],

  components: [
    { path: '~/components', pathPrefix: false },
  ],

  css: ["~/assets/css/main.css"],

  runtimeConfig: {
    jwtSecret:        process.env.JWT_SECRET,
    jwtRefreshSecret: process.env.JWT_REFRESH_SECRET,
    pythonAiUrl:      process.env.PYTHON_AI_URL || "http://localhost:8000",
    public: {
      appName:    "PeleAnálise",
      appVersion: "1.0.0",
    },
  },

  tailwindcss: { configPath: "tailwind.config.ts" },
  typescript:  { strict: true, typeCheck: false },

  app: {
    head: {
      title: "PeleAnálise — Sistema de Análisis Dermatológico",
      meta: [
        { charset: "utf-8" },
        { name: "viewport", content: "width=device-width, initial-scale=1" },
      ],
      link: [
        { rel: "preconnect", href: "https://fonts.googleapis.com" },
        { rel: "stylesheet", href: "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" },
      ],
    },
  },

  compatibilityDate: "2024-07-01",
});
