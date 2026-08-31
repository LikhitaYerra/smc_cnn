const MODE_LABELS = {
  classical: 'Classical SMC',
  cnn_adaptive: 'CNN-Adaptive SMC',
  rl_agent: 'RL Agent (PPO)',
}

export function CompletionSummary({ simState, controllerMode, onDismiss, onRunAgain }) {
  if (!simState?.finished) return null

  const metrics = simState.metrics || {}
  const error = simState.tracking_error ?? 0
  const grade = error < 0.08 ? 'Excellent' : error < 0.2 ? 'Good' : error < 0.35 ? 'Fair' : 'Poor'
  const gradeColor = error < 0.08 ? '#00d4aa' : error < 0.2 ? '#ffd93d' : error < 0.35 ? '#ffaa44' : '#ff6b6b'

  return (
    <div className="completion-overlay" onClick={onDismiss}>
      <div className="completion-card" onClick={(e) => e.stopPropagation()}>
        <div className="completion-badge" style={{ color: gradeColor, borderColor: gradeColor }}>
          {grade}
        </div>
        <h3>Simulation Complete</h3>
        <p className="completion-mode">{MODE_LABELS[controllerMode]}</p>

        <div className="completion-stats">
          <div className="completion-stat">
            <span className="stat-val" style={{ color: gradeColor }}>{error.toFixed(4)}</span>
            <span className="stat-label">Final Error (m)</span>
          </div>
          <div className="completion-stat">
            <span className="stat-val">{metrics.rmse_tracking_error?.toFixed(4) ?? '—'}</span>
            <span className="stat-label">RMSE</span>
          </div>
          <div className="completion-stat">
            <span className="stat-val">{metrics.chattering_index?.toFixed(1) ?? '—'}</span>
            <span className="stat-label">Chattering</span>
          </div>
          <div className="completion-stat">
            <span className="stat-val">{simState.time?.toFixed(1) ?? '—'}s</span>
            <span className="stat-label">Duration</span>
          </div>
        </div>

        <div className="completion-actions">
          <button className="btn btn-primary" onClick={onRunAgain}>Run Again</button>
          <button className="btn btn-secondary" onClick={onDismiss}>Close</button>
        </div>
      </div>
    </div>
  )
}
