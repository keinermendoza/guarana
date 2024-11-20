/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../project/core/templates/parafrasis/partials/*.html",
    "../project/template_components/*.html",
    "../project/**/templates/**/**/*.html",
    "../project/cotton_components/cotton/**/**/**/*.html",

    "./src/**/*.{js,jsx}",
    "./src/react/**/*.{js,jsx}",

    "../admin_index/src/**/*.{js,jsx}",


  ],
  theme: {
    extend: {
      colors: {
        'primary': '#1b98e0',
        'secundary': '#00bfb3',
        'lightblue': '#ADD4EB',
        'darkblue': {
          'card': '#006494',
          'card-gradient': '#001f2e',
          'back': '#13293d',
        },
        'custom-gray': '#CACCCE',
      },
      fontFamily: {
        oxanium: ["oxanium", "sans"],
        poppins: ["poppins", "sans"],

      },
      screens: {
        'xs': '470px',
      },
      backgroundImage: {
        'blocks': "block",
      },
      listStyleImage: {
        'check':" url('/static/icons/check-badge.svg')",
      }
    }
  },
  plugins: [
    require('@tailwindcss/container-queries'),
  ],
}

