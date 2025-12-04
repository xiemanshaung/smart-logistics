# SQL 查询语句详解

## 查询语句

```sql
SELECT 
    o.order_id,
    o.customer,
    o.rsd,
    s.name as sku_name,
    s.length,
    s.width,
    s.height,
    s.weight,
    oi.quantity
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN skus s ON oi.sku_id = s.id
WHERE o.order_id = 'ORD-1000';
```

## 📝 逐行解释

### 1. SELECT 子句 - 选择要显示的字段

```sql
SELECT 
    o.order_id,        -- 订单号（来自orders表）
    o.customer,        -- 客户名称（来自orders表）
    o.rsd,            -- 急单标识（来自orders表）
    s.name as sku_name, -- SKU名称（来自skus表，重命名为sku_name）
    s.length,         -- SKU长度（来自skus表）
    s.width,          -- SKU宽度（来自skus表）
    s.height,         -- SKU高度（来自skus表）
    s.weight,         -- SKU重量（来自skus表）
    oi.quantity       -- 商品数量（来自order_items表）
```

**说明**：
- `o.` 表示字段来自 `orders` 表（别名 `o`）
- `s.` 表示字段来自 `skus` 表（别名 `s`）
- `oi.` 表示字段来自 `order_items` 表（别名 `oi`）
- `as sku_name` 表示将 `s.name` 重命名为 `sku_name` 显示

### 2. FROM 子句 - 主表

```sql
FROM orders o
```

**说明**：
- 从 `orders` 表开始查询
- `o` 是 `orders` 表的别名（简化写法）

### 3. JOIN 子句 - 连接订单明细表

```sql
JOIN order_items oi ON o.id = oi.order_id
```

**说明**：
- `JOIN order_items oi` - 连接 `order_items` 表，别名为 `oi`
- `ON o.id = oi.order_id` - 连接条件：
  - `orders` 表的 `id` 字段
  - 等于 `order_items` 表的 `order_id` 字段
  - 这样就能找到每个订单的所有明细

**含义**：找到订单 ORD-1000 的所有订单明细记录

### 4. JOIN 子句 - 连接SKU表

```sql
JOIN skus s ON oi.sku_id = s.id
```

**说明**：
- `JOIN skus s` - 连接 `skus` 表，别名为 `s`
- `ON oi.sku_id = s.id` - 连接条件：
  - `order_items` 表的 `sku_id` 字段
  - 等于 `skus` 表的 `id` 字段
  - 这样就能获取每个订单明细对应的SKU信息

**含义**：通过订单明细中的 `sku_id`，找到对应的SKU详细信息

### 5. WHERE 子句 - 过滤条件

```sql
WHERE o.order_id = 'ORD-1000'
```

**说明**：
- 只查询订单号为 `'ORD-1000'` 的订单
- 如果没有这个条件，会返回所有订单的明细

## 🔄 查询执行流程

### 步骤1：从订单表开始
```
orders 表
┌────┬───────────┬──────────────┐
│ id │ order_id  │ customer     │
├────┼───────────┼──────────────┤
│ 1  │ ORD-1000  │ Walmart_DC_0 │
│ 2  │ ORD-1001  │ BestBuy_Hub  │
└────┴───────────┴──────────────┘
```

### 步骤2：连接订单明细表（JOIN order_items）
```
找到 order_items 表中 order_id = 1 的记录
┌────┬──────────┬────────┬──────────┐
│ id │ order_id │ sku_id │ quantity │
├────┼──────────┼────────┼──────────┤
│ 1  │ 1        │ 1      │ 75       │ ← 订单1的第1个明细
│ 2  │ 1        │ 2      │ 100      │ ← 订单1的第2个明细
└────┴──────────┴────────┴──────────┘
```

### 步骤3：连接SKU表（JOIN skus）
```
通过 sku_id 找到对应的SKU信息
┌────┬──────────────────┬────────┬───────┬────────┬────────┐
│ id │ name             │ length│ width │ height │ weight │
├────┼──────────────────┼───────┼───────┼────────┼────────┤
│ 1  │ Tower_Fan_Pilot  │ 110   │ 30    │ 30     │ 8.5    │
│ 2  │ Air_Fryer_Pro    │ 40    │ 35    │ 35     │ 6.0    │
└────┴──────────────────┴───────┴───────┴────────┴────────┘
```

### 步骤4：应用WHERE过滤
```
只保留 order_id = 'ORD-1000' 的记录
```

## 📊 查询结果示例

执行这个查询后，会得到类似这样的结果：

```
order_id | customer      | rsd | sku_name        | length | width | height | weight | quantity
---------|---------------|-----|-----------------|--------|-------|--------|--------|----------
ORD-1000 | Walmart_DC_0  | 0   | Tower_Fan_Pilot | 110    | 30    | 30     | 8.5    | 75
ORD-1000 | Walmart_DC_0  | 0   | Air_Fryer_Pro   | 40     | 35    | 35     | 6.0    | 100
```

**解读**：
- 订单 ORD-1000 包含两种商品
- 第1行：75个 Tower_Fan_Pilot（塔扇）
- 第2行：100个 Air_Fryer_Pro（空气炸锅）

## 🎯 查询目的

这个查询的目的是：**获取订单 ORD-1000 的完整信息，包括订单基本信息、订单中包含的所有SKU及其详细信息、以及每个SKU的数量**。

## 🔍 等价的查询方式

### 方式1：使用表全名（不使用别名）

```sql
SELECT 
    orders.order_id,
    orders.customer,
    orders.rsd,
    skus.name as sku_name,
    skus.length,
    skus.width,
    skus.height,
    skus.weight,
    order_items.quantity
FROM orders
JOIN order_items ON orders.id = order_items.order_id
JOIN skus ON order_items.sku_id = skus.id
WHERE orders.order_id = 'ORD-1000';
```

### 方式2：使用 INNER JOIN（显式指定）

```sql
SELECT 
    o.order_id,
    o.customer,
    o.rsd,
    s.name as sku_name,
    s.length,
    s.width,
    s.height,
    s.weight,
    oi.quantity
FROM orders o
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN skus s ON oi.sku_id = s.id
WHERE o.order_id = 'ORD-1000';
```

（`JOIN` 和 `INNER JOIN` 是等价的）

## 💡 关键概念

### 1. 表别名（Alias）
- `orders o` - `o` 是 `orders` 的别名
- `order_items oi` - `oi` 是 `order_items` 的别名
- `skus s` - `s` 是 `skus` 的别名
- **作用**：简化代码，避免重复写长表名

### 2. JOIN（连接）
- **作用**：将多个表的数据组合在一起
- **类型**：
  - `INNER JOIN`（内连接）：只返回两个表都有匹配的记录
  - `LEFT JOIN`（左连接）：返回左表所有记录，右表没有匹配则显示NULL
  - `RIGHT JOIN`（右连接）：返回右表所有记录，左表没有匹配则显示NULL

### 3. ON 条件
- **作用**：指定两个表如何连接
- `o.id = oi.order_id` - 订单表的ID等于订单明细表的订单ID
- `oi.sku_id = s.id` - 订单明细表的SKU ID等于SKU表的ID

## 🔄 数据流向图

```
orders (订单表)
  │
  │ JOIN: o.id = oi.order_id
  │
  ▼
order_items (订单明细表)
  │
  │ JOIN: oi.sku_id = s.id
  │
  ▼
skus (SKU表)
  │
  │ WHERE: o.order_id = 'ORD-1000'
  │
  ▼
最终结果（订单 + 明细 + SKU信息）
```

## 📚 相关查询

### 查询所有订单的明细（去掉WHERE条件）

```sql
SELECT 
    o.order_id,
    o.customer,
    s.name as sku_name,
    oi.quantity
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN skus s ON oi.sku_id = s.id;
-- 会返回所有订单的明细
```

### 只查询急单（rsd=0）

```sql
SELECT 
    o.order_id,
    o.customer,
    s.name as sku_name,
    oi.quantity
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN skus s ON oi.sku_id = s.id
WHERE o.rsd = 0;  -- 只查询急单
```

### 统计每个订单的商品总数

```sql
SELECT 
    o.order_id,
    o.customer,
    SUM(oi.quantity) as total_quantity
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN skus s ON oi.sku_id = s.id
WHERE o.order_id = 'ORD-1000'
GROUP BY o.order_id, o.customer;
```

