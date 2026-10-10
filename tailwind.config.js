/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        surface: "#111827",
        "surface-hover": "#1a2234",
        border: "#1f2937",
        ink: "#e8ecf3",
        "ink-muted": "#8b95a7",
        "ink-faint": "#5c6675",
        accent: "#7c8cf8",
      },
    },
  },
  plugins: [],
};