-- DREO 智能物流调度系统数据库初始化脚本
-- 创建表结构

CREATE TABLE IF NOT EXISTS skus (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    length INTEGER NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    weight FLOAT NOT NULL,
    -- 扩展字段：品类、包装与属性
    category VARCHAR(50),
    volume_unit VARCHAR(20), -- 体积单位，如 UNIT / CARTON / PALLET
    pack_unit VARCHAR(20),   -- 包装单位
    is_hazardous BOOLEAN DEFAULT FALSE, -- 是否危险品
    temperature_zone VARCHAR(20),       -- 温区，如 AMBIENT/CHILL/FROZEN
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_skus_name ON skus(name);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    customer VARCHAR(200) NOT NULL,
    -- 可选外键：关联客户维表
    customer_id INTEGER,
    rsd INTEGER NOT NULL DEFAULT 1,
    location_x INTEGER NOT NULL,
    location_y INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    -- 扩展字段：订单类型与优先级
    order_type VARCHAR(20),          -- B2B / B2C / RETURN 等
    priority INTEGER,                -- 优先级分数，数字越大越紧急
    -- 承诺与计划日期
    planned_ship_date DATE,
    promised_date DATE,
    -- 更细粒度的收货地址
    ship_to_city VARCHAR(100),
    ship_to_country VARCHAR(100),
    ship_to_postal_code VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    sku_id INTEGER NOT NULL REFERENCES skus(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    -- 扩展字段：金额与币种
    unit_price FLOAT,
    currency VARCHAR(10),
    -- 行号，方便与外部 OMS 对齐
    line_no INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_sku_id ON order_items(sku_id);

-------------------------------------------------------------------------------
-- 二层：业务维度表
-------------------------------------------------------------------------------

-- 客户维度表
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    postal_code VARCHAR(20),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    customer_type VARCHAR(20), -- DC / STORE / HUB 等
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 仓库 / 车场表
CREATE TABLE IF NOT EXISTS warehouses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    lat DOUBLE PRECISION,
    lng DOUBLE PRECISION,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 车辆资源表
CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL, -- 车辆编号或车牌
    plate_no VARCHAR(50),
    capacity_pallets FLOAT,
    capacity_weight FLOAT,
    home_warehouse_id INTEGER REFERENCES warehouses(id),
    region VARCHAR(100),
    cost_per_km FLOAT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 路线主表（用于保存排程结果）
CREATE TABLE IF NOT EXISTS routes (
    id SERIAL PRIMARY KEY,
    route_code VARCHAR(100) UNIQUE,
    planning_date DATE,
    vehicle_id INTEGER REFERENCES vehicles(id),
    warehouse_id INTEGER REFERENCES warehouses(id),
    total_distance FLOAT,
    total_pallets FLOAT,
    status VARCHAR(20) DEFAULT 'planned', -- planned / executed / cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- 路线站点表
CREATE TABLE IF NOT EXISTS route_stops (
    id SERIAL PRIMARY KEY,
    route_id INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    sequence_no INTEGER NOT NULL, -- 在路线中的顺序
    order_id INTEGER REFERENCES orders(id),
    arrival_time TIMESTAMP WITH TIME ZONE,
    departure_time TIMESTAMP WITH TIME ZONE,
    distance_from_prev FLOAT,
    pallets FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routes_planning_date ON routes(planning_date);
CREATE INDEX IF NOT EXISTS idx_route_stops_route_id ON route_stops(route_id);
CREATE INDEX IF NOT EXISTS idx_route_stops_order_id ON route_stops(order_id);

-------------------------------------------------------------------------------
-- 三层：规划输入表（供算法引擎读取）
-------------------------------------------------------------------------------

-- 规划订单表：作为算法输入的扁平化视图
CREATE TABLE IF NOT EXISTS planning_orders (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL, -- 业务订单号
    customer_id INTEGER REFERENCES customers(id),
    customer_name VARCHAR(200),
    rsd INTEGER NOT NULL DEFAULT 1,
    location_x INTEGER NOT NULL,
    location_y INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending / planned / dropped
    total_weight FLOAT,
    total_volume FLOAT,
    pallets_estimated FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_planning_orders_status ON planning_orders(status);

-- 插入初始SKU数据（DREO典型产品）
INSERT INTO skus (name, length, width, height, weight) VALUES
    ('Tower_Fan_Pilot', 110, 30, 30, 8.5),
    ('Air_Fryer_Pro', 40, 35, 35, 6.0),
    ('Heater_Solaris', 25, 25, 60, 4.2)
ON CONFLICT (name) DO NOTHING;

-- 插入示例订单数据（用于测试）
-- 注意：这些是示例数据，实际使用时应该通过API或DBeaver手动插入
INSERT INTO orders (order_id, customer, rsd, location_x, location_y, status) VALUES
    ('ORD-1000', 'Walmart_DC_0', 0, 45, 55, 'pending'),
    ('ORD-1001', 'BestBuy_Hub_1', 0, 60, 70, 'pending'),
    ('ORD-1002', 'Target_DC_2', 1, 35, 40, 'pending'),
    ('ORD-1003', 'HomeDepot_3', 0, 80, 90, 'pending')
ON CONFLICT (order_id) DO NOTHING;

-- 插入订单明细（避免重复插入）
INSERT INTO order_items (order_id, sku_id, quantity)
SELECT 
    o.id,
    s.id,
    CASE 
        WHEN o.order_id = 'ORD-1000' AND s.name = 'Tower_Fan_Pilot' THEN 75
        WHEN o.order_id = 'ORD-1000' AND s.name = 'Air_Fryer_Pro' THEN 100
        WHEN o.order_id = 'ORD-1001' AND s.name = 'Tower_Fan_Pilot' THEN 60
        WHEN o.order_id = 'ORD-1002' AND s.name = 'Heater_Solaris' THEN 50
        WHEN o.order_id = 'ORD-1003' AND s.name = 'Air_Fryer_Pro' THEN 120
        ELSE 0
    END as qty
FROM orders o
CROSS JOIN skus s
WHERE (o.order_id, s.name) IN (
    ('ORD-1000', 'Tower_Fan_Pilot'),
    ('ORD-1000', 'Air_Fryer_Pro'),
    ('ORD-1001', 'Tower_Fan_Pilot'),
    ('ORD-1002', 'Heater_Solaris'),
    ('ORD-1003', 'Air_Fryer_Pro')
)
AND CASE 
    WHEN o.order_id = 'ORD-1000' AND s.name = 'Tower_Fan_Pilot' THEN 75
    WHEN o.order_id = 'ORD-1000' AND s.name = 'Air_Fryer_Pro' THEN 100
    WHEN o.order_id = 'ORD-1001' AND s.name = 'Tower_Fan_Pilot' THEN 60
    WHEN o.order_id = 'ORD-1002' AND s.name = 'Heater_Solaris' THEN 50
    WHEN o.order_id = 'ORD-1003' AND s.name = 'Air_Fryer_Pro' THEN 120
    ELSE 0
END > 0
AND NOT EXISTS (
    SELECT 1 FROM order_items oi 
    WHERE oi.order_id = o.id AND oi.sku_id = s.id
);

