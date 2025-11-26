import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 监听所有 IP，必须保留
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true
      }
    },
    watch: {
      usePolling: true,   // 强制轮询 (Docker 下必须)
    },
    hmr: {
      clientPort: 5173    // 明确告诉浏览器热更新走 5173 端口
    }
  }
})