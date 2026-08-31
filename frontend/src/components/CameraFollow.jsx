import { useRef } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import * as THREE from 'three'

export function CameraFollow({ target, enabled, running }) {
  const { camera } = useThree()
  const targetPos = useRef(new THREE.Vector3(8, 10, 8))
  const lookAt = useRef(new THREE.Vector3(0, 0, 0))

  useFrame((_, delta) => {
    if (!enabled || !target) return

    const tx = target.x ?? 0
    const tz = target.y ?? 0
    const desired = new THREE.Vector3(tx + 5, 7, tz + 5)
    const lerpSpeed = running ? 3 : 1.5

    targetPos.current.lerp(desired, Math.min(delta * lerpSpeed, 1))
    lookAt.current.lerp(new THREE.Vector3(tx, 0.2, tz), Math.min(delta * lerpSpeed, 1))

    camera.position.copy(targetPos.current)
    camera.lookAt(lookAt.current)
  })

  return null
}
