"""
Simplified 3D Bin Packing heuristic.

使用 First Fit Decreasing 思路，为演示提供可视化坐标。
"""

class Item:
    """用于求解的货物数据结构"""

    def __init__(self, id, w, h, d, color):
        self.id = id
        self.w = w  # width (x)
        self.h = h  # height (y)
        self.d = d  # depth (z)
        self.color = color
        self.position = None  # (x, y, z)
        self.rotation = 0     # 预留字段：0 代表未旋转


class BinPackingSolver:
    """简单的启发式 3D 装箱求解器"""

    def __init__(self, container_size=(300, 200, 200)):  # L, H, W
        self.L, self.H, self.W = container_size
        self.packed_items = []

    def check_collision(self, item, x, y, z):
        """
        判断 item 放在 (x, y, z) 时是否越界或与其他物体发生碰撞。
        使用 AABB（Axis-Aligned Bounding Box）检测。
        """
        # 边界检查：任一方向超出箱体即可判定冲突
        if x + item.w > self.L or y + item.h > self.H or z + item.d > self.W:
            return True

        # 与已放置物体逐个碰撞检测
        for other in self.packed_items:
            ox, oy, oz = other.position
            if (
                x < ox + other.w and x + item.w > ox and
                y < oy + other.h and y + item.h > oy and
                z < oz + other.d and z + item.d > oz
            ):
                return True
        return False

    def solve(self, items):
        """
        核心求解流程：
        1. 先按体积从大到小排序（更容易填满空间）
        2. 维护潜在放置点集合，依次尝试直到放置成功
        3. 每放入一个物体，就在其右/上/前生成新的潜在点
        """
        # 启发式策略：按体积从大到小排序 (First Fit Decreasing)
        items.sort(key=lambda x: x.w * x.h * x.d, reverse=True)

        # 潜在放置点集合（初始化为原点）
        potential_points = [(0, 0, 0)]

        for item in items:
            placed = False
            # 让候选点按 “靠左、靠下、靠前” 排序，模拟人工装箱习惯
            potential_points.sort(key=lambda p: (p[0], p[1], p[2]))

            for x, y, z in potential_points:
                if not self.check_collision(item, x, y, z):
                    item.position = (x, y, z)
                    self.packed_items.append(item)
                    placed = True

                    # 新增潜在点：放在刚放好的物体右侧、上方、前方
                    potential_points.append((x + item.w, y, z))
                    potential_points.append((x, y + item.h, z))
                    potential_points.append((x, y, z + item.d))
                    break

            if not placed:
                print(f"Item {item.id} could not be packed.")

        # 将内部对象转换为前端可渲染的数据格式
        return [
            {
                "id": i.id,
                "dims": [i.w, i.h, i.d],
                "pos": i.position,
                "color": i.color,
            }
            for i in self.packed_items
        ]