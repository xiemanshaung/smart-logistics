# DBeaver 数据库连接指南

## 一、使用 Docker Compose 启动数据库

项目已配置 PostgreSQL 数据库服务，通过以下命令启动：

```bash
docker-compose up -d postgres
```

或者启动所有服务：

```bash
docker-compose up -d
```

## 二、在 DBeaver 中配置连接

### 1. 创建新连接

1. 打开 DBeaver
2. 点击左上角 "新建数据库连接" 图标（或 `文件` → `新建` → `数据库连接`）
3. 选择 **PostgreSQL** 数据库类型
4. 点击 "下一步"

### 2. 配置连接参数

**连接设置：**
- **主机（Host）**: `localhost`
- **端口（Port）**: `5432`
- **数据库（Database）**: `dreo_logistics`
- **用户名（Username）**: `dreo_user`
- **密码（Password）**: `dreo_password`

**高级设置（可选）：**
- 在 "驱动属性" 中可以设置连接超时等参数
- 建议勾选 "显示所有数据库" 以便查看系统数据库

### 3. 测试连接

1. 点击 "测试连接" 按钮
2. 如果是首次使用，DBeaver 会提示下载 PostgreSQL JDBC 驱动，点击 "下载" 即可
3. 测试成功后，点击 "完成" 保存连接

## 三、数据库表结构

连接成功后，您可以在 DBeaver 中看到以下表：

### 1. `skus` 表 - SKU基础信息
- `id`: 主键
- `name`: SKU名称（唯一）
- `length`, `width`, `height`: 尺寸（cm）
- `weight`: 重量（kg）
- `created_at`, `updated_at`: 时间戳

### 2. `orders` 表 - 订单主表
- `id`: 主键
- `order_id`: 业务订单号（唯一，如 ORD-1000）
- `customer`: 客户名称
- `rsd`: 急单标识（0=今天急单, 1=明天）
- `location_x`, `location_y`: 配送坐标
- `status`: 订单状态（pending, processed, completed）
- `created_at`, `updated_at`: 时间戳

### 3. `order_items` 表 - 订单明细
- `id`: 主键
- `order_id`: 外键关联 orders.id
- `sku_id`: 外键关联 skus.id
- `quantity`: 商品数量
- `created_at`: 创建时间

## 四、常用 SQL 操作

### 查看所有订单
```sql
SELECT o.order_id, o.customer, o.rsd, o.status, 
       COUNT(oi.id) as item_count
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_id, o.customer, o.rsd, o.status
ORDER BY o.created_at DESC;
```

### 查看订单详情（包含SKU信息）
```sql
SELECT 
    o.order_id,
    o.customer,
    o.rsd,
    s.name as sku_name,
    oi.quantity,
    s.length, s.width, s.height, s.weight
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN skus s ON oi.sku_id = s.id
WHERE o.status = 'pending'
ORDER BY o.order_id, s.name;
```

### 插入新订单
```sql
-- 1. 插入订单主表
INSERT INTO orders (order_id, customer, rsd, location_x, location_y, status)
VALUES ('ORD-2000', 'New_Customer', 0, 50, 60, 'pending');

-- 2. 插入订单明细（需要先获取订单ID和SKU ID）
INSERT INTO order_items (order_id, sku_id, quantity)
SELECT 
    o.id,
    s.id,
    100  -- 数量
FROM orders o, skus s
WHERE o.order_id = 'ORD-2000' AND s.name = 'Tower_Fan_Pilot';
```

### 插入新SKU
```sql
INSERT INTO skus (name, length, width, height, weight)
VALUES ('New_Product', 50, 40, 30, 5.5)
ON CONFLICT (name) DO UPDATE 
SET length = EXCLUDED.length,
    width = EXCLUDED.width,
    height = EXCLUDED.height,
    weight = EXCLUDED.weight;
```

### 更新订单状态
```sql
UPDATE orders 
SET status = 'processed' 
WHERE order_id = 'ORD-1000';
```

## 五、数据导入导出

### 导出数据
1. 在 DBeaver 中右键点击表名
2. 选择 "导出数据"
3. 选择导出格式（CSV, Excel, SQL等）
4. 配置导出选项并执行

### 导入数据
1. 右键点击表名
2. 选择 "导入数据"
3. 选择数据源文件
4. 配置映射关系并执行

## 六、注意事项

1. **数据持久化**: Docker 数据存储在 `postgres_data` volume 中，删除容器不会丢失数据
2. **连接池**: 应用使用连接池管理数据库连接，默认大小为5
3. **事务管理**: 所有数据库操作都在事务中执行，确保数据一致性
4. **索引优化**: 已在关键字段（order_id, sku_name, status）上创建索引

## 七、故障排查

### 连接失败
- 检查 Docker 容器是否运行：`docker ps | grep postgres`
- 检查端口是否被占用：`netstat -an | grep 5432`
- 检查防火墙设置

### 表不存在
- 运行初始化脚本：`python backend/app/init_database.py`
- 或检查 `backend/init_db.sql` 是否已执行

### 权限问题
- 确认用户名和密码正确
- 检查数据库用户权限设置


