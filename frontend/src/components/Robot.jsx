import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function Robot({ position = [0, 0, 0], rotation = 0, controllerMode = 'cnn_adaptive', running = false }) {
  const groupRef = useRef()
  const currentPos = useRef(new THREE.Vector3(position[0], 0.12, position[2]))
  const currentRot = useRef(-rotation)

  const colors = {
    classical: '#ff6b6b',
    cnn_adaptive: '#00d4aa',
    rl_agent: '#7c5cff',
  }
  const color = colors[controllerMode] || '#00d4aa'

  useFrame((_, delta) => {
    if (!groupRef.current) return
    const target = new THREE.Vector3(position[0], 0.12, position[2])
    currentPos.current.lerp(target, Math.min(delta * 12, 1))
    groupRef.current.position.copy(currentPos.current)

    const targetRot = -rotation
    currentRot.current += (targetRot - currentRot.current) * Math.min(delta * 10, 1)
    groupRef.current.rotation.y = currentRot.current
  })

  return (
    <group ref={groupRef}>
      <mesh castShadow position={[0, 0.04, 0]}>
        <cylinderGeometry args={[0.22, 0.22, 0.08, 32]} />
        <meshStandardMaterial color="#1a1a2e" metalness={0.6} roughness={0.3} />
      </mesh>

      <mesh castShadow position={[0, 0.18, 0]}>
        <boxGeometry args={[0.35, 0.16, 0.28]} />
        <meshStandardMaterial color={color} metalness={0.4} roughness={0.4} />
      </mesh>

      <mesh castShadow position={[0, 0.32, 0]}>
        <sphereGeometry args={[0.1, 16, 16]} />
        <meshStandardMaterial color="#e8f4ff" emissive={color} emissiveIntensity={0.4} metalness={0.8} />
      </mesh>

      <mesh position={[0.2, 0.18, 0]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.06, 0.12, 8]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} />
      </mesh>

      {[[-0.12, 0.06, 0.14], [0.12, 0.06, 0.14], [-0.12, 0.06, -0.14], [0.12, 0.06, -0.14]].map((pos, i) => (
        <mesh key={i} position={pos} rotation={[Math.PI / 2, 0, 0]} castShadow>
          <cylinderGeometry args={[0.05, 0.05, 0.04, 16]} />
          <meshStandardMaterial color="#333" metalness={0.7} />
        </mesh>
      ))}

      <mesh position={[0, 0.01, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.28, 0.32, 32]} />
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={running ? 1.0 : 0.6} transparent opacity={running ? 0.8 : 0.5} />
      </mesh>

      {running && (
        <pointLight position={[0, 0.4, 0]} intensity={0.5} color={color} distance={2} />
      )}
    </group>
  )
}
