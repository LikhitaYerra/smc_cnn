export function ReplayPanel({ recordings, onReplay, running }) {
  if (!recordings?.length) {
    return (
      <div className="panel replay-panel">
        <div className="panel-header"><h2>Recordings</h2></div>
        <p className="replay-empty">Run a simulation to auto-save a recording for replay.</p>
      </div>
    )
  }

  return (
    <div className="panel replay-panel">
      <div className="panel-header"><h2>Recordings</h2></div>
      <p className="replay-desc">Saved runs — click to replay in the 3D view.</p>
      <div className="recording-list">
        {recordings.map((rec) => (
          <button
            key={rec.id}
            className="recording-item"
            onClick={() => onReplay(rec.id)}
            disabled={running}
          >
            <div className="recording-header">
              <span className="recording-mode">{rec.controller_mode}</span>
              <span className="recording-frames">{rec.frames} frames</span>
            </div>
            <div className="recording-meta">
              {rec.scenario_name} · RMSE {rec.metrics?.rmse_tracking_error?.toFixed(4) ?? '—'}
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
