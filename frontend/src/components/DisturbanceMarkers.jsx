import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

export function DisturbanceMarkers({ simState, config }) {
  const pulseRef = useRef(0)
  const time = simState?.time ?? 0
  const robot = simState?.robot ?? { x: 0, y: 0.5 }

  const noise = config?.enable_noise
  const force = config?.enable_disturbance && time >= 8.0 && time <= 8.6
  const slip = config?.enable_slip && time >= 10.0 && time <= 14.0

  useFrame((_, delta) => {
    pulseRef.current += delta * 4
  })

  const pulse = 0.5 + Math.sin(pulseRef.current) * 0.3

  return (
    <group>
      {noise && (
        <mesh position={[robot.x, 1.2, robot.y]}>
          <sphereGeometry args={[0.15 + pulse * 0.05, 12, 12]} />
          <meshStandardMaterial color="#ffd93d" emissive="#ffd93d" emissiveIntensity={0.6} transparent opacity={0.35} />
        </mesh>
      )}
      {force && (
        <group position={[robot.x, 0.5, robot.y]}>
          <mesh rotation={[0, 0, Math.PI / 2]}>
            <coneGeometry args={[0.2, 0.6, 8]} />
            <meshStandardMaterial color="#ff6b6b" emissive="#ff6b6b" emissiveIntensity={1.2} />
          </mesh>
        </group>
      )}
      {slip && (
        <mesh position={[robot.x, 0.05, robot.y]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.35, 0.55, 32]} />
          <meshStandardMaterial color="#7c5cff" emissive="#7c5cff" emissiveIntensity={0.8} transparent opacity={0.5 + pulse * 0.2} />
        </mesh>
      )}
    </group>
  )
}
