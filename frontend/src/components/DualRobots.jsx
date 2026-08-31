import { Robot } from './Robot'
import { TrajectoryPath } from './TrajectoryPath'

export function DualRobots({ dualCompare }) {
  if (!dualCompare) return null

  const a = dualCompare.mode_a
  const b = dualCompare.mode_b
  const lastA = a.path_history?.[a.path_history.length - 1] ?? { x: 0, y: 0.5 }
  const lastB = b.path_history?.[b.path_history.length - 1] ?? { x: 0, y: 0.5 }

  return (
    <group>
      <TrajectoryPath pathHistory={a.path_history ?? []} desiredPath={[]} controllerMode="classical" />
      <TrajectoryPath pathHistory={b.path_history ?? []} desiredPath={[]} controllerMode="cnn_adaptive" />
      <Robot position={[lastA.x, 0, lastA.y]} rotation={0} controllerMode="classical" running={false} />
      <Robot position={[lastB.x, 0, lastB.y + 0.3]} rotation={0} controllerMode="cnn_adaptive" running={false} />
    </group>
  )
}
