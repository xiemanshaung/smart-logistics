import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import axios from 'axios';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css'; // 确保引入 CSS
import Bin3DViewer from './components/Bin3DViewer';

// 修复 Leaflet 默认图标不显示的问题
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

// 仓库图标 (红色)
const depotIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// 客户图标 (蓝色)
const customerIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

// 基础锚点 (洛杉矶)，所有的相对坐标都基于这个点偏移
const BASE_ANCHOR = [34.0522, -118.2437]; 
const COLORS = ['#2563eb', '#16a34a', '#9333ea', '#ea580c', '#000000'];

// 修改坐标映射函数：
// 后端返回的是 [x, y] (0-100)，我们需要把它映射成 [lat, lng]
const mapCoordinate = (loc) => {
    if (!loc) return BASE_ANCHOR;
    const [x, y] = loc; 
    // 简单的线性投影：x 对应经度，y 对应纬度
    // 0.05 是缩放系数，让 0-100 的范围在地图上铺开约 500km
    return [
        BASE_ANCHOR[0] + (y - 20) * 0.08,  // 纬度：主要往北
        BASE_ANCHOR[1] + (x - 20) * 0.08   // 经度：主要往东
    ];
};

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState(null);  // 新增：控制 3D 弹窗的状态
  // 新增：专门存储仓库的地图坐标
  const [depotPosition, setDepotPosition] = useState(BASE_ANCHOR);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
      const response = await axios.post(`${apiUrl}/calculate`);
      const result = response.data;
      setData(result);
      
      // 核心修复：更新仓库的实际位置
      if (result.locations && result.locations["DEPOT"]) {
          const realDepotPos = mapCoordinate(result.locations["DEPOT"]);
          setDepotPosition(realDepotPos);
      }
    } catch (error) {
      console.error("API Error:", error);
      alert("调度计算失败，请检查后端服务！");
    }
    setLoading(false);
  };

  return (
    <div className="flex h-screen flex-col relative">
      {/* 3D 视图弹窗 (Modal) */}
      {selectedVehicle && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm p-10">
          <div className="bg-white w-full h-full max-w-6xl max-h-[80vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden relative">
            {/* 关闭按钮 */}
            <button 
              onClick={() => setSelectedVehicle(null)}
              className="absolute top-4 right-4 z-50 bg-white/10 hover:bg-white/20 text-white rounded-full p-2 transition"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            
            {/* 3D 组件 */}
            <Bin3DViewer items={selectedVehicle.packed_items || []} vehicleId={selectedVehicle.vehicle_id} />
          </div>
        </div>
      )}

      <header className="bg-slate-900 text-white p-4 shadow-md flex justify-between items-center z-50 relative">
        <div>
          <h1 className="text-xl font-bold tracking-wider">智能履约调度系统</h1>
          <p className="text-xs text-slate-400">VRP Path Optimization & 3D Packing Engine</p>
        </div>
        <button 
          onClick={handleCalculate}
          disabled={loading}
          className={`px-6 py-2 rounded font-bold transition-all shadow-lg ${
            loading ? 'bg-slate-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 hover:scale-105'
          }`}
        >
          {loading ? '正在计算全局最优解...' : '开始智能排程'}
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* 左侧看板 */}
        <div className="w-1/3 bg-white border-r p-6 overflow-y-auto shadow-2xl z-10">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-1 h-6 bg-blue-600 rounded"></div>
            <h2 className="text-lg font-bold text-slate-800">调度结果看板</h2>
          </div>
          
          {!data ? (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400 border-2 border-dashed border-slate-200 rounded-xl">
              <p>等待数据输入...</p>
              <p className="text-xs mt-2">点击右上角按钮启动计算</p>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                  <p className="text-blue-600 text-xs font-semibold uppercase">总发货托盘</p>
                  <p className="text-3xl font-extrabold text-slate-800 mt-1">{data.total_pallets} <span className="text-sm font-normal text-slate-500">托</span></p>
                </div>
                <div className="bg-emerald-50 p-4 rounded-xl border border-emerald-100">
                  <p className="text-emerald-600 text-xs font-semibold uppercase">预估总里程</p>
                  <p className="text-3xl font-extrabold text-slate-800 mt-1">{data.total_distance} <span className="text-sm font-normal text-slate-500">km</span></p>
                </div>
              </div>

              <div>
                <h3 className="font-bold text-slate-800 mb-3">车辆调度详情 (Prepaid)</h3>
                <p className="text-xs text-slate-400 mb-2">点击卡片查看 3D 装载方案</p>
                <div className="space-y-4">
                  {data.routes.map((route, idx) => (
                    <div 
                      key={idx} 
                      onClick={() => setSelectedVehicle(route)}
                      className="border border-slate-200 rounded-xl p-4 hover:border-blue-500 hover:shadow-lg hover:scale-[1.02] cursor-pointer transition-all bg-white group"
                    >
                      <div className="flex justify-between items-center mb-3">
                        <div className="flex items-center gap-2">
                          <span className="w-3 h-3 rounded-full" style={{backgroundColor: COLORS[idx % COLORS.length]}}></span>
                          <span className="font-bold text-slate-700 group-hover:text-blue-600">车辆 {route.vehicle_id}</span>
                          {/* 3D 图标 */}
                          <span className="bg-slate-100 text-slate-500 text-[10px] px-1.5 py-0.5 rounded border border-slate-200">3D视图</span>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          route.load_percent > 90 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                        }`}>
                          装载率: {route.load_percent}%
                        </span>
                      </div>
                      <div className="text-sm text-slate-600 space-y-1">
                        <p>行驶里程: <span className="font-mono">{route.distance} km</span></p>
                        <p>包含急单: {route.is_urgent_covered ? <span className="text-red-500 font-bold">是 (RSD优先)</span> : '否'}</p>
                      </div>
                      <div className="mt-3 pt-3 border-t border-slate-100">
                        <p className="text-xs text-slate-400 mb-1">配送路径:</p>
                        <div className="text-xs text-slate-500 leading-relaxed font-mono">
                          {route.route_path.map(stop => stop.split('(')[0]).join(' → ')}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {data.dropped_orders.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">⚠️</span>
                    <h4 className="text-red-800 font-bold text-sm">运力不足预警</h4>
                  </div>
                  <p className="text-xs text-red-600 mb-2">以下订单被延后处理 (RSD=1):</p>
                  <div className="flex flex-wrap gap-1">
                    {data.dropped_orders.map(id => (
                      <span key={id} className="px-1.5 py-0.5 bg-red-100 text-red-700 rounded text-[10px] font-mono">{id}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 右侧地图 */}
        <div className="w-2/3 h-full relative z-0">
          <MapContainer center={BASE_ANCHOR} zoom={9} scrollWheelZoom={true} className="h-full w-full">
            <TileLayer
              attribution='&copy; OpenStreetMap contributors'
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />
            
            {/* 核心修复：仓库 Marker 使用动态坐标 depotPosition */}
            <Marker position={depotPosition} icon={depotIcon}>
              <Popup>DREO 中心仓库 (Depot)</Popup>
            </Marker>

            {/* 绘制路线 */}
            {data && data.routes.map((route, idx) => {
              const routeColor = COLORS[idx % COLORS.length];
              
              // 1. 起点必须是仓库
              const positions = [depotPosition];
              
              const markers = route.route_path.map((stop, i) => {
                // stop 格式如 "ORD-1001(2.5托)"
                const id = stop.split('(')[0];
                
                // 2. 从后端返回的 locations 中获取坐标
                const rawLoc = data.locations && data.locations[id]; 
                if (!rawLoc) return null;

                const pos = mapCoordinate(rawLoc);
                positions.push(pos); // 加入路径点
                
                return (
                  <Marker key={`${route.vehicle_id}-${i}`} position={pos} icon={customerIcon}>
                    <Popup>
                      <strong>{id}</strong><br/>
                      需配送: {stop.split('(')[1]?.replace(')', '') || 'N/A'}<br/>
                      车辆: {route.vehicle_id}
                    </Popup>
                  </Marker>
                );
              });
              
              // 3. 终点回到仓库 (形成闭环)
              positions.push(depotPosition);
              
              return (
                <div key={idx}>
                  {markers}
                  {positions.length > 1 && (
                    <Polyline 
                      positions={positions} 
                      pathOptions={{ color: routeColor, weight: 4, opacity: 0.7 }} 
                    />
                  )}
                </div>
              );
            })}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}

export default App
