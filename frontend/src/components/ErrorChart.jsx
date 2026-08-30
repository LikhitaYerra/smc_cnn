import { useEffect, useRef } from 'react'

export function ErrorChart({ errorHistory = [], color = '#00d4aa', height = 80 }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const dpr = window.devicePixelRatio || 1
    const w = canvas.clientWidth
    const h = height
    canvas.width = w * dpr
    canvas.height = h * dpr
    ctx.scale(dpr, dpr)

    ctx.clearRect(0, 0, w, h)

    // Background grid
    ctx.strokeStyle = 'rgba(255,255,255,0.05)'
    ctx.lineWidth = 1
    for (let i = 0; i < 4; i++) {
      const y = (h / 4) * i
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(w, y)
      ctx.stroke()
    }

    if (!errorHistory.length) {
      ctx.fillStyle = 'rgba(136,153,170,0.5)'
      ctx.font = '11px Inter, sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('Run simulation to see live error chart', w / 2, h / 2)
      return
    }

    const errors = errorHistory.map((p) => p.error)
    const maxErr = Math.max(...errors, 0.05)
    const minErr = 0
    const pad = 4

    // Fill area
    ctx.beginPath()
    errors.forEach((err, i) => {
      const x = pad + (i / Math.max(errors.length - 1, 1)) * (w - pad * 2)
      const y = h - pad - ((err - minErr) / (maxErr - minErr)) * (h - pad * 2)
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    })
    ctx.lineTo(pad + (w - pad * 2), h - pad)
    ctx.lineTo(pad, h - pad)
    ctx.closePath()
    const grad = ctx.createLinearGradient(0, 0, 0, h)
    grad.addColorStop(0, color + '40')
    grad.addColorStop(1, color + '05')
    ctx.fillStyle = grad
    ctx.fill()

    // Line
    ctx.beginPath()
    errors.forEach((err, i) => {
      const x = pad + (i / Math.max(errors.length - 1, 1)) * (w - pad * 2)
      const y = h - pad - ((err - minErr) / (maxErr - minErr)) * (h - pad * 2)
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    })
    ctx.strokeStyle = color
    ctx.lineWidth = 2
    ctx.stroke()

    // Threshold line at 0.05m
    const threshY = h - pad - ((0.05 - minErr) / (maxErr - minErr)) * (h - pad * 2)
    ctx.setLineDash([4, 4])
    ctx.strokeStyle = 'rgba(255,217,61,0.5)'
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(0, threshY)
    ctx.lineTo(w, threshY)
    ctx.stroke()
    ctx.setLineDash([])
  }, [errorHistory, color, height])

  return (
    <div className="error-chart">
      <div className="error-chart-header">
        <span>Tracking Error Over Time</span>
        <span className="error-chart-max">
          max: {errorHistory.length ? Math.max(...errorHistory.map((p) => p.error)).toFixed(3) : '—'} m
        </span>
      </div>
      <canvas ref={canvasRef} style={{ width: '100%', height }} />
    </div>
  )
}
