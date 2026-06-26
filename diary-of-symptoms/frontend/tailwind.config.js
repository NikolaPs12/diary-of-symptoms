/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        diary: {
          white: "var(--surface)",
          panel: "var(--bg-secondary)",
          line: "var(--border)",
          muted: "var(--text-muted)",
          black: "var(--text)",
          accent: "var(--accent)",
          accentSoft: "var(--accent-soft)",
          bg: "var(--bg)",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Roboto Mono", "ui-monospace", "monospace"],
      },
      letterSpacing: {
        swiss: "-0.04em",
      },
    },
  },
  plugins: [],
};
