"""
数据库连接测试脚本
用于验证数据库配置和连接是否正常
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.db_models import Base, Order, OrderItem, SKU
from app.db_service import DatabaseService

def test_connection():
    """测试数据库连接"""
    try:
        # 测试连接
        with engine.connect() as conn:
            print("✅ 数据库连接成功！")
        
        # 创建表（如果不存在）
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表结构已创建/验证")
        
        # 测试查询
        db = SessionLocal()
        try:
            # 查询SKU数量
            sku_count = db.query(SKU).count()
            print(f"✅ SKU表中有 {sku_count} 条记录")
            
            # 查询订单数量
            order_count = db.query(Order).count()
            print(f"✅ 订单表中有 {order_count} 条记录")
            
            # 查询待处理订单
            pending_orders = db.query(Order).filter(Order.status == 'pending').count()
            print(f"✅ 待处理订单数量: {pending_orders}")
            
            # 测试数据库服务
            db_service = DatabaseService(db)
            orders = db_service.get_orders(limit=5)
            print(f"✅ 数据库服务测试成功，获取到 {len(orders)} 条订单")
            
            if orders:
                print(f"   示例订单: {orders[0].id} - {orders[0].customer}")
            
            sku_db = db_service.get_sku_db()
            print(f"✅ SKU数据库包含 {len(sku_db)} 个SKU")
            if sku_db:
                print(f"   示例SKU: {list(sku_db.keys())[0]}")
            
        finally:
            db.close()
        
        print("\n🎉 所有测试通过！数据库配置正确。")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        print("\n请检查：")
        print("1. PostgreSQL 服务是否已启动 (docker-compose up -d postgres)")
        print("2. 数据库连接配置是否正确 (backend/app/database.py)")
        print("3. 环境变量 DATABASE_URL 是否设置")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)


