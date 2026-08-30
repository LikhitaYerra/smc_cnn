const MODES = [
  { id: 'classical', label: 'Classical SMC', color: '#ff6b6b', desc: 'Fixed parameters', key: '1' },
  { id: 'cnn_adaptive', label: 'CNN-Adaptive', color: '#00d4aa', desc: 'CNN scenario classification', key: '2' },
  { id: 'rl_agent', label: 'RL Agent', color: '#7c5cff', desc: 'PPO-learned parameters', key: '3' },
]

const SCENARIOS = [
  { id: 'normal', label: 'Normal' },
  { id: 'noise', label: 'Sensor Noise' },
  { id: 'disturbance', label: 'Disturbance' },
  { id: 'slip', label: 'Wheel Slip' },
  { id: 'combined', label: 'Combined' },
]

const TRAJECTORIES = [
  { id: 'straight', label: 'Straight' },
  { id: 'circle', label: 'Circular' },
  { id: 's_curve', label: 'S-Curve' },
]

const SPEEDS = [
  { value: 1, label: '1×' },
  { value: 2, label: '2×' },
  { value: 3, label: '3×' },
  { value: 5, label: '5×' },
]

export function ControlPanel({
  config,
  setConfig,
  presets,
  onReset,
  onStart,
  onPause,
  onStartTour,
  tourActive,
  running,
  connected,
  rlModelLoaded,
}) {
  const applyPreset = (preset) => {
    setConfig({ ...config, ...preset.config })
  }

  const setScenarioFlags = (scenarioId) => {
    const flags = {
      normal: { enable_noise: false, enable_disturbance: false, enable_slip: false },
      noise: { enable_noise: true, enable_disturbance: false, enable_slip: false },
      disturbance: { enable_noise: false, enable_disturbance: true, enable_slip: false },
      slip: { enable_noise: false, enable_disturbance: false, enable_slip: true },
      combined: { enable_noise: true, enable_disturbance: true, enable_slip: true },
    }
    setConfig({ ...config, scenario_name: scenarioId, ...flags[scenarioId] })
  }

  return (
    <div className="panel control-panel">
      <div className="panel-header">
        <h2>Simulation Control</h2>
        <span className={`status-dot ${connected ? 'online' : 'offline'}`} />
      </div>

      {presets?.length > 0 && (
        <div className="section">
          <label className="section-label">Presentation Presets</label>
          <div className="preset-list">
            {presets.map((p) => (
              <button
                key={p.id}
                className="preset-btn"
                onClick={() => applyPreset(p)}
                disabled={running}
              >
                <span className="preset-name">{p.name}</span>
                <span className="preset-desc">{p.description}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="section">
        <label className="section-label">Controller Mode</label>
        <div className="mode-grid">
          {MODES.map((mode) => (
            <button
              key={mode.id}
              className={`mode-btn ${config.controller_mode === mode.id ? 'active' : ''}`}
              style={{ '--mode-color': mode.color }}
              onClick={() => setConfig({ ...config, controller_mode: mode.id })}
              disabled={running}
            >
              <span className="mode-dot" />
              <span className="mode-label">{mode.label}</span>
              <span className="mode-desc">{mode.desc}</span>
              <span className="mode-key">{mode.key}</span>
            </button>
          ))}
        </div>
        {config.controller_mode === 'rl_agent' && (
          <div className={`rl-model-status ${rlModelLoaded ? 'loaded' : 'heuristic'}`}>
            {rlModelLoaded ? '✓ Trained PPO model loaded' : '◎ Using heuristic policy (train for full RL)'}
          </div>
        )}
      </div>

      <div className="section">
        <label className="section-label">Environment Scenario</label>
        <div className="chip-group">
          {SCENARIOS.map((s) => (
            <button
              key={s.id}
              className={`chip ${config.scenario_name === s.id ? 'active' : ''}`}
              onClick={() => setScenarioFlags(s.id)}
              disabled={running}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <label className="section-label">Trajectory</label>
        <div className="chip-group">
          {TRAJECTORIES.map((t) => (
            <button
              key={t.id}
              className={`chip ${config.trajectory_type === t.id ? 'active' : ''}`}
              onClick={() => setConfig({ ...config, trajectory_type: t.id })}
              disabled={running}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <label className="section-label">Simulation Speed</label>
        <div className="chip-group">
          {SPEEDS.map((s) => (
            <button
              key={s.value}
              className={`chip ${config.simulation_speed === s.value ? 'active' : ''}`}
              onClick={() => setConfig({ ...config, simulation_speed: s.value })}
            >
              {s.label}
            </button>
          ))}
        </div>
      </div>

      <div className="section">
        <label className="section-label">Disturbances</label>
        <div className="toggle-group">
          {[
            { key: 'enable_noise', label: 'Sensor Noise' },
            { key: 'enable_disturbance', label: 'External Force' },
            { key: 'enable_slip', label: 'Wheel Slip' },
          ].map(({ key, label }) => (
            <label key={key} className="toggle">
              <input
                type="checkbox"
                checked={config[key]}
                onChange={(e) => setConfig({ ...config, [key]: e.target.checked })}
                disabled={running}
              />
              <span className="toggle-slider" />
              <span className="toggle-label">{label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="action-buttons">
        <button className="btn btn-tour" onClick={onStartTour} disabled={running || tourActive}>
          🎬 Controller Tour
        </button>
      </div>

      <div className="action-buttons">
        <button className="btn btn-secondary" onClick={onReset} disabled={running}>
          Reset
        </button>
        {running ? (
          <button className="btn btn-warning" onClick={onPause}>
            ⏸ Pause
          </button>
        ) : (
          <button className="btn btn-primary" onClick={onStart}>
            ▶ Run Simulation
          </button>
        )}
      </div>
    </div>
  )
}
