/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        diary: {
          white: "#FFFFFF",
          panel: "#F5F5F5",
          line: "#E5E5E5",
          muted: "#737373",
          black: "#000000",
          accent: "#4F46E5",
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
