import { useEffect, useRef } from 'react'

const SCENARIO_PATTERNS = {
  normal: { noise: 0.05, marker: 0, band: 0 },
  noise: { noise: 0.35, marker: 0, band: 0.15 },
  disturbance: { noise: 0.1, marker: 1, band: 0 },
  slip: { noise: 0.1, marker: 0, band: 0.4 },
  combined: { noise: 0.3, marker: 1, band: 0.35 },
}

export function EnvironmentMap({ scenario = 'normal', confidence = 0 }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const size = 64
    canvas.width = size
    canvas.height = size

    const pat = SCENARIO_PATTERNS[scenario] || SCENARIO_PATTERNS.normal

    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const base = 40 + Math.random() * pat.noise * 80
        let v = base
        if (pat.band > 0 && y > size * 0.55 && y < size * 0.75) v *= 1 - pat.band
        if (pat.marker > 0 && Math.hypot(x - size * 0.7, y - size * 0.3) < 6) v = 200
        ctx.fillStyle = `rgb(${v},${v},${v})`
        ctx.fillRect(x, y, 1, 1)
      }
    }

    // Path line
    ctx.strokeStyle = '#00d4aa'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(4, size / 2)
    ctx.lineTo(size - 4, size / 2)
    ctx.stroke()
  }, [scenario])

  return (
    <div className="env-map">
      <div className="env-map-header">
        <span>CNN Environment Map</span>
        {confidence > 0 && <span className="env-map-conf">{(confidence * 100).toFixed(0)}%</span>}
      </div>
      <canvas ref={canvasRef} className="env-map-canvas" width={64} height={64} />
      <div className="env-map-label">Scenario: {scenario}</div>
    </div>
  )
}
