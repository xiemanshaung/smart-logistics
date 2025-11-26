from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import math

def create_data_model(num_vehicles, locations):
    """
    准备 VRP 算法所需的数据
    """
    data = {}
    data['locations'] = locations
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0

    # --- 核心修改：添加 CVRP 容量数据，防止一辆车跑完所有点 ---
    
    # 1. 定义需求量 (Demands)
    # 仓库需求为0，其他客户点需求为 1
    num_locations = len(locations)
    data['demands'] = [0] + [1] * (num_locations - 1)

    # 2. 定义车辆容量 (Vehicle Capacities)
    # 动态计算：让总容量仅比总需求多一点点 (1.2倍)，迫使算法必须使用多辆车
    total_demand = sum(data['demands'])
    
    if num_vehicles > 0:
        avg_demand = total_demand / num_vehicles
        # 向上取整并留 20% 余量
        capacity_per_vehicle = math.ceil(avg_demand * 1.2)
        # 兜底：防止容量过小无法配送
        capacity_per_vehicle = max(int(capacity_per_vehicle), 5)
    else:
        capacity_per_vehicle = 100 

    data['vehicle_capacities'] = [capacity_per_vehicle] * num_vehicles

    print(f"🔍 [VRP Debug] Total Demand: {total_demand}, Vehicles: {num_vehicles}, Cap/Truck: {capacity_per_vehicle}")
    
    return data

def compute_euclidean_distance_matrix(locations):
    """
    计算欧氏距离矩阵 (作为 OSRM 失败时的备选)
    返回 List[List[int]] 格式，保持与 OSRM 格式一致
    """
    size = len(locations)
    matrix = [[0] * size for _ in range(size)]
    
    for i in range(size):
        for j in range(size):
            if i == j:
                matrix[i][j] = 0
            else:
                # 粗略估算：1度 ≈ 111km = 111000米
                # 这只是个估值，用来做 Fallback 足够了
                dist = math.hypot(
                    locations[i][0] - locations[j][0],
                    locations[i][1] - locations[j][1]
                ) * 111000
                matrix[i][j] = int(dist)
    return matrix

def solve_vrp(num_vehicles, locations, external_matrix=None):
    """
    求解 VRP 问题
    :param external_matrix: 外部传入的真实距离矩阵 (OSRM)
    """
    # 1. 创建数据模型
    data = create_data_model(num_vehicles, locations)

    # 2. 创建路由索引管理器
    manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])

    # 3. 创建路由模型
    routing = pywrapcp.RoutingModel(manager)

    # 4. 确定距离矩阵 (OSRM vs Euclidean)
    if external_matrix:
        distance_matrix = external_matrix
    else:
        distance_matrix = compute_euclidean_distance_matrix(data['locations'])

    # 5. 注册距离回调
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # List[List] 和 Dict[Dict] 的访问方式是一样的 [i][j]
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # 6. 设置每条边的成本
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # --- 核心修改：添加容量约束 (Capacity Constraint) ---
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null_capacity_slack
        data['vehicle_capacities'],  # 车辆容量数组
        True,  # start_cumul_to_zero
        'Capacity'
    )
    # -----------------------------------------------

    # 7. 设置搜索策略 (使用引导式局部搜索以跳出局部最优)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    # 开启 GLOP (Guided Local Search) 让结果更均衡
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.seconds = 1  # 限制计算时间

    # 8. 求解
    solution = routing.SolveWithParameters(search_parameters)

    # 9. 格式化输出
    routes = []
    if solution:
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            
            # 添加终点 (仓库)
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            
            # 过滤：如果路径长度<=2 (只有仓库->仓库)，说明这辆车没干活
            if len(route) > 2:
                routes.append(route)
    
    return routes