/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['"PingFang SC"', '"Inter"', '"SF Pro Display"', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
