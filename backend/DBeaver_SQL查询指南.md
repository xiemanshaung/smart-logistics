# DBeaver SQL 查询操作指南

## 方法一：使用 SQL 编辑器（最常用）

### 步骤：

1. **打开 SQL 编辑器**
   - 方式1：菜单栏 → `SQL 编辑器` → `新建 SQL 编辑器`
   - 方式2：快捷键 `Ctrl + \` (反引号)
   - 方式3：工具栏点击 SQL 编辑器图标（通常是一个文档图标）

2. **选择数据库连接**
   - 在 SQL 编辑器顶部，有一个下拉菜单
   - 选择 `dreo_logistics` 或 `public@dreo_logistics`

3. **输入 SQL 语句**
   ```sql
   SELECT * FROM skus;
   ```

4. **执行查询**
   - 选中要执行的 SQL 语句（或全选 `Ctrl+A`）
   - 点击工具栏的"执行 SQL 语句"按钮（▶️ 播放图标）
   - 或使用快捷键：`Ctrl+Enter`
   - 或使用快捷键：`Alt+X`

5. **查看结果**
   - 结果会显示在编辑器下方的"数据"标签页
   - 可以切换查看"文本"、"网格"等不同格式

## 方法二：在数据视图中使用 SQL 过滤

1. **打开表数据**
   - 在数据库导航器中，展开 `dreo_logistics` → `public` → `表`
   - 右键点击表名（如 `orders`）
   - 选择 `查看数据` 或 `编辑数据`

2. **使用 SQL 过滤**
   - 在数据视图顶部，有一个输入框
   - 提示文字："输入一个SQL 表达式来过滤结果(使用Ctrl+Space)"
   - 输入过滤条件，如：`status = 'pending'`
   - 按 `Enter` 执行

## 方法三：右键菜单执行 SQL

1. **创建 SQL 脚本**
   - 在数据库导航器中，右键点击 `dreo_logistics` 数据库
   - 选择 `SQL 编辑器` → `新建 SQL 脚本`

2. **输入并执行**
   - 输入 SQL 语句
   - 使用 `Ctrl+Enter` 执行

## 常用 SQL 查询示例

### 1. 查看所有 SKU
```sql
SELECT * FROM skus;
```

### 2. 查看待处理订单
```sql
SELECT * FROM orders WHERE status = 'pending';
```

### 3. 查看订单详情（包含SKU信息）
```sql
SELECT 
    o.order_id,
    o.customer,
    o.rsd,
    s.name as sku_name,
    oi.quantity
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN skus s ON oi.sku_id = s.id
WHERE o.status = 'pending';
```

### 4. 统计每个订单的商品数量
```sql
SELECT 
    o.order_id,
    o.customer,
    COUNT(oi.id) as item_count,
    SUM(oi.quantity) as total_quantity
FROM orders o
LEFT JOIN order_items oi ON o.id = oi.order_id
GROUP BY o.id, o.order_id, o.customer
ORDER BY o.created_at DESC;
```

### 5. 查看订单的完整信息（包含所有SKU）
```sql
SELECT 
    o.order_id,
    o.customer,
    o.rsd,
    o.location_x,
    o.location_y,
    o.status,
    s.name as sku_name,
    s.length,
    s.width,
    s.height,
    s.weight,
    oi.quantity
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN skus s ON oi.sku_id = s.id
WHERE o.status = 'pending'
ORDER BY o.order_id, s.name;
```

## 快捷键参考

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + \` | 打开 SQL 编辑器 |
| `Ctrl + Enter` | 执行选中的 SQL |
| `Alt + X` | 执行选中的 SQL |
| `Ctrl + Space` | SQL 自动补全 |
| `Ctrl + Shift + F` | 格式化 SQL |
| `F5` | 刷新数据 |

## 提示

1. **多语句执行**：可以一次输入多个 SQL 语句，用分号 `;` 分隔，DBeaver 会依次执行

2. **结果导出**：在查询结果区域，右键可以选择"导出数据"，支持导出为 CSV、Excel、JSON 等格式

3. **保存 SQL 脚本**：可以将常用的 SQL 保存为脚本文件，方便重复使用

4. **SQL 历史**：DBeaver 会保存 SQL 执行历史，可以通过历史记录快速重用之前的查询

