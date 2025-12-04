from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.db_service import DatabaseService
from app.modules.packing.estimator import PackingEstimator
from app.modules.vrp.solver import VRPSolver
from app.models.schemas import SolutionResponse

router = APIRouter()

@router.post("/calculate", response_model=SolutionResponse)
async def calculate_logistics_plan(db: Session = Depends(get_db)):
    # 1. 从数据库获取订单数据（替代MockDataGenerator）
    db_service = DatabaseService(db)
    raw_orders = db_service.get_orders(limit=20, status="pending")
    
    # 如果没有订单，返回空结果
    if not raw_orders:
        return SolutionResponse(
            total_distance=0.0,
            total_pallets=0.0,
            routes=[],
            dropped_orders=[],
            locations={}
        )
    
    # 2. 调用装箱模块计算托盘量（从数据库获取SKU信息）
    sku_db = db_service.get_sku_db()
    packer = PackingEstimator(sku_db=sku_db)
    packed_orders = [packer.process(order) for order in raw_orders]
    
    # 3. 调用运筹模块规划路径
    solver = VRPSolver(packed_orders)
    result = solver.solve()
    
    return result

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "DREO Logistics Engine"}

