from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class SKU(Base):
    """SKU基础信息表"""

    __tablename__ = "skus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    length = Column(Integer, nullable=False)  # 长度(cm)
    width = Column(Integer, nullable=False)  # 宽度(cm)
    height = Column(Integer, nullable=False)  # 高度(cm)
    weight = Column(Float, nullable=False)  # 重量(kg)
    # 扩展字段
    category = Column(String(50))  # 品类
    volume_unit = Column(String(20))  # 体积单位，如 UNIT/CARTON/PALLET
    pack_unit = Column(String(20))  # 包装单位
    is_hazardous = Column(Boolean, default=False)  # 是否危险品
    temperature_zone = Column(String(20))  # 温区，如 AMBIENT/CHILL/FROZEN

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    order_items = relationship("OrderItem", back_populates="sku")


class Customer(Base):
    """客户维度表"""

    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    lat = Column(Float)
    lng = Column(Float)
    customer_type = Column(String(20))  # DC / STORE / HUB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    orders = relationship("Order", back_populates="customer_ref")


class Warehouse(Base):
    """仓库 / 车场表"""

    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    lat = Column(Float)
    lng = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    vehicles = relationship("Vehicle", back_populates="home_warehouse")
    routes = relationship("Route", back_populates="warehouse")


class Vehicle(Base):
    """车辆资源表"""

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    plate_no = Column(String(50))
    capacity_pallets = Column(Float)
    capacity_weight = Column(Float)
    home_warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    region = Column(String(100))
    cost_per_km = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    home_warehouse = relationship("Warehouse", back_populates="vehicles")
    routes = relationship("Route", back_populates="vehicle")


class Order(Base):
    """订单主表"""

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)  # 业务订单号，如 ORD-1000
    customer = Column(String(200), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    rsd = Column(Integer, nullable=False, default=1)  # 0=今天(急单), 1=明天
    location_x = Column(Integer, nullable=False)  # 坐标X
    location_y = Column(Integer, nullable=False)  # 坐标Y
    status = Column(String(20), default="pending")  # pending, processed, completed

    # 扩展字段
    order_type = Column(String(20))  # B2B / B2C / RETURN
    priority = Column(Integer)  # 优先级，数字越大越紧急
    planned_ship_date = Column(DateTime(timezone=True))
    promised_date = Column(DateTime(timezone=True))
    ship_to_city = Column(String(100))
    ship_to_country = Column(String(100))
    ship_to_postal_code = Column(String(20))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    customer_ref = relationship("Customer", back_populates="orders")
    route_stops = relationship("RouteStop", back_populates="order")


class OrderItem(Base):
    """订单明细表（订单与SKU的多对多关系）"""

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)  # 商品数量
    unit_price = Column(Float)  # 单价
    currency = Column(String(10))  # 币种
    line_no = Column(Integer)  # 行号
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    order = relationship("Order", back_populates="items")
    sku = relationship("SKU", back_populates="order_items")


class Route(Base):
    """路线主表（保存排程结果）"""

    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    route_code = Column(String(100), unique=True, index=True)
    planning_date = Column(DateTime(timezone=True))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    total_distance = Column(Float)
    total_pallets = Column(Float)
    status = Column(String(20), default="planned")  # planned / executed / cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    vehicle = relationship("Vehicle", back_populates="routes")
    warehouse = relationship("Warehouse", back_populates="routes")
    stops = relationship("RouteStop", back_populates="route", cascade="all, delete-orphan")


class RouteStop(Base):
    """路线站点表"""

    __tablename__ = "route_stops"

    id = Column(Integer, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, index=True)
    sequence_no = Column(Integer, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    arrival_time = Column(DateTime(timezone=True))
    departure_time = Column(DateTime(timezone=True))
    distance_from_prev = Column(Float)
    pallets = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    route = relationship("Route", back_populates="stops")
    order = relationship("Order", back_populates="route_stops")


class PlanningOrder(Base):
    """规划输入订单表：供算法引擎读取的扁平化视图"""

    __tablename__ = "planning_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String(200))
    rsd = Column(Integer, nullable=False, default=1)
    location_x = Column(Integer, nullable=False)
    location_y = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")  # pending / planned / dropped
    total_weight = Column(Float)
    total_volume = Column(Float)
    pallets_estimated = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
