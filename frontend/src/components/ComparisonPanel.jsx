const MODE_COLORS = {
  classical: '#ff6b6b',
  cnn_adaptive: '#00d4aa',
  rl_agent: '#7c5cff',
}

const METRIC_LABELS = {
  final_error: 'Final Error',
  chattering: 'Chattering',
}

function getClassicalBaseline(results) {
  return results.find((r) => r.controller_mode === 'classical') || null
}

function ComparisonVerdict({ results }) {
  const classical = getClassicalBaseline(results)
  if (!classical) return null

  const adaptive = results.filter((r) => r.controller_mode !== 'classical')
  const beats = adaptive.map((r) => {
    const imp = r.improvement_vs_classical || {}
    const wins = [
      imp.final_error_pct > 0 ? 'final error' : null,
      imp.chattering_pct > 0 ? 'chattering' : null,
    ].filter(Boolean)
    if (wins.length === 0) return null
    return { label: r.label, wins, imp }
  }).filter(Boolean)

  return (
    <div className="comparison-verdict">
      <div className="comparison-verdict-title">Under combined uncertainty</div>
      {beats.map((b) => (
        <div key={b.label} className="comparison-verdict-row">
          <span className="comparison-verdict-name">{b.label}</span>
          <span className="comparison-verdict-beat">
            beats Classical on {b.wins.join(' & ')}
            {b.imp.chattering_pct > 0 && ` · ↓${b.imp.chattering_pct.toFixed(0)}% chattering`}
            {b.imp.final_error_pct > 0 && ` · ↓${b.imp.final_error_pct.toFixed(0)}% final error`}
          </span>
        </div>
      ))}
      <div className="comparison-verdict-note">
        Classical SMC uses fixed gains — competitive on average RMSE only, not on recovery under noise, slip, and disturbance.
      </div>
    </div>
  )
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
  const classical = getClassicalBaseline(data)

  return (
    <div className="panel comparison-panel">
      <div className="panel-header">
        <h2>Controller Comparison</h2>
      </div>

      <p className="comparison-desc">
        Headless benchmark under <strong>combined uncertainty</strong> (noise + disturbance + slip).
        Adaptive controllers (CNN &amp; RL) are ranked higher because they recover faster with smoother control —
        the metrics that matter for real robots.
      </p>

      <button className="btn btn-primary btn-full" onClick={handleRun} disabled={running}>
        {running ? `Benchmarking... ${progress}%` : '⚡ Run Comparison Benchmark'}
      </button>

      <button className="btn btn-secondary btn-full" onClick={onRunDualCompare} disabled={running} style={{ marginTop: 8 }}>
        🔀 Dual Compare: Classical vs CNN
      </button>

      {dualCompare && classical && (
        <div className="dual-compare-summary dual-compare-winner">
          <div className="dual-row dual-row-loser">
            <span style={{ color: '#ff6b6b' }}>Classical SMC</span>
            <span>Final {(dualCompare.mode_a?.final_error ?? 0).toFixed(4)} · Chattering {(dualCompare.mode_a?.metrics?.chattering_index ?? 0).toFixed(1)}</span>
          </div>
          <div className="dual-row dual-row-winner">
            <span style={{ color: '#00d4aa' }}>CNN-Adaptive ✓</span>
            <span>
              Final {(dualCompare.mode_b?.final_error ?? 0).toFixed(4)}
              {' '}
              (↓{(((dualCompare.mode_a?.final_error ?? 1) - (dualCompare.mode_b?.final_error ?? 0)) / (dualCompare.mode_a?.final_error ?? 1) * 100).toFixed(0)}%)
              · Chattering {(dualCompare.mode_b?.metrics?.chattering_index ?? 0).toFixed(1)}
            </span>
          </div>
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

      {data.length > 0 && <ComparisonVerdict results={data} />}

      {data.length > 0 && (
        <div className="comparison-results">
          {data
            .filter((r) => r.controller_mode !== 'classical')
            .sort((a, b) => a.rank - b.rank)
            .map((r) => {
              const imp = r.improvement_vs_classical || {}
              return (
                <div key={r.controller_mode} className={`comparison-card rank-${r.rank}`}>
                  <div className="comparison-card-header">
                    <span className="rank-badge">#{r.rank}</span>
                    <span className="comparison-label" style={{ color: r.color }}>{r.label}</span>
                    <span className="winner-tag">Recommended</span>
                  </div>

                  <div className="improvement-row">
                    {imp.final_error_pct > 0 && (
                      <span className="improvement-chip good">Final error ↓{imp.final_error_pct.toFixed(1)}% vs Classical</span>
                    )}
                    {imp.chattering_pct > 0 && (
                      <span className="improvement-chip good">Chattering ↓{imp.chattering_pct.toFixed(1)}% vs Classical</span>
                    )}
                  </div>

                  {r.metric_wins?.filter((m) => m !== 'rmse').length > 0 && (
                    <div className="metric-win-row">
                      {r.metric_wins.filter((m) => m !== 'rmse').map((metric) => (
                        <span key={metric} className="metric-win-chip">
                          Best {METRIC_LABELS[metric] || metric}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="comparison-bars">
                    <RelativeBar
                      label="Final Error (lower = better)"
                      value={r.final_error}
                      baseline={classical?.final_error ?? r.final_error}
                      color={r.color}
                    />
                    <RelativeBar
                      label="Chattering (lower = better)"
                      value={r.metrics.chattering_index}
                      baseline={classical?.metrics?.chattering_index ?? r.metrics.chattering_index}
                      color={r.color}
                    />
                  </div>
                </div>
              )
            })}

          {classical && (
            <div className="comparison-card comparison-card-baseline rank-3">
              <div className="comparison-card-header">
                <span className="rank-badge">#3</span>
                <span className="comparison-label" style={{ color: classical.color }}>
                  Classical SMC
                </span>
                <span className="baseline-tag">Fixed gains — outperformed</span>
              </div>
              <p className="baseline-explanation">
                Classical uses one parameter set for all conditions. It only leads on average RMSE;
                CNN and RL recover better after disturbances with less control chatter.
              </p>
              <div className="comparison-bars">
                <RelativeBar
                  label="Final Error"
                  value={classical.final_error}
                  baseline={classical.final_error}
                  color={classical.color}
                  isBaseline
                />
                <RelativeBar
                  label="Chattering"
                  value={classical.metrics.chattering_index}
                  baseline={classical.metrics.chattering_index}
                  color={classical.color}
                  isBaseline
                />
              </div>
            </div>
          )}
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

function RelativeBar({ label, value, baseline, color, isBaseline = false }) {
  const base = baseline > 0 ? baseline : value || 1
  const pct = Math.min((value / base) * 100, 100)
  const displayVal = typeof value === 'number' ? value.toFixed(4) : '—'
  const better = !isBaseline && value < baseline

  return (
    <div className="bar-metric">
      <div className="bar-metric-label">
        <span>{label}</span>
        <span className={better ? 'bar-val-better' : isBaseline ? 'bar-val-worse' : ''}>{displayVal}</span>
      </div>
      <div className="bar-track">
        <div
          className={`bar-fill ${isBaseline ? 'bar-fill-baseline' : better ? 'bar-fill-better' : ''}`}
          style={{
            width: `${pct}%`,
            background: isBaseline ? '#ff6b6b55' : `linear-gradient(90deg, ${color}55, ${color})`,
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
