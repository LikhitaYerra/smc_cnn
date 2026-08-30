import { Suspense, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, PerspectiveCamera, Grid } from '@react-three/drei'
import { HospitalEnvironment } from './HospitalEnvironment'
import { Robot } from './Robot'
import { TrajectoryPath } from './TrajectoryPath'
import { CameraFollow } from './CameraFollow'
import { DisturbanceMarkers } from './DisturbanceMarkers'

import { DualRobots } from './DualRobots'

function SceneContent({ simState, controllerMode, running, config, followCamera, dualCompare }) {
  const robot = simState?.robot || { x: 0, y: 0.5, theta: 0 }
  const pathHistory = simState?.path_history || []
  const desiredPath = simState?.desired_path || []

  return (
    <>
      <PerspectiveCamera makeDefault position={[8, 10, 8]} fov={50} />
      {followCamera ? (
        <CameraFollow target={robot} enabled={followCamera} running={running} />
      ) : (
        <OrbitControls
          enablePan
          enableZoom
          enableRotate
          maxPolarAngle={Math.PI / 2.2}
          minDistance={3}
          maxDistance={25}
          target={[robot.x, 0, robot.y]}
        />
      )}

      <ambientLight intensity={0.3} />
      <directionalLight position={[10, 15, 5]} intensity={1.2} castShadow shadow-mapSize={[2048, 2048]} />
      <hemisphereLight args={['#c0e8ff', '#1a2332', 0.4]} />

      <HospitalEnvironment />
      <DisturbanceMarkers simState={simState} config={config} />

      <Grid
        position={[3, -0.005, 0]}
        args={[30, 16]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#1e3048"
        sectionSize={5}
        sectionThickness={1}
        sectionColor="#2a4a68"
        fadeDistance={30}
        infiniteGrid={false}
      />

      {!dualCompare && (
        <TrajectoryPath pathHistory={pathHistory} desiredPath={desiredPath} controllerMode={controllerMode} />
      )}

      {dualCompare ? (
        <DualRobots dualCompare={dualCompare} />
      ) : (
        <Robot
          position={[robot.x, 0, robot.y]}
          rotation={robot.theta}
          controllerMode={controllerMode}
          running={running}
        />
      )}

      <fog attach="fog" args={['#0a0f1a', 15, 35]} />
    </>
  )
}

export function Scene3D({ simState, controllerMode, running, config, dualCompare }) {
  const [followCamera, setFollowCamera] = useState(true)

  return (
    <div className="scene-container">
      <Canvas shadows gl={{ antialias: true, alpha: false }}>
        <color attach="background" args={['#0a0f1a']} />
        <Suspense fallback={null}>
          <SceneContent
            simState={simState}
            controllerMode={controllerMode}
            running={running}
            config={config}
            followCamera={followCamera}
            dualCompare={dualCompare}
          />
        </Suspense>
      </Canvas>
      <div className="scene-overlay">
        <div className="scene-badge">
          3D Digital Twin
          {running && <span className="live-indicator"> LIVE</span>}
        </div>
        <button
          className={`camera-toggle ${followCamera ? 'active' : ''}`}
          onClick={() => setFollowCamera((f) => !f)}
          title="Toggle camera follow"
        >
          {followCamera ? '📹 Follow' : '🔄 Free'}
        </button>
        {dualCompare && (
          <div className="dual-compare-badge">
            Classical (red) vs CNN (green)
          </div>
        )}
        <div className="scene-coords">
          {simState?.robot
            ? `x: ${simState.robot.x.toFixed(2)}  y: ${simState.robot.y.toFixed(2)}  θ: ${((simState.robot.theta * 180) / Math.PI).toFixed(1)}°`
            : 'Ready'}
        </div>
      </div>
    </div>
  )
}
