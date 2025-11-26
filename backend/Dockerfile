# Base image：轻量级 Python 3.9，适合部署 FastAPI
FROM python:3.9-slim

# 将工作目录固定在 /app，方便之后的 COPY/运行
WORKDIR /app

# 先复制依赖文件，利用 Docker layer cache
COPY requirements.txt .

# 安装依赖，--no-cache-dir 避免 pip 缓存撑大镜像
RUN pip install --no-cache-dir -r requirements.txt

# 再复制剩余代码
COPY . .

# 默认启动命令：运行 uvicorn 服务
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]