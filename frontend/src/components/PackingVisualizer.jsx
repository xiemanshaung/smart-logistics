import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import * as THREE from 'three';

// 单个货物立方体
const Box = ({ position, dims, color, id }) => {
  // Three.js 以立方体中心为锚点，而求解器返回的是左下角坐标
  // 因此需要把 (x, y, z) 平移半个尺寸，让物体显示在正确位置
  const [w, h, d] = dims;
  const [x, y, z] = position;

  const centerPos = [x + w / 2, y + h / 2, z + d / 2];

  return (
    <mesh position={centerPos}>
      <boxGeometry args={[w, h, d]} />
      <meshStandardMaterial color={color} opacity={0.9} transparent />
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(w, h, d)]} />
        <lineBasicMaterial color="black" />
      </lineSegments>
    </mesh>
  );
};

// 箱体的线框（供参考）
const ContainerFrame = ({ dims }) => {
  const [L, H, W] = dims;
  return (
    <mesh position={[L / 2, H / 2, W / 2]}>
      <boxGeometry args={[L, H, W]} />
      <meshBasicMaterial color="#ccc" wireframe />
    </mesh>
  );
};

export default function PackingVisualizer({ data }) {
  if (!data) return <div className="placeholder">等待计算数据...</div>;

  return (
    <div style={{ height: '500px', width: '100%', background: '#111' }}>
      {/* React Three Fiber 渲染区域 */}
      <Canvas camera={{ position: [400, 300, 400], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[100, 100, 100]} />
        <OrbitControls />
        <gridHelper args={[1000, 20]} />

        {/* 集装箱线框 */}
        <ContainerFrame dims={data.container} />

        {/* 货物实体 */}
        {data.items.map((item, idx) => (
          <Box 
            key={idx} 
            position={item.pos} 
            dims={item.dims} 
            color={item.color} 
            id={item.id} 
          />
        ))}
      </Canvas>
      <div style={{ color: 'white', padding: '10px' }}>
        空间利用率: {data.utilization}%
      </div>
    </div>
  );
}