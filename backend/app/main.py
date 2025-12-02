from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="DREO Supply Chain Algorithm Engine")

# 配置允许跨域，允许前端 localhost:3000 访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 生产环境建议设置为具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # 启动服务：python app/main.py
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

