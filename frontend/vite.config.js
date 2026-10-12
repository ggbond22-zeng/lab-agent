import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
// command: 'serve' 为本地开发, 'build' 为打包
// 打包时 base 指向 /lab-agent/（GitHub Pages 的仓库子路径），否则线上资源 404 白屏
export default defineConfig(({ command }) => ({
  base: command === 'build' ? '/lab-agent/' : '/',
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
}))
