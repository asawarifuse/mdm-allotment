/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          50:  "#f0f4fa",
          100: "#d9e2ef",
          500: "#1e3a6d",
          700: "#0B2447",
          900: "#061632",
        },
        gold: {
          400: "#d4b23c",
          500: "#C9A227",
          600: "#a6851f",
        },
        ink: "#1A1A1A",
        paper: "#F7F8FA",
        ok: "#2E7D32",
        err: "#C62828",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};