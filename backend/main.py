"""
Smart Logistics Demo - Backend API

提供箱体装载（3D Bin Packing）和车辆路径规划（VRP）的一站式优化接口。
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
import random

# 引入核心模块
from packing_solver import BinPackingSolver, Item
from routing_solver import solve_vrp
from osrm_service import OSRMService

app = FastAPI()

# --- 数据模型 ---
class ItemReq(BaseModel):
    id: str
    w: int
    h: int
    d: int

class OptimizeRequest(BaseModel):
    items: List[ItemReq]
    container_size: Tuple[int, int, int]
    num_vehicles: int
    num_stops: int

@app.post("/api/optimize")
async def optimize(req: OptimizeRequest):
    # ==========================================
    # 1. 3D 装箱逻辑 (Bin Packing)
    # ==========================================
    colors = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6"]
    
    solver_items = [
        Item(i.id, i.w, i.h, i.d, random.choice(colors)) 
        for i in req.items
    ]
    
    packer = BinPackingSolver(req.container_size)
    packed_result = packer.solve(solver_items)
    
    # 计算空间利用率
    used_vol = sum([i['dims'][0]*i['dims'][1]*i['dims'][2] for i in packed_result])
    total_vol = req.container_size[0]*req.container_size[1]*req.container_size[2]
    utilization = used_vol / total_vol

    # ==========================================
    # 2. 车辆路径规划 (CVRP)
    # ==========================================

    # [Step A] 生成模拟的真实经纬度 (纽约曼哈顿附近)
    # 这样 OSRM 才能算出真实的路网距离。如果用 0,0 这种坐标，OSRM 会报错。
    # 仓库位置: 帝国大厦附近 (40.748817, -73.985428)
    base_lat, base_lng = 40.748817, -73.985428
    
    locations = [(base_lat, base_lng)] # 第一个是仓库
    
    for _ in range(req.num_stops):
        # 在仓库周围 0.05 度 (约 5km) 范围内随机分布
        lat = base_lat + (random.random() - 0.5) * 0.05
        lng = base_lng + (random.random() - 0.5) * 0.05
        locations.append((lat, lng))

    # [Step B] 获取距离矩阵 (混合策略)
    # 优先尝试 OSRM，失败则回退到欧氏距离
    osrm = OSRMService() # 默认连 http://osrm:5000
    matrix_data = osrm.get_distance_matrix(locations)
    
    final_matrix = None

    if matrix_data and "distances" in matrix_data:
        print("✅ [Main] 成功获取 OSRM 真实路网距离")
        # OSRM 返回的是 float (米)，转成 int 给 OR-Tools
        final_matrix = [
            [int(dist) for dist in row] 
            for row in matrix_data["distances"]
        ]
    else:
        print("⚠️ [Main] OSRM 不可用或返回空，将降级使用欧氏距离")
        final_matrix = None # 传 None，让 solve_vrp 内部自己算欧氏距离

    # [Step C] 调用 OR-Tools 求解
    routes = solve_vrp(req.num_vehicles, locations, external_matrix=final_matrix)

    return {
        "packing": {
            "container": req.container_size,
            "items": packed_result,
            "utilization": round(utilization * 100, 2)
        },
        "routing": {
            "routes": routes,
            "locations": locations # 返回坐标给前端画图
        }
    }