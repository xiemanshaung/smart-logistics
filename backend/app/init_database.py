"""
数据库初始化脚本
用于在应用启动时创建表结构（如果不存在）
"""
from app.database import engine, Base
from app.db_models import Order, OrderItem, SKU

def init_database():
    """创建所有数据库表"""
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表结构初始化完成")

if __name__ == "__main__":
    init_database()


