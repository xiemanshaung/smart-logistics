import math
from app.models.schemas import OrderRequest, PackedOrder
from app.modules.mock.generator import SKU_DB

class PackingEstimator:
    def __init__(self):
        # 标准托盘参数
        self.PALLET_L = 120
        self.PALLET_W = 100
        self.PALLET_H_MAX = 180
        self.PALLET_VOL = self.PALLET_L * self.PALLET_W * self.PALLET_H_MAX
        self.LOAD_FACTOR = 0.85 # 经验装载率

    def process(self, order: OrderRequest) -> PackedOrder:
        total_vol = 0
        total_weight = 0
        
        for sku_name, qty in order.items.items():
            if sku_name in SKU_DB:
                sku = SKU_DB[sku_name]
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

