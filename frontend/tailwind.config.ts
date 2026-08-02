import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{vue,ts,js}",
    "./components/**/*.{vue,ts,js}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          50:  "#eef2ff",
          100: "#e0e7ff",
          200: "#c7d2fe",
          300: "#a5b4fc",
          400: "#818cf8",
          500: "#6366f1",
          600: "#4f46e5",
          700: "#4338ca",
          800: "#3730a3",
          900: "#312e81",
          950: "#1e1b4b",
        },
        risk: {
          benigno:    "#10b981",
          sospechoso: "#f59e0b",
          maligno:    "#ef4444",
        },
      },
      animation: {
        "fade-in":    "fadeIn 0.2s ease-in-out",
        "slide-in":   "slideIn 0.3s ease-out",
        "spin-slow":  "spin 2s linear infinite",
      },
      keyframes: {
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideIn: {
          "0%":   { transform: "translateX(-10px)", opacity: "0" },
          "100%": { transform: "translateX(0)",     opacity: "1" },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
