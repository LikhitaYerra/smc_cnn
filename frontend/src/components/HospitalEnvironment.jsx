import { useMemo } from 'react'
import * as THREE from 'three'

export function HospitalEnvironment() {
  const floorTexture = useMemo(() => {
    const canvas = document.createElement('canvas')
    canvas.width = 512
    canvas.height = 512
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#1a2332'
    ctx.fillRect(0, 0, 512, 512)
    ctx.strokeStyle = '#2a3a4f'
    ctx.lineWidth = 1
    for (let i = 0; i < 512; i += 32) {
      ctx.beginPath()
      ctx.moveTo(i, 0)
      ctx.lineTo(i, 512)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(0, i)
      ctx.lineTo(512, i)
      ctx.stroke()
    }
    const tex = new THREE.CanvasTexture(canvas)
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping
    tex.repeat.set(20, 20)
    return tex
  }, [])

  return (
    <group>
      {/* Floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[3, -0.01, 0]} receiveShadow>
        <planeGeometry args={[30, 16]} />
        <meshStandardMaterial map={floorTexture} roughness={0.8} metalness={0.1} />
      </mesh>

      {/* Main corridor walls */}
      <mesh position={[3, 1.5, -4]} castShadow receiveShadow>
        <boxGeometry args={[30, 3, 0.15]} />
        <meshStandardMaterial color="#2d3f56" roughness={0.6} metalness={0.2} />
      </mesh>
      <mesh position={[3, 1.5, 4]} castShadow receiveShadow>
        <boxGeometry args={[30, 3, 0.15]} />
        <meshStandardMaterial color="#2d3f56" roughness={0.6} metalness={0.2} />
      </mesh>

      {/* Corridor center line */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[3, 0.005, 0]}>
        <planeGeometry args={[28, 0.08]} />
        <meshStandardMaterial color="#00d4aa" emissive="#00d4aa" emissiveIntensity={0.3} />
      </mesh>

      {/* Room dividers / door frames */}
      {[-2, 4, 10, 16].map((x) => (
        <group key={x} position={[x, 0, -4]}>
          <mesh position={[0, 1.2, 0]} castShadow>
            <boxGeometry args={[0.12, 2.4, 0.8]} />
            <meshStandardMaterial color="#3a5068" />
          </mesh>
          <mesh position={[0, 2.3, 0]}>
            <boxGeometry args={[0.8, 0.15, 0.8]} />
            <meshStandardMaterial color="#4a6080" />
          </mesh>
          {/* Room label plate */}
          <mesh position={[0, 1.8, 0.35]}>
            <boxGeometry args={[0.5, 0.2, 0.02]} />
            <meshStandardMaterial color="#00d4aa" emissive="#00d4aa" emissiveIntensity={0.2} />
          </mesh>
        </group>
      ))}

      {/* South side rooms */}
      {[-2, 4, 10, 16].map((x) => (
        <group key={`s-${x}`} position={[x, 0, 4]}>
          <mesh position={[0, 1.2, 0]} castShadow>
            <boxGeometry args={[0.12, 2.4, 0.8]} />
            <meshStandardMaterial color="#3a5068" />
          </mesh>
          <mesh position={[0, 2.3, 0]}>
            <boxGeometry args={[0.8, 0.15, 0.8]} />
            <meshStandardMaterial color="#4a6080" />
          </mesh>
        </group>
      ))}

      {/* Ceiling lights */}
      {Array.from({ length: 8 }, (_, i) => (
        <group key={`light-${i}`} position={[i * 3.5, 2.85, 0]}>
          <mesh>
            <boxGeometry args={[1.2, 0.05, 0.4]} />
            <meshStandardMaterial
              color="#e8f4ff"
              emissive="#a0d8ff"
              emissiveIntensity={0.8}
            />
          </mesh>
          <pointLight intensity={0.4} distance={6} color="#c0e8ff" />
        </group>
      ))}

      {/* Equipment carts */}
      <group position={[7, 0, -2.5]}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <boxGeometry args={[0.6, 1, 0.4]} />
          <meshStandardMaterial color="#4a5568" metalness={0.5} />
        </mesh>
        <mesh position={[0, 1.1, 0]}>
          <boxGeometry args={[0.5, 0.1, 0.35]} />
          <meshStandardMaterial color="#00d4aa" emissive="#00d4aa" emissiveIntensity={0.1} />
        </mesh>
      </group>

      <group position={[13, 0, 2.5]}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <boxGeometry args={[0.6, 1, 0.4]} />
          <meshStandardMaterial color="#4a5568" metalness={0.5} />
        </mesh>
      </group>

      {/* Hospital sign */}
      <mesh position={[3, 2.5, -3.7]}>
        <boxGeometry args={[4, 0.3, 0.05]} />
        <meshStandardMaterial color="#00d4aa" emissive="#00d4aa" emissiveIntensity={0.3} />
      </mesh>

      {/* Start / checkpoint markers */}
      {[
        { x: 0, z: 0, color: '#00ff88' },
        { x: 3, z: 0, color: '#00d4aa' },
        { x: 6, z: 0, color: '#00b8d4' },
      ].map((wp, i) => (
        <mesh key={i} position={[wp.x, 0.02, wp.z]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[0.15, 0.25, 32]} />
          <meshStandardMaterial
            color={wp.color}
            emissive={wp.color}
            emissiveIntensity={0.5}
            transparent
            opacity={0.7}
          />
        </mesh>
      ))}
    </group>
  )
}
