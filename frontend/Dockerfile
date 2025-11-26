# 使用体积小的 Node 18 镜像，适合跑 Vite
FROM node:18-alpine

WORKDIR /app

# 先复制 package.json 以便缓存 node_modules
COPY package.json .

# 安装依赖
RUN npm install

# 拷贝剩余源代码
COPY . .

# 以 dev server 模式对外暴露，--host 允许外部访问
CMD ["npm", "run", "dev", "--", "--host"]

# 说明：线上环境应换成 npm run build + nginx，当前仅为演示