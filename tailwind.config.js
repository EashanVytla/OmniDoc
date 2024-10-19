/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './omnidoc_app/templates/**/*.html',  // Includes all HTML files inside the omnidoc_app/templates folder and its subdirectories
    './omnidoc_app/**/*.py',  // To include any Python files in the omnidoc_app directory that may contain inline template code
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}


