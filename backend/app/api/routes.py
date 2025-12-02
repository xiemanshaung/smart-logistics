from fastapi import APIRouter
from app.modules.mock.generator import MockDataGenerator
from app.modules.packing.estimator import PackingEstimator
from app.modules.vrp.solver import VRPSolver
from app.models.schemas import SolutionResponse

router = APIRouter()

@router.post("/calculate", response_model=SolutionResponse)
async def calculate_logistics_plan():
    # 1. 获取(模拟)订单数据
    raw_orders = MockDataGenerator.generate_orders(20)
    
    # 2. 调用装箱模块计算托盘量
    packer = PackingEstimator()
    packed_orders = [packer.process(order) for order in raw_orders]
    
    # 3. 调用运筹模块规划路径
    solver = VRPSolver(packed_orders)
    result = solver.solve()
    
    return result

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "DREO Logistics Engine"}

