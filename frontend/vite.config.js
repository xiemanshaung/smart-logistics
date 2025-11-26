import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite 配置：启用 React 插件，并把 /api 请求代理到 FastAPI
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // 允许外部访问（Docker、局域网）
    proxy: {
      "/api": {
        target: "http://backend:8000", // docker-compose 中 backend 服务
        changeOrigin: true,
      },
    },
  },
});
