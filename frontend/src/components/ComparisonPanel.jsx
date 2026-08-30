const MODE_COLORS = {
  classical: '#ff6b6b',
  cnn_adaptive: '#00d4aa',
  rl_agent: '#7c5cff',
}

export function ComparisonPanel({
  comparisonStatus, dualCompare, onRunComparison, onRunDualCompare,
  onExportComparison, onPoll,
}) {
  const { running, progress, results, message } = comparisonStatus

  const handleRun = async () => {
    await onRunComparison()
    const interval = setInterval(async () => {
      const status = await onPoll()
      if (!status.running) clearInterval(interval)
    }, 800)
  }

  const data = results?.results || []

  return (
    <div className="panel comparison-panel">
      <div className="panel-header">
        <h2>Controller Comparison</h2>
      </div>

      <p className="comparison-desc">
        Headless benchmark of all three controllers under the <strong>combined</strong> scenario
        (noise + disturbance + slip). Lower RMSE wins.
      </p>

      <button className="btn btn-primary btn-full" onClick={handleRun} disabled={running}>
        {running ? `Benchmarking... ${progress}%` : '⚡ Run Comparison Benchmark'}
      </button>

      <button className="btn btn-secondary btn-full" onClick={onRunDualCompare} disabled={running} style={{ marginTop: 8 }}>
        🔀 Dual Compare: Classical vs CNN
      </button>

      {dualCompare && (
        <div className="dual-compare-summary">
          <div className="dual-row">
            <span style={{ color: '#ff6b6b' }}>Classical</span>
            <span>RMSE {dualCompare.mode_a?.metrics?.rmse_tracking_error?.toFixed(4)}</span>
          </div>
          <div className="dual-row">
            <span style={{ color: '#00d4aa' }}>CNN-Adaptive</span>
            <span>RMSE {dualCompare.mode_b?.metrics?.rmse_tracking_error?.toFixed(4)}</span>
          </div>
          <p className="dual-hint">Paths shown in 3D view</p>
        </div>
      )}

      {data.length > 0 && (
        <button className="btn btn-outline btn-full" onClick={onExportComparison} style={{ marginTop: 8 }}>
          📥 Export Comparison CSV
        </button>
      )}

      {running && (
        <div className="progress-bar" style={{ marginTop: 12 }}>
          <div className="progress-fill" style={{ width: `${progress}%` }} />
        </div>
      )}

      {message && !running && (
        <div className="comparison-message">{message}</div>
      )}

      {data.length > 0 && (
        <div className="comparison-results">
          {data
            .sort((a, b) => a.rank - b.rank)
            .map((r) => (
              <div key={r.controller_mode} className={`comparison-card rank-${r.rank}`}>
                <div className="comparison-card-header">
                  <span className="rank-badge">#{r.rank}</span>
                  <span className="comparison-label" style={{ color: r.color }}>
                    {r.label}
                  </span>
                  {r.rank === 1 && <span className="winner-tag">Winner</span>}
                </div>
                <div className="comparison-bars">
                  <BarMetric label="RMSE" value={r.metrics.rmse_tracking_error} max={0.5} color={r.color} />
                  <BarMetric label="Max Error" value={r.metrics.max_tracking_error} max={0.8} color={r.color} />
                  <BarMetric label="Chattering" value={r.metrics.chattering_index} max={50} color={r.color} invert />
                  <BarMetric label="Effort" value={r.metrics.control_effort} max={200} color={r.color} invert />
                </div>
              </div>
            ))}
        </div>
      )}

      <div className="architecture-section">
        <label className="section-label">System Architecture</label>
        <div className="arch-flow">
          <ArchNode label="Environment Map" sub="64×64 sensor grid" />
          <ArchArrow />
          <ArchNode label="CNN Classifier" sub="5 scenario classes" accent />
          <ArchArrow />
          <ArchNode label="SMC Controller" sub="Sliding mode control" />
          <ArchArrow />
          <ArchNode label="Robot" sub="Differential drive" />
        </div>
        <div className="arch-flow rl-flow">
          <ArchNode label="Robot State" sub="observation vector" />
          <ArchArrow />
          <ArchNode label="PPO Agent" sub="continuous policy" accent purple />
          <ArchArrow />
          <ArchNode label="SMC Gains" sub="λ, k, φ, smoothing" />
        </div>
      </div>
    </div>
  )
}

function BarMetric({ label, value, max, color, invert }) {
  const pct = Math.min((value / max) * 100, 100)
  const displayVal = typeof value === 'number' ? value.toFixed(4) : '—'
  return (
    <div className="bar-metric">
      <div className="bar-metric-label">
        <span>{label}</span>
        <span>{displayVal}</span>
      </div>
      <div className="bar-track">
        <div
          className="bar-fill"
          style={{
            width: `${pct}%`,
            background: invert ? `linear-gradient(90deg, ${color}40, ${color})` : color,
          }}
        />
      </div>
    </div>
  )
}

function ArchNode({ label, sub, accent, purple }) {
  return (
    <div className={`arch-node ${accent ? 'accent' : ''} ${purple ? 'purple' : ''}`}>
      <div className="arch-node-label">{label}</div>
      <div className="arch-node-sub">{sub}</div>
    </div>
  )
}

function ArchArrow() {
  return <div className="arch-arrow">→</div>
}
