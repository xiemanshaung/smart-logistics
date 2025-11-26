import axios from "axios";

// FastAPI <-> Vite 的 Axios 封装，自动应用代理配置
const api = axios.create({
  // 这里不用写 http://localhost:8000
  // 因为我们在 vite.config.js 里配置了代理 (proxy)
  // 前端发给 /api 的请求，会自动转发给后端
  baseURL: "/",
});

// 添加响应拦截器（可选，用于处理错误）
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error);
    return Promise.reject(error);
  }
);

export default api;
