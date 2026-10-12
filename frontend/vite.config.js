import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      //  API 接口代理  凡是在前端中访问以 /api 开头的路由都会在前面加上 http://127.0.0.1:8000
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      // 静态文件接口代理 (头像、图片)
      '/uploads': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  }
})
