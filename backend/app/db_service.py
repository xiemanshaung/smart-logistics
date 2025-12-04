from sqlalchemy.orm import Session
from typing import List, Dict
from app.db_models import Order, OrderItem, SKU
from app.models.schemas import OrderRequest, SKUInfo

class DatabaseService:
    """数据库服务层，替代MockDataGenerator"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_sku_db(self) -> Dict[str, SKUInfo]:
        """获取所有SKU信息，返回字典格式（兼容原有接口）"""
        skus = self.db.query(SKU).all()
        return {
            sku.name: SKUInfo(
                name=sku.name,
                length=sku.length,
                width=sku.width,
                height=sku.height,
                weight=sku.weight
            )
            for sku in skus
        }
    
    def get_orders(self, limit: int = 20, status: str = "pending") -> List[OrderRequest]:
        """从数据库获取订单数据，转换为OrderRequest格式"""
        # 查询待处理的订单
        orders = self.db.query(Order).filter(
            Order.status == status
        ).limit(limit).all()
        
        result = []
        for order in orders:
            # 查询订单明细
            order_items = self.db.query(OrderItem).filter(
                OrderItem.order_id == order.id
            ).all()
            
            # 构建items字典 {sku_name: quantity}
            items = {}
            for item in order_items:
                sku = self.db.query(SKU).filter(SKU.id == item.sku_id).first()
                if sku:
                    items[sku.name] = item.quantity
            
            # 转换为OrderRequest
            result.append(OrderRequest(
                id=order.order_id,
                customer=order.customer,
                rsd=order.rsd,
                items=items,
                location=[order.location_x, order.location_y]
            ))
        
        return result
    
    def get_order_by_id(self, order_id: str) -> OrderRequest:
        """根据订单ID获取单个订单"""
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        order_items = self.db.query(OrderItem).filter(
            OrderItem.order_id == order.id
        ).all()
        
        items = {}
        for item in order_items:
            sku = self.db.query(SKU).filter(SKU.id == item.sku_id).first()
            if sku:
                items[sku.name] = item.quantity
        
        return OrderRequest(
            id=order.order_id,
            customer=order.customer,
            rsd=order.rsd,
            items=items,
            location=[order.location_x, order.location_y]
        )
    
    def update_order_status(self, order_id: str, status: str):
        """更新订单状态"""
        order = self.db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            order.status = status
            self.db.commit()


