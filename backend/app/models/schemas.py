from pydantic import BaseModel
from typing import List, Dict, Tuple, Optional

# SKU 基础信息
class SKUInfo(BaseModel):
    name: str
    length: int
    width: int
    height: int
    weight: float

# 原始订单请求
class OrderRequest(BaseModel):
    id: str
    customer: str
    rsd: int  # 0=今天(急单), 1=明天
    items: Dict[str, int] # SKU名称: 数量
    location: List[int]   # [x, y]

# 经过装箱计算后的订单 (增加了托盘数)
class PackedOrder(OrderRequest):
    total_weight: float
    total_volume: float
    pallets_needed: float

# 新增：3D 箱子模型
class Box3D(BaseModel):
    id: str
    sku_name: str
    color: str  # 用于区分不同SKU
    x: float
    y: float
    z: float
    w: float    # width
    h: float    # height
    d: float    # depth (length)

# 单个车辆的路线结果
class VehicleRoute(BaseModel):
    vehicle_id: int
    route_path: List[str] # 订单ID列表
    load_percent: float   # 装载率
    distance: float       # 行驶距离
    is_urgent_covered: bool # 是否包含了急单
    coordinates: List[List[float]]  # 路线坐标点 [[lat, lng], ...]
    packed_items: List[Box3D] = []  # 新增：3D装箱数据

# 最终返回给前端的完整方案
class SolutionResponse(BaseModel):
    total_distance: float
    total_pallets: float
    routes: List[VehicleRoute]
    dropped_orders: List[str] # 未能配送的订单
    locations: Dict[str, List[float]]  # 新增：返回所有点的坐标字典 {"ORD-1": [x, y], "DEPOT": [50, 50]}

