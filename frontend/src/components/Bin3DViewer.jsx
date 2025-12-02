// frontend/src/components/Bin3DViewer.jsx
import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import * as THREE from 'three';

const Box = ({ data }) => {
  return (
    <group position={[data.x / 10, data.y / 10, data.z / 10]}>
      <mesh>
        {/* 几何体：宽 高 深 */}
        <boxGeometry args={[data.w / 10, data.h / 10, data.d / 10]} />
        {/* 材质：颜色 */}
        <meshStandardMaterial color={data.color} transparent opacity={0.9} />
      </mesh>
      {/* 边框线，让箱子更清晰 */}
      <lineSegments>
        <edgesGeometry args={[new THREE.BoxGeometry(data.w / 10, data.h / 10, data.d / 10)]} />
        <lineBasicMaterial color="black" />
      </lineSegments>
    </group>
  );
};

const TruckContainer = () => {
  // 模拟一个半透明的集装箱轮廓
  return (
    <mesh position={[12, 13, 20]}>
      <boxGeometry args={[25, 26, 60]} />
      <meshBasicMaterial color="#e5e7eb" wireframe transparent opacity={0.2} />
    </mesh>
  );
};

const Bin3DViewer = ({ items, vehicleId }) => {
  return (
    <div className="h-full w-full bg-slate-900 rounded-lg overflow-hidden relative">
      <div className="absolute top-4 left-4 z-10 bg-black/50 text-white p-2 rounded backdrop-blur-sm">
        <h3 className="font-bold">🚛 车辆 {vehicleId} 装载视图</h3>
        <p className="text-xs text-gray-300">左键旋转 / 右键平移 / 滚轮缩放</p>
        <div className="mt-2 flex gap-2 text-xs">
          <span className="flex items-center">
            <span className="w-2 h-2 rounded-full bg-blue-500 mr-1"></span>
            Tower Fan
          </span>
          <span className="flex items-center">
            <span className="w-2 h-2 rounded-full bg-green-500 mr-1"></span>
            Air Fryer
          </span>
          <span className="flex items-center">
            <span className="w-2 h-2 rounded-full bg-yellow-500 mr-1"></span>
            Heater
          </span>
        </div>
      </div>
      <Canvas shadows camera={{ position: [40, 40, 40], fov: 50 }}>
        <color attach="background" args={['#1e293b']} />
        
        {/* 控制器 */}
        <OrbitControls makeDefault autoRotate autoRotateSpeed={0.5} />
        
        {/* 灯光 */}
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight position={[50, 50, 50]} angle={0.15} penumbra={1} intensity={2} castShadow />
        
        {/* 场景内容 */}
        <group position={[-10, 0, -20]}>
          {/* 地面网格 */}
          <Grid infiniteGrid fadeDistance={50} sectionColor="#4f46e5" cellColor="#6366f1"/>
          
          {/* 所有的箱子 */}
          {items.map((item) => (
            <Box key={item.id} data={item} />
          ))}
          
          {/* 集装箱外壳 */}
          <TruckContainer />
        </group>
      </Canvas>
    </div>
  );
};

export default Bin3DViewer;



