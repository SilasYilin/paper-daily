import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// base './'：产物全部相对路径，兼容 GitHub Pages 子路径 /paper-daily/
export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
})
