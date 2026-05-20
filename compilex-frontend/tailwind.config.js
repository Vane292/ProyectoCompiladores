/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"JetBrains Mono"', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        display: ['"Space Mono"', 'monospace'],
      },
      colors: {
        void:    { DEFAULT: '#080B0F', 50: '#0D1117', 100: '#161B22', 200: '#21262D', 300: '#30363D', 400: '#484F58', 500: '#6E7681' },
        plasma:  { DEFAULT: '#58A6FF', dim: '#1F6FEB', glow: '#79C0FF' },
        emerald: { DEFAULT: '#3FB950', dim: '#238636', glow: '#56D364' },
        crimson: { DEFAULT: '#F85149', dim: '#DA3633', glow: '#FF7B72' },
        amber:   { DEFAULT: '#E3B341', dim: '#9E6A03', glow: '#F0C27F' },
        violet:  { DEFAULT: '#BC8CFF', dim: '#6E40C9', glow: '#D2A8FF' },
      },
      boxShadow: {
        'plasma': '0 0 20px rgba(88, 166, 255, 0.15)',
        'emerald': '0 0 20px rgba(63, 185, 80, 0.15)',
        'crimson': '0 0 20px rgba(248, 81, 73, 0.15)',
        'panel': '0 1px 0 rgba(255,255,255,0.04), inset 0 1px 0 rgba(255,255,255,0.02)',
      },
      animation: {
        'pulse-plasma': 'pulsePlasma 2s ease-in-out infinite',
        'scanline': 'scanline 0.15s ease-out',
        'fade-up': 'fadeUp 0.25s cubic-bezier(0.23, 1, 0.32, 1) forwards',
        'blink': 'blink 1.2s step-end infinite',
      },
      keyframes: {
        pulsePlasma: { '0%,100%': { opacity: 1 }, '50%': { opacity: 0.6 } },
        scanline:    { from: { opacity: 0, transform: 'translateY(-4px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        fadeUp:      { from: { opacity: 0, transform: 'translateY(8px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        blink:       { '0%,100%': { opacity: 1 }, '50%': { opacity: 0 } },
      }
    }
  },
  plugins: []
}
