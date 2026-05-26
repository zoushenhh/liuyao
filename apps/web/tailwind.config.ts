/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      screens: {
        xs: '480px',
      },
      colors: {
        paper: '#F7F3E8',
        cinnabar: '#9E2A2B',
        'cinnabar-hover': '#7a2021',
        gold: '#D4AF37',
        'gold-light': '#F4E4C1',
        dark: '#2B2B2B',
      },
      fontFamily: {
        serif: ['SimSun', '宋体', 'serif'],
        mono: ['Consolas', 'SimSun', 'monospace'],
      },
    },
  },
  plugins: [],
}
