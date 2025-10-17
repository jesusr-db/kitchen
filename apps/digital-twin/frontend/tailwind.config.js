/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        kitchen: {
          created: '#6B7280',
          cooking: '#F59E0B',
          ready: '#EAB308',
          delivery: '#3B82F6',
          completed: '#10B981',
        }
      }
    },
  },
  plugins: [],
}
