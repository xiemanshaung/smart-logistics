# smart-logistics
海外仓末端配送与装载优化 (VRP + 3D Bin Packing) 基于 CVRP (带容量限制的车辆路径) 模型优化海外仓自有车队路径，结合 Three.js 开发 3D 装箱可视化功能，提升集装箱空间利用率
smart-logistics-demo/
├── docker-compose.yml          # 一键启动配置文件
├── backend/                    # 后端算法服务
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # API 入口
│   ├── packing_solver.py       # 3D 装箱算法 (LBF + 旋转)
│   └── routing_solver.py       # VRP 路径优化 (OR-Tools)
└── frontend/                   # 前端可视化界面
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── App.jsx             # 主界面
        ├── api.js              # API 调用
        └── components/
            └── PackingVisualizer.jsx # Three.js 3D 核心组件

启动：docker compose up --build
端口：http://127.0.0.1:5173/

| Type | 含义 | 适用场景 |
| :--- | :--- | :--- |
| **feat** | **新功能** | 增加了 3D 装箱功能、新增了 OSRM 服务 |
| **fix** | **修补 Bug** | 修复 Docker 镜像下载失败、修复 VRP 路径画图报错 |
| **docs** | **文档** | 修改 README.md、添加代码注释 |
| **style** | **格式** | 代码格式化 (Prettier/Black)、删除空行 (不影响代码逻辑) |
| **refactor**| **重构** | 代码整理（既不是新增功能也不是修 bug），如把大函数拆小 |
| **perf** | **性能** | 优化算法计算速度、减少前端渲染卡顿 |
| **test** | **测试** | 增加单元测试代码 |
| **chore** | **杂项/构建** | 修改 `.gitignore`、`Dockerfile`、`requirements.txt`、依赖升级 |
| **ci** | **CI/CD** | 修改 GitHub Actions 脚本等 |