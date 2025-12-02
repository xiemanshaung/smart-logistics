# 使用 Node 镜像
FROM node:18-alpine

WORKDIR /app

# 先复制依赖定义，利用 Docker 缓存层
COPY package*.json ./

RUN npm install

# 复制源代码
COPY . .

EXPOSE 3000

# 启动 Vite 开发服务器
CMD ["npm", "run", "dev", "--", "--host"]