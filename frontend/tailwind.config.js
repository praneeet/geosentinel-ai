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
        // High-end dark intelligence palette
        slate: {
          950: '#080D17', // Main background
          900: '#0D1422', // Secondary background
          850: '#111C2D', // Elevated surface
          800: '#131F31', // Card background
          750: '#1A2942', // Card hover / active surface
          700: '#233857', // Subtle borders
          600: '#334E75', // Focused borders / dividers
          500: '#476999', // Muted text
          400: '#94A3B8', // Secondary text
          300: '#CBD5E1', // Body text
          200: '#E2E8F0', // Emphasized text
          100: '#F1F5F9', // Primary text
          50: '#F8FAFC',
        },
        sentinel: {
          950: '#080D17',
          900: '#0D1422',
          850: '#111C2D',
          800: '#131F31',
          750: '#1A2942',
          700: '#233857',
          600: '#334E75',
          500: '#38BDF8',
          400: '#818CF8',
        },
        brand: {
          sky: '#38BDF8',
          indigo: '#818CF8',
          cyan: '#06B6D4',
        },
        risk: {
          low: '#22C55E',      // Emerald Green (< 30)
          moderate: '#F59E0B', // Amber (30 - 60)
          severe: '#EF4444',   // Crimson Red (> 60)
          critical: '#DC2626', // Pulsing Alert Red (> 75)
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'monospace'],
      },
      boxShadow: {
        'card': '0 4px 20px -2px rgba(3, 7, 18, 0.5), 0 0 0 1px rgba(148, 163, 184, 0.08)',
        'card-hover': '0 8px 30px -4px rgba(3, 7, 18, 0.7), 0 0 0 1px rgba(56, 189, 248, 0.25)',
        'modal': '0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(148, 163, 184, 0.12)',
        'glow-sky': '0 0 20px rgba(56, 189, 248, 0.25)',
        'glow-indigo': '0 0 20px rgba(129, 140, 248, 0.25)',
      },
    },
  },
  plugins: [],
}
