import { useMemo } from 'react'
import * as THREE from 'three'

export function TrajectoryPath({ pathHistory = [], desiredPath = [], controllerMode = 'cnn_adaptive' }) {
  const colors = {
    classical: '#ff6b6b',
    cnn_adaptive: '#00d4aa',
    rl_agent: '#7c5cff',
  }
  const color = colors[controllerMode] || '#00d4aa'

  const actualPoints = useMemo(() => {
    if (pathHistory.length < 2) return null
    const pts = pathHistory.map((p) => new THREE.Vector3(p.x, 0.05, p.y))
    return new THREE.CatmullRomCurve3(pts)
  }, [pathHistory])

  const desiredPoints = useMemo(() => {
    if (desiredPath.length < 2) return null
    const pts = desiredPath.map((p) => new THREE.Vector3(p.x, 0.03, p.y))
    return new THREE.CatmullRomCurve3(pts)
  }, [desiredPath])

  const actualGeometry = useMemo(() => {
    if (!actualPoints) return null
    return new THREE.TubeGeometry(actualPoints, Math.max(pathHistory.length, 2), 0.02, 8, false)
  }, [actualPoints, pathHistory.length])

  const desiredGeometry = useMemo(() => {
    if (!desiredPoints) return null
    return new THREE.TubeGeometry(desiredPoints, Math.max(desiredPath.length, 2), 0.015, 8, false)
  }, [desiredPoints, desiredPath.length])

  return (
    <group>
      {desiredGeometry && (
        <mesh geometry={desiredGeometry}>
          <meshStandardMaterial
            color="#4a6080"
            transparent
            opacity={0.4}
            roughness={0.8}
          />
        </mesh>
      )}
      {actualGeometry && (
        <mesh geometry={actualGeometry}>
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={0.3}
            transparent
            opacity={0.8}
          />
        </mesh>
      )}
      {/* Trail dots */}
      {pathHistory.slice(-20).map((p, i) => (
        <mesh key={i} position={[p.x, 0.06, p.y]}>
          <sphereGeometry args={[0.03, 8, 8]} />
          <meshStandardMaterial
            color={color}
            emissive={color}
            emissiveIntensity={0.5}
            transparent
            opacity={0.3 + (i / 20) * 0.5}
          />
        </mesh>
      ))}
    </group>
  )
}
