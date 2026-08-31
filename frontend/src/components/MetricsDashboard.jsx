import { ErrorChart } from './ErrorChart'
import { EnvironmentMap } from './EnvironmentMap'

const MODE_COLORS = {
  classical: '#ff6b6b',
  cnn_adaptive: '#00d4aa',
  rl_agent: '#7c5cff',
}

export function MetricsDashboard({ simState, controllerMode, onExport }) {
  const error = simState?.tracking_error ?? 0
  const metrics = simState?.metrics || {}
  const params = simState?.active_params || {}
  const control = simState?.control || {}
  const surface = simState?.sliding_surface || {}
  const errorHistory = simState?.error_history || []
  const progress = simState?.total_steps
    ? ((simState.step / simState.total_steps) * 100).toFixed(0)
    : 0

  const modeLabels = {
    classical: 'Classical SMC',
    cnn_adaptive: 'CNN-Adaptive',
    rl_agent: 'RL Agent (PPO)',
  }

  const color = MODE_COLORS[controllerMode] || '#00d4aa'
  const errorColor = error < 0.05 ? '#00d4aa' : error < 0.15 ? '#ffd93d' : '#ff6b6b'

  return (
    <div className="panel metrics-panel">
      <div className="panel-header">
        <h2>Live Metrics</h2>
        <div className="panel-header-actions">
          {onExport && (
            <button className="btn btn-outline btn-sm" onClick={onExport} title="Export metrics CSV">
              📥 CSV
            </button>
          )}
          <span className="mode-tag" data-mode={controllerMode}>
            {modeLabels[controllerMode]}
          </span>
        </div>
      </div>

      <div className="metric-hero">
        <div className="metric-hero-value" style={{ color: errorColor }}>
          {simState ? error.toFixed(4) : '—'}
        </div>
        <div className="metric-hero-label">Tracking Error (m)</div>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${progress}%`, background: color }} />
        </div>
        <div className="progress-label">
          {progress}% complete · t = {(simState?.time ?? 0).toFixed(1)}s
          {simState?.finished && ' · ✓ Done'}
        </div>
      </div>

      <ErrorChart errorHistory={errorHistory} color={color} />

      {controllerMode === 'cnn_adaptive' && (
        <EnvironmentMap
          scenario={simState?.predicted_scenario ?? 'normal'}
          confidence={simState?.cnn_confidence ?? 0}
        />
      )}

      <div className="metric-grid">
        <MetricCard label="Linear Vel (v)" value={control.v?.toFixed(3) ?? '—'} unit="m/s" />
        <MetricCard label="Angular Vel (ω)" value={control.omega?.toFixed(3) ?? '—'} unit="rad/s" />
        <MetricCard label="Sliding Sx" value={surface.sx?.toFixed(4) ?? '—'} />
        <MetricCard label="Sliding Sy" value={surface.sy?.toFixed(4) ?? '—'} />
        <MetricCard
          label="RL Reward"
          value={simState?.rl_reward?.toFixed(3) ?? '—'}
          highlight={controllerMode === 'rl_agent'}
        />
        <MetricCard
          label="CNN Scenario"
          value={
            controllerMode === 'cnn_adaptive'
              ? `${simState?.predicted_scenario ?? '—'} (${((simState?.cnn_confidence ?? 0) * 100).toFixed(0)}%)`
              : '—'
          }
          highlight={controllerMode === 'cnn_adaptive'}
        />
      </div>

      {Object.keys(metrics).length > 0 && (
        <div className="section">
          <label className="section-label">Episode Summary</label>
          <div className="summary-grid">
            <SummaryItem label="RMSE" value={metrics.rmse_tracking_error?.toFixed(4)} good={metrics.rmse_tracking_error < 0.1} />
            <SummaryItem label="Max Error" value={metrics.max_tracking_error?.toFixed(4)} />
            <SummaryItem label="Chattering" value={metrics.chattering_index?.toFixed(2)} />
            <SummaryItem label="Effort" value={metrics.control_effort?.toFixed(1)} />
          </div>
        </div>
      )}

      {Object.keys(params).length > 0 && (
        <div className="section">
          <label className="section-label">Active SMC Parameters</label>
          <div className="params-list">
            {Object.entries(params).map(([key, val]) => (
              <div key={key} className="param-row">
                <span className="param-key">{key}</span>
                <span className="param-val">{typeof val === 'number' ? val.toFixed(3) : val}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function MetricCard({ label, value, unit, highlight }) {
  return (
    <div className={`metric-card ${highlight ? 'highlight' : ''}`}>
      <div className="metric-value">{value}{unit && <span className="metric-unit">{unit}</span>}</div>
      <div className="metric-label">{label}</div>
    </div>
  )
}

function SummaryItem({ label, value, good }) {
  return (
    <div className={`summary-item ${good ? 'good' : ''}`}>
      <span className="summary-label">{label}</span>
      <span className="summary-value">{value ?? '—'}</span>
    </div>
  )
}
