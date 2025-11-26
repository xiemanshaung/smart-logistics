"""
Smart Logistics Demo - Backend API

提供箱体装载（3D Bin Packing）和车辆路径规划（VRP）的一站式优化接口。
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Tuple
from packing_solver import BinPackingSolver, Item
from routing_solver import solve_vrp
import random

# 创建 FastAPI 实例，供前端调用
app = FastAPI()


# --- Data Models ---
class ItemReq(BaseModel):
    """前端传入的单个货物参数"""

    id: str
    w: int  # width
    h: int  # height
    d: int  # depth


class OptimizeRequest(BaseModel):
    """前端调用 /api/optimize 时的整体请求结构"""

    items: List[ItemReq]              # 需要装载的货物
    container_size: Tuple[int, int, int]  # 箱体尺寸 (W,H,D)
    num_vehicles: int                 # 车队中的车辆数
    num_stops: int                    # 需要访问的客户点数量


@app.post("/api/optimize")
async def optimize(req: OptimizeRequest):
    """
    综合调度入口：
    1. 调用 3D 装箱求解器进行货物布局
    2. 调用 VRP 求解器生成车辆路径
    """

    # 1. 3D Bin Packing
    # 为每个货物随机指定颜色，便于前端可视化区分
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6"]

    solver_items = [
        Item(i.id, i.w, i.h, i.d, random.choice(colors))
        for i in req.items
    ]

    # 初始化装箱求解器并执行
    packer = BinPackingSolver(req.container_size)
    packed_result = packer.solve(solver_items)

    # 计算箱体利用率 = 已装载体积 / 箱体总体积
    utilization = sum([i["dims"][0] * i["dims"][1] * i["dims"][2] for i in packed_result]) / (
        req.container_size[0] * req.container_size[1] * req.container_size[2]
    )

    # 2. VRP (Mock 数据)
    # 生成随机坐标：第 0 个点默认视为仓库，其余为客户点
    locations = [(50, 50)] + [
        (random.randint(0, 100), random.randint(0, 100)) for _ in range(req.num_stops)
    ]
    routes = solve_vrp(req.num_vehicles, locations)

    # 聚合返回给前端
    return {
        "packing": {
            "container": req.container_size,
            "items": packed_result,
            "utilization": round(utilization * 100, 2),
        },
        "routing": {
            "routes": routes,
            "locations": locations,
        },
    }