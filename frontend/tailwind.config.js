/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sentinel: {
          950: '#06090e',
          900: '#0b111a',
          850: '#101926',
          800: '#162234',
          700: '#1e3048',
          600: '#2d4668',
          500: '#3e6392',
          400: '#5c87bf',
        },
        risk: {
          low: '#10b981',      // Emerald Green (< 30)
          moderate: '#f59e0b', // Amber (30 - 60)
          severe: '#ef4444',   // Crimson Red (> 60)
          critical: '#dc2626', // Pulsing Alert Red (> 75)
        }
      }
    },
  },
  plugins: [],
}
