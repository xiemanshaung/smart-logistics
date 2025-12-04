import math
from typing import Dict, Optional
from app.models.schemas import OrderRequest, PackedOrder, SKUInfo

class PackingEstimator:
    def __init__(self, sku_db: Optional[Dict[str, SKUInfo]] = None):
        # 标准托盘参数
        self.PALLET_L = 120
        self.PALLET_W = 100
        self.PALLET_H_MAX = 180
        self.PALLET_VOL = self.PALLET_L * self.PALLET_W * self.PALLET_H_MAX
        self.LOAD_FACTOR = 0.85 # 经验装载率
        # 支持外部传入SKU数据库（从数据库获取）
        self.sku_db = sku_db or {}
    
    def set_sku_db(self, sku_db: Dict[str, SKUInfo]):
        """设置SKU数据库（从数据库服务获取）"""
        self.sku_db = sku_db

    def process(self, order: OrderRequest, sku_db: Optional[Dict[str, SKUInfo]] = None) -> PackedOrder:
        """
        处理订单，计算托盘数
        Args:
            order: 订单请求
            sku_db: 可选的SKU数据库，如果提供则使用，否则使用self.sku_db
        """
        # 优先使用传入的sku_db，其次使用实例的sku_db
        active_sku_db = sku_db if sku_db is not None else self.sku_db
        
        total_vol = 0
        total_weight = 0
        
        for sku_name, qty in order.items.items():
            if sku_name in active_sku_db:
                sku = active_sku_db[sku_name]
                item_vol = sku.length * sku.width * sku.height
                total_vol += item_vol * qty
                total_weight += sku.weight * qty
        
        # 核心算法：体积折算托盘数
        effective_vol = self.PALLET_VOL * self.LOAD_FACTOR
        pallets = math.ceil((total_vol / effective_vol) * 10) / 10
        
        # 返回增强后的数据模型
        return PackedOrder(
            **order.dict(),
            total_weight=total_weight,
            total_volume=total_vol,
            pallets_needed=max(0.1, pallets)
        )
    
    def process_with_sku_db(self, order: OrderRequest, sku_db: Dict[str, SKUInfo]) -> PackedOrder:
        """便捷方法：使用外部SKU数据库处理订单"""
        return self.process(order, sku_db=sku_db)

