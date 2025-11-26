/**
 * 前端主界面：负责输入参数、触发优化、展示结果。
 */
import React, { useState } from 'react';
import api from './api';
import PackingVisualizer from './components/PackingVisualizer';
import './App.css'; // 👈 引入刚才创建的 CSS 文件

// 🎨 车辆路线颜色池
const ROUTE_COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f1c40f'];

export default function App() {
  // --- 状态管理 ---
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // --- 交互参数控制 ---
  const [params, setParams] = useState({
    itemCount: 50,
    vehicleCount: 3,
    containerL: 300,
    containerH: 200,
    containerW: 200
  });

  // --- 核心：触发优化计算 ---
  const handleOptimize = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    // 1. 前端模拟生成随机订单数据
    const mockItems = Array.from({ length: params.itemCount }).map((_, i) => ({
      id: `Order-${i + 1}`,
      w: Math.floor(Math.random() * 40) + 20, 
      h: Math.floor(Math.random() * 40) + 20,
      d: Math.floor(Math.random() * 40) + 20
    }));

    try {
      // 2. 发送给 Python 后端
      const res = await api.post('/api/optimize', {
        items: mockItems,
        container_size: [params.containerL, params.containerH, params.containerW],
        num_vehicles: parseInt(params.vehicleCount),
        num_stops: params.itemCount
      });

      console.log("算法返回结果:", res.data);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError("请求失败：请确保后端 Docker 已启动且网络正常。");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* --- 顶部标题栏 --- */}
      <header className="app-header">
        <h1 className="app-title">📦 智能供应链调度中心</h1>
        <p className="app-subtitle">基于 OR-Tools CVRP & 启发式 3D 装箱算法</p>
      </header>

      {/* --- 控制面板 --- */}
      <div className="controls-panel">
        <div className="input-group">
          <label>订单数量:</label>
          <input 
            type="number" 
            value={params.itemCount}
            onChange={e => setParams({...params, itemCount: Number(e.target.value)})}
          />
        </div>
        <div className="input-group">
          <label>车队数量:</label>
          <input 
            type="number" 
            value={params.vehicleCount}
            onChange={e => setParams({...params, vehicleCount: Number(e.target.value)})}
          />
        </div>
        <button 
          className="btn-primary"
          onClick={handleOptimize} 
          disabled={loading}
        >
          {loading ? '⚡ 算法正在疯狂计算中...' : '🚀 开始智能调度'}
        </button>
      </div>

      {/* --- 错误提示 --- */}
      {error && <div className="error-message">{error}</div>}

      {/* --- 结果展示区 --- */}
      {result && (
        <div className="result-grid">
          
          {/* 左侧：3D 装箱可视化 */}
          <div className="result-card">
            <div className="card-header">
              <h3>🧊 3D 智能装箱 (LBF算法)</h3>
              <span className="status-tag">空间利用率: {result.packing.utilization}%</span>
            </div>
            <div className="visualizer-container">
              <PackingVisualizer data={result.packing} />
            </div>
            <p className="hint-text">* 鼠标左键旋转，右键平移，滚轮缩放</p>
          </div>

          {/* 右侧：VRP 路径规划地图 */}
          <div className="result-card">
            <div className="card-header">
              <h3>🚚 车辆路径规划 (CVRP)</h3>
              <span className="status-tag">车辆数: {result.routing.routes.length}</span>
            </div>
            
            {/* 2D SVG 地图可视化 */}
            <div className="map-container">
              <svg viewBox="-10 -10 120 120" style={{width: '100%', height: '100%'}}>
                {/* 绘制仓库 (原点) */}
                <circle cx="50" cy="50" r="3" fill="black" />
                <text x="50" y="45" fontSize="4" textAnchor="middle" fontWeight="bold">DEPOT</text>

                {/* 绘制客户点 */}
                {result.routing.locations.slice(1).map((loc, i) => (
                  <circle key={i} cx={loc[0]} cy={loc[1]} r="1.5" fill="#ccc" />
                ))}

                {/* 绘制车辆路径 */}
                {result.routing.routes.map((route, vIdx) => {
                  // 构建 SVG 路径 path d="..."
                  const pathData = route.map((nodeIdx, i) => {
                    const [x, y] = result.routing.locations[nodeIdx];
                    return (i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`);
                  }).join(' ');
                  
                  return (
                    <g key={vIdx}>
                      <path 
                        d={pathData} 
                        stroke={ROUTE_COLORS[vIdx % ROUTE_COLORS.length]} 
                        strokeWidth="1" 
                        fill="none" 
                        strokeDasharray="2"
                      />
                      {/* 终点标记 */}
                      <circle 
                        cx={result.routing.locations[route[route.length-2]][0]} 
                        cy={result.routing.locations[route[route.length-2]][1]} 
                        r="2" 
                        fill={ROUTE_COLORS[vIdx % ROUTE_COLORS.length]} 
                      />
                    </g>
                  );
                })}
              </svg>
            </div>

            {/* 文字版路径详情 */}
            <div className="route-list">
              {result.routing.routes.map((route, i) => (
                <div 
                  key={i} 
                  className="route-item"
                  // 这里的 border-left 颜色是动态的，所以保留内联样式
                  style={{ borderLeft: `4px solid ${ROUTE_COLORS[i % ROUTE_COLORS.length]}` }}
                >
                  <strong>Vehicle {i + 1}:</strong>
                  <span> 仓库 ➝ {route.length - 2} 个客户 ➝ 仓库</span>
                </div>
              ))}
            </div>
          </div>

        </div>
      )}
    </div>
  );
}