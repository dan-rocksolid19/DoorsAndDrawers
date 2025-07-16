/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
    './core/**/*.py'
  ],
  theme: {
    extend: {
      colors: {
        'card-pink': '#fff1f0',
        'card-purple': '#f3f1ff',
        'card-mint': '#f0fff4',
        'card-peach': '#fff3e0',
        'card-blue': '#e3f2fd',
      }
    },
  },
  plugins: [],
}
