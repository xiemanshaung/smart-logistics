"""
Thin wrapper around OSRM table API.

提供距离矩阵和耗时矩阵，便于 VRP/调度模块调用。
"""

import requests
from typing import List, Tuple, Dict


class OSRMService:
    """负责与 OSRM 服务通信的客户端"""

    def __init__(self, osrm_host: str = "http://osrm:5000"):
        # 在 docker-compose 的网络中可以直接使用服务名称 `osrm`
        self.osrm_host = osrm_host

    def get_distance_matrix(self, coordinates: List[Tuple[float, float]]) -> Dict:
        """
        请求 OSRM table 接口，获取两两坐标之间的距离/耗时矩阵。

        Args:
            coordinates: [(lat, lng), ...] 采用常见的 Google Lat/Lng 顺序

        Returns:
            dict: {"distances": [[..]], "durations": [[..]]}；如失败返回空 dict
        """
        if not coordinates:
            return {}

        # 1. 坐标转换：OSRM 要求经度在前，因此需要将 (lat, lng) -> (lng, lat)
        coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordinates])

        # 2. 构造 table API URL，annotations 参数可一次性返回距离和耗时
        url = f"{self.osrm_host}/table/v1/driving/{coords_str}?annotations=distance,duration"

        try:
            print(f"🚀 [OSRM] Requesting matrix for {len(coordinates)} points...")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == "Ok":
                return {
                    "distances": data["distances"],  # 单位：米
                    "durations": data["durations"],  # 单位：秒
                }
            print(f"❌ OSRM Error Code: {data.get('code')}")
            return {}
        except Exception as e:
            print(f"❌ Failed to connect to OSRM: {e}")
            # 若 OSRM 不可用，返回空，交由上层决定是否使用欧氏距离等降级方案
            return {}