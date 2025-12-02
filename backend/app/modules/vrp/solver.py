import math
import random
from typing import List
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from app.models.schemas import PackedOrder, SolutionResponse, VehicleRoute, Box3D

class VRPSolver:
    def __init__(self, orders: List[PackedOrder]):
        self.orders = orders
        self.depot_loc = [50, 50] # 仓库位置
        self.num_vehicles = 5
        # 53尺柜通常装26-30托，这里设定容量约束
        self.vehicle_capacity = 26.0 
        # 距离放大系数（OR-Tools需要整数）
        self.scale = 100 

    def _get_distance(self, loc1, loc2):
        dist = math.sqrt((loc1[0]-loc2[0])**2 + (loc1[1]-loc2[1])**2)
        return int(dist * self.scale)

    def _simulate_3d_packing(self, route_orders: List[PackedOrder]) -> List[Box3D]:
        """
        这是一个启发式模拟生成器，用于前端展示。
        它将订单里的 SKU 转换成 3D 坐标，模拟堆叠在 53尺集装箱里。
        
        修复：增加了完整的边界检查，防止箱子溢出集装箱
        """
        boxes = []
        # 集装箱尺寸限制 (简化单位，厘米)
        MAX_WIDTH = 240  
        MAX_HEIGHT = 260
        MAX_DEPTH = 1200  # 假设是 40尺柜长 12米 (1200cm)
        
        current_x = 0
        current_y = 0
        current_z = 0
        row_max_depth = 0
        layer_max_height = 0  # 记录这一层最高的箱子
        
        # 颜色库
        colors = {
            "Tower_Fan_Pilot": "#3b82f6", 
            "Air_Fryer_Pro": "#10b981", 
            "Heater_Solaris": "#f59e0b"
        }
        
        for order in route_orders:
            for sku_name, qty in order.items.items():
                # 获取 SKU 尺寸 (从 mock generator 拿，或者这里硬编码简化)
                # 为了演示效果，我们稍微随机化尺寸
                w, h, d = 0, 0, 0
                if "Tower" in sku_name: 
                    w, h, d = 30, 110, 30
                elif "Fryer" in sku_name: 
                    w, h, d = 35, 35, 40
                else: 
                    w, h, d = 25, 60, 25
                
                # 限制数量，防止前端渲染太卡
                display_qty = min(qty, 10) 
                
                for i in range(display_qty):
                    # 1. 判断 X 轴（宽度）是否满了 -> 换行
                    if current_x + w > MAX_WIDTH:
                        current_x = 0
                        current_z += row_max_depth + 2
                        row_max_depth = 0  # 重置行深
                    
                    # 2. 【修复】判断 Z 轴（深度/长度）是否满了 -> 换层
                    if current_z + d > MAX_DEPTH:
                        current_z = 0
                        current_x = 0
                        current_y += layer_max_height + 5  # 加5cm间隙
                        layer_max_height = 0  # 重置层高
                        row_max_depth = 0  # 重置行深
                    
                    # 3. 【修复】判断 Y 轴（高度）是否满了 -> 爆柜了（虽然VRP控制了总量，但模拟摆放可能不优）
                    if current_y + h > MAX_HEIGHT:
                        # 简单的处理：不再渲染溢出的箱子
                        # 在实际生产环境中，这里应该触发警告或重新计算装箱方案
                        continue
                    
                    # 简单的堆叠逻辑
                    boxes.append(Box3D(
                        id=f"{order.id}-{sku_name}-{random.randint(1000,9999)}",
                        sku_name=sku_name,
                        color=colors.get(sku_name, "#6b7280"),
                        x=current_x + w/2,  # 中心点坐标
                        y=current_y + h/2,  # 从地面开始堆叠
                        z=current_z + d/2,
                        w=w, h=h, d=d
                    ))
                    
                    current_x += w + 2  # 留点缝隙
                    row_max_depth = max(row_max_depth, d + 2)
                    layer_max_height = max(layer_max_height, h)  # 更新层高
                    
        return boxes

    def solve(self) -> SolutionResponse:
        # 1. 准备数据
        locations = [self.depot_loc] + [o.location for o in self.orders]
        # 托盘需求量放大10倍转整数处理 (因为capacity是26.0)
        demands = [0] + [int(o.pallets_needed * 10) for o in self.orders]
        
        manager = pywrapcp.RoutingIndexManager(len(locations), self.num_vehicles, 0)
        routing = pywrapcp.RoutingModel(manager)
        
        # 2. 距离回调
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self._get_distance(locations[from_node], locations[to_node])

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # 3. 容量约束 (CVRP)
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return demands[from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            [int(self.vehicle_capacity * 10)] * self.num_vehicles,
            True,  # start cumul to zero
            "Capacity"
        )

        # 4. RSD 软约束 (惩罚机制)
        # 如果 RSD=0 (急单)，设置极高的惩罚值，迫使必须配送
        for i, order in enumerate(self.orders):
            node_index = manager.NodeToIndex(i + 1)
            penalty = 10000000 if order.rsd == 0 else 1000
            routing.AddDisjunction([node_index], penalty)

        # 5. 求解
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
        search_parameters.time_limit.seconds = 2
        solution = routing.SolveWithParameters(search_parameters)

        # 6. 解析结果
        return self._format_solution(manager, routing, solution)

    def _format_solution(self, manager, routing, solution) -> SolutionResponse:
        routes = []
        total_dist = 0
        total_load = 0
        dropped = []
        
        # 新增：构建坐标映射表
        location_map = {}
        # 1. 添加仓库坐标 (固定为 DEPOT)
        location_map["DEPOT"] = self.depot_loc
        # 2. 添加所有订单坐标
        for order in self.orders:
            location_map[order.id] = order.location
        
        if not solution:
            return SolutionResponse(
                total_distance=0, 
                total_pallets=0, 
                routes=[], 
                dropped_orders=[],
                locations=location_map  # 返回空结果时也带上坐标
            )

        # 准备所有位置（仓库 + 订单位置）
        locations = [self.depot_loc] + [o.location for o in self.orders]
        
        # 坐标映射函数：将 0-100 的相对坐标映射到加州地图
        DEPOT_LAT = 34.0522  # 洛杉矶纬度
        DEPOT_LNG = -118.2437  # 洛杉矶经度
        
        def map_coordinate(loc):
            """将相对坐标转换为经纬度
            修复：让点往内陆（东北方向）偏移，避免下海
            洛杉矶往西是太平洋，所以主要往东（经度增加）和往北（纬度增加）偏移
            """
            return [
                DEPOT_LAT + (loc[1] - 20) * 0.08,  # 纬度：主要往北 (20-100 -> 正偏移)
                DEPOT_LNG + (loc[0] - 20) * 0.08   # 经度：主要往东 (20-100 -> 正偏移)
            ]

        # 提取路线
        for vehicle_id in range(self.num_vehicles):
            index = routing.Start(vehicle_id)
            route_path_ids = []
            route_coordinates = []
            route_dist = 0
            route_load = 0
            has_urgent = False
            vehicle_orders = []  # 收集这辆车装的所有订单
            
            # 从仓库开始
            route_coordinates.append(map_coordinate(self.depot_loc))
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                if node_index != 0:
                    order = self.orders[node_index - 1]
                    route_path_ids.append(f"{order.id}({order.pallets_needed}托)")
                    route_load += order.pallets_needed
                    vehicle_orders.append(order)  # 收集订单
                    # 添加订单坐标
                    route_coordinates.append(map_coordinate(order.location))
                    if order.rsd == 0:
                        has_urgent = True
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                if previous_index != index:
                    route_dist += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
            # 回到仓库
            route_coordinates.append(map_coordinate(self.depot_loc))
            
            if route_path_ids:
                total_dist += route_dist
                total_load += route_load
                
                # 生成 3D 装箱数据
                packed_boxes = self._simulate_3d_packing(vehicle_orders)
                
                routes.append(VehicleRoute(
                    vehicle_id=vehicle_id + 1,
                    route_path=route_path_ids,
                    load_percent=round((route_load / self.vehicle_capacity) * 100, 2),
                    distance=round(route_dist / self.scale, 2),
                    is_urgent_covered=has_urgent,
                    coordinates=route_coordinates,
                    packed_items=packed_boxes  # 注入 3D 数据
                ))

        # 检查未配送订单（通过检查是否在已分配的路线中）
        assigned_nodes = set()
        for route in routes:
            for path_str in route.route_path:
                # 从路径字符串中提取订单ID（格式：ORD-1000(2.5托)）
                order_id = path_str.split('(')[0]
                assigned_nodes.add(order_id)
        
        for order in self.orders:
            if order.id not in assigned_nodes:
                dropped.append(order.id)

        return SolutionResponse(
            total_distance=round(total_dist / self.scale, 2),
            total_pallets=round(total_load, 2),
            routes=routes,
            dropped_orders=dropped,
            locations=location_map  # 新增：返回坐标数据
        )

