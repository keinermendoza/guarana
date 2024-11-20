import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'
import { resolve } from 'path';
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    origin: 'http://localhost:5173',

  },
  base: "/static/",
  build: {
    manifest: "manifest.json",
    rollupOptions: {
      input: {
        main: resolve('./src/main.jsx'),
      },
      output: {
        dir: '../project/staticfiles',
        entryFileNames: '[name].js',
      },
    },
  },
})