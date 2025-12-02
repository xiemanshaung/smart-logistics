import random
from typing import List
from app.models.schemas import OrderRequest, SKUInfo

# DREO 典型产品库
SKU_DB = {
    "Tower_Fan_Pilot": SKUInfo(name="Tower_Fan_Pilot", length=110, width=30, height=30, weight=8.5),
    "Air_Fryer_Pro": SKUInfo(name="Air_Fryer_Pro", length=40, width=35, height=35, weight=6.0),
    "Heater_Solaris": SKUInfo(name="Heater_Solaris", length=25, width=25, height=60, weight=4.2)
}

class MockDataGenerator:
    @staticmethod
    def generate_orders(count: int = 20) -> List[OrderRequest]:
        orders = []
        customers = ["Walmart DC", "BestBuy Hub", "Target DC", "HomeDepot"]
        
        for i in range(count):
            items = {}
            # 修改 2: 增加每个订单的商品数量，让一辆车装不下，必须用第二辆
            if random.random() > 0.5:
                items["Tower_Fan_Pilot"] = random.randint(50, 100)  # 数量翻倍
            if random.random() > 0.3:
                items["Air_Fryer_Pro"] = random.randint(50, 150)  # 数量翻倍
            if not items: # 确保订单不为空
                items["Heater_Solaris"] = random.randint(30, 80)  # 增加数量
            
            # 修改 1: 提高急单(RSD=0)的概率到 80%，强迫算法必须送
            rsd = 0 if random.random() < 0.8 else 1
            
            orders.append(OrderRequest(
                id=f"ORD-{1000+i}",
                customer=random.choice(customers) + f"_{i}",
                rsd=rsd,
                items=items,
                # 修复：坐标范围改为20-100，确保映射后往内陆（东北方向）偏移，避免下海
                location=[random.randint(20, 100), random.randint(20, 100)]
            ))
        return orders

    @staticmethod
    def get_sku_db():
        return SKU_DB

