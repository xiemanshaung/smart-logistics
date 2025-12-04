# Mock 数据模块（已废弃）

⚠️ **注意**：此模块已不再使用，项目已迁移到数据库模式。

## 迁移说明

- **旧方式**：使用 `MockDataGenerator.generate_orders()` 生成模拟数据
- **新方式**：使用 `DatabaseService.get_orders()` 从 PostgreSQL 数据库读取数据

## 如何获取数据

现在请使用以下方式：

1. **通过 DBeaver**：直接在数据库中插入订单和SKU数据
2. **通过 API**：系统会自动从数据库读取 `status='pending'` 的订单

详细说明请参考：
- `backend/DBeaver连接指南.md`
- `backend/app/db_service.py`


