/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#0A0E1A',
          dark: '#060810',
          light: '#141B2D',
        },
        electric: {
          blue: '#00D4FF',
          amber: '#FFB300',
          green: '#00FF88',
          red: '#FF3366',
        },
      },
      fontFamily: {
        mono: ['Space Mono', 'monospace'],
        sans: ['Outfit', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 2s linear infinite',
      },
    },
  },
  plugins: [],
}
