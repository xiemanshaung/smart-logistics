# DREO 智能物流调度系统

## 项目简介

海外仓末端配送与装载优化系统 (VRP + 3D Bin Packing)

基于 CVRP (带容量限制的车辆路径) 模型优化海外仓自有车队路径，结合 Three.js 开发 3D 装箱可视化功能，提升集装箱空间利用率约 8%。

**技术栈：**

- 后端：FastAPI + OR-Tools (CVRP) + Pydantic + SQLAlchemy + PostgreSQL
- 前端：React + Leaflet (地图) + Three.js (3D可视化) + Tailwind CSS
- 数据库：PostgreSQL (可通过 DBeaver 管理)
- 部署：Docker Compose

**核心功能：**

1. ✅ 智能路径规划 (CVRP with RSD优先级)
2. ✅ 3D 装箱可视化 (Three.js)
3. ✅ 实时调度看板 (React + Leaflet)
4. ✅ 急单优先处理 (RSD=0 硬约束)
5. ✅ 多车辆协同调度

# 📂 项目目录结构

```text
dreo-logistics-system/
├── backend/                  # 后端根目录
│   ├── requirements.txt      # 依赖包列表
│   ├── init_db.sql           # 数据库初始化SQL脚本
│   ├── DBeaver连接指南.md     # DBeaver使用说明
│   └── app/
│       ├── __init__.py
│       ├── main.py           # 程序入口
│       ├── database.py       # 数据库连接配置
│       ├── db_models.py      # SQLAlchemy ORM模型
│       ├── db_service.py     # 数据库服务层（替代mock）
│       ├── init_database.py  # 数据库初始化脚本
│       ├── models/           # 数据模型定义 (Pydantic)
│       │   ├── __init__.py
│       │   └── schemas.py    # SKU, Order, Route 等数据结构
│       ├── api/              # API 路由层
│       │   ├── __init__.py
│       │   └── routes.py     # 定义前端调用的接口
│       └── modules/          # 核心算法模块 (按功能分文件夹)
│           ├── __init__.py
│           ├── mock/         # 模块1: 模拟数据生成（已废弃，改用数据库）
│           │   ├── __init__.py
│           │   └── generator.py
│           ├── packing/      # 模块2: 3D装箱/托盘估算
│           │   ├── __init__.py
│           │   └── estimator.py
│           └── vrp/          # 模块3: 路径规划求解器
│               ├── __init__.py
│               └── solver.py
└── frontend/                 # 前端根目录
```

## 快速开始

### 启动服务

```bash
# 启动所有服务（包括PostgreSQL数据库）
docker-compose up --build

# 停止当前容器
docker-compose down

# 仅启动数据库服务（用于DBeaver连接）
docker-compose up -d postgres
```

### 数据库配置

项目使用 **PostgreSQL** 数据库，默认配置如下：

- **主机**: `localhost`
- **端口**: `5432`
- **数据库名**: `dreo_logistics`
- **用户名**: `dreo_user`
- **密码**: `dreo_password`

**使用 DBeaver 连接数据库：**

1. 启动数据库服务：`docker-compose up -d postgres`
2. 打开 DBeaver，创建新的 PostgreSQL 连接
3. 填写上述连接信息
4. 详细步骤请参考：`backend/DBeaver连接指南.md`

**数据库表结构：**

- `skus`: SKU基础信息表（商品尺寸、重量等）
- `orders`: 订单主表（订单号、客户、坐标、急单标识等）
- `order_items`: 订单明细表（订单与SKU的多对多关系）

数据库会在首次启动时自动创建表结构并插入示例数据。

### 访问地址

- **前端界面**：http://localhost:3000
- **后端 API 文档**：http://localhost:8000/docs
- **健康检查**：http://localhost:8000/api/health

### 使用说明

1. **准备数据**（使用 DBeaver）：
   - 在 `orders` 表中插入待处理的订单（status='pending'）
   - 在 `order_items` 表中插入订单明细（关联订单和SKU）
   - 确保 `skus` 表中有对应的SKU信息

2. **运行排程**：
   - 打开前端页面，点击右上角"开始智能排程"按钮
   - 系统从数据库读取订单数据并计算最优配送方案
   - 左侧看板显示车辆调度详情和核心指标
   - 右侧地图显示配送路线可视化
   - 点击车辆卡片可查看 3D 装箱视图（支持旋转、缩放、平移）

3. **查看结果**：
   - 排程完成后，可通过 API 或前端界面查看结果
   - 订单状态会自动更新（建议后续扩展为自动更新）

## 项目亮点

### 算法层面

- **CVRP 模型**：带容量约束的车辆路径问题，考虑车辆满载率（26托/车）
- **RSD 优先级**：急单（RSD=0）硬约束，普通订单（RSD=1）软约束
- **启发式装箱**：3D Bin Packing 模拟算法，优化空间利用率

### 工程层面

- **模块化架构**：分层设计（API → Business Logic → Data Models → Database）
- **数据库集成**：SQLAlchemy ORM + PostgreSQL，支持 DBeaver 可视化管理
- **类型安全**：Pydantic 数据验证，确保接口稳定性
- **容器化部署**：Docker Compose 一键启动，支持热更新
- **高性能可视化**：React + Canvas 渲染，流畅支持大规模数据

### 业务适配

- **Prepaid 模式**：贴合 DREO 海外仓降本增效目标
- **实时反馈**：WebSocket 支持长时计算结果的实时推送（可扩展）
- **交互式调整**：支持计划员拖拽微调，触发局部重算（可扩展）

| Type               | 含义                | 适用场景                                                            |
| :----------------- | :------------------ | :------------------------------------------------------------------ |
| **feat**     | **新功能**    | 增加了 3D 装箱功能、新增了 OSRM 服务                                |
| **fix**      | **修补 Bug**  | 修复 Docker 镜像下载失败、修复 VRP 路径画图报错                     |
| **docs**     | **文档**      | 修改 README.md、添加代码注释                                        |
| **style**    | **格式**      | 代码格式化 (Prettier/Black)、删除空行 (不影响代码逻辑)              |
| **refactor** | **重构**      | 代码整理（既不是新增功能也不是修 bug），如把大函数拆小              |
| **perf**     | **性能**      | 优化算法计算速度、减少前端渲染卡顿                                  |
| **test**     | **测试**      | 增加单元测试代码                                                    |
| **chore**    | **杂项/构建** | 修改 `.gitignore`、`Dockerfile`、`requirements.txt`、依赖升级 |
| **ci**       | **CI/CD**     | 修改 GitHub Actions 脚本等                                          |
