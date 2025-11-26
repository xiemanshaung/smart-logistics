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

    # --- 核心修改：添加 CVRP 容量数据 ---
    
    # 1. 定义每个地点的“需求量” (Demands)
    # 规则：仓库(索引0)需求为0，其他所有客户点需求假设为 1 个单位
    # (实际业务中，这里可以是包裹的重量、体积或数量)
    num_locations = len(locations)
    data['demands'] = [0] + [1] * (num_locations - 1)

    # 2. 定义每辆车的“最大载重” (Vehicle Capacities)
    # 逻辑：为了让多辆车都动起来，我们不能给无限容量。
    # 我们动态计算：让每辆车的容量大约等于 (总需求 / 车辆数) * 1.2
    # 这样一辆车肯定装不完，必须派其他车。
    total_demand = sum(data['demands'])
    
    if num_vehicles > 0:
        # 动态计算容量，保留 20% 的余量 (Buffer)
        avg_demand = total_demand / num_vehicles
        capacity_per_vehicle = math.ceil(avg_demand * 1.2)
        # 兜底：防止容量过小
        capacity_per_vehicle = max(int(capacity_per_vehicle), 5)
    else:
        capacity_per_vehicle = 100 # Fallback

    data['vehicle_capacities'] = [capacity_per_vehicle] * num_vehicles

    print(f"🔍 [VRP Debug] Total Demand: {total_demand}, Vehicles: {num_vehicles}, Cap/Truck: {capacity_per_vehicle}")
    
    return data

def compute_euclidean_distance_matrix(locations):
    """
    计算欧氏距离矩阵 (作为 OSRM 失败时的备选)
    """
    distances = {}
    for from_counter, from_node in enumerate(locations):
        distances[from_counter] = {}
        for to_counter, to_node in enumerate(locations):
            if from_counter == to_counter:
                distances[from_counter][to_counter] = 0
            else:
                # 欧氏距离公式：sqrt((x1-x2)^2 + (y1-y2)^2)
                # 乘以 1000 是为了放大数值，避免 int 截断太严重
                distances[from_counter][to_counter] = int(math.hypot(
                    from_node[0] - to_node[0],
                    from_node[1] - to_node[1]
                ) * 1000)
    return distances

def solve_vrp(num_vehicles, locations, external_matrix=None):
    """
    求解 VRP 问题
    :param external_matrix: 如果有外部(如OSRM)提供的真实距离矩阵，则优先使用
    """
    # 1. 创建数据模型
    data = create_data_model(num_vehicles, locations)

    # 2. 创建路由索引管理器
    manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])

    # 3. 创建路由模型
    routing = pywrapcp.RoutingModel(manager)

    # 4. 定义距离回调函数
    if external_matrix:
        # 使用外部传入的真实矩阵 (OSRM)
        distance_matrix = external_matrix
    else:
        # 使用内部计算的欧氏距离
        distance_matrix = compute_euclidean_distance_matrix(data['locations'])

    def distance_callback(from_index, to_index):
        # 将 RoutingIndex 转换为 NodeIndex
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # 定义每条边的成本 (这里成本 = 距离)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # --- 核心修改：添加容量约束 (Capacity Constraint) ---
    def demand_callback(from_index):
        """返回当前节点的需求量"""
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null_capacity_slack: 容量松弛度 (通常为0)
        data['vehicle_capacities'],  # 每辆车的容量上限数组
        True,  # start_cumul_to_zero: 起点累积量是否强制为0
        'Capacity'  # 维度名称
    )
    # -----------------------------------------------

    # 5. 设置搜索策略 (使用引导式局部搜索 Guided Local Search 以跳出局部最优)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    
    # 开启局部搜索 (Metaheuristic) - 这样结果会更均衡
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    # 限制计算时间 (防止算太久)
    search_parameters.time_limit.seconds = 1

    # 6. 求解
    solution = routing.SolveWithParameters(search_parameters)

    # 7. 格式化输出结果
    routes = []
    if solution:
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = []
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                index = solution.Value(routing.NextVar(index))
            
            # 添加终点 (回到仓库)
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            
            # 只有当车辆确实跑了客户才加入结果 (过滤掉没干活的车)
            if len(route) > 2:
                routes.append(route)
    
    return routes