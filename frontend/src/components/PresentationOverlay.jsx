export function PresentationOverlay({ onDismiss, onStartDemo }) {
  const steps = [
    {
      num: '01',
      title: 'Pick a Controller',
      desc: 'Compare Classical SMC, CNN-Adaptive, and RL Agent modes.',
    },
    {
      num: '02',
      title: 'Set the Scenario',
      desc: 'Enable disturbances (noise, force, slip) for a realistic challenge.',
    },
    {
      num: '03',
      title: 'Run & Present',
      desc: 'Hit Run Simulation or use a one-click preset. Watch the 3D digital twin live.',
    },
  ]

  return (
    <div className="presentation-overlay">
      <div className="presentation-card">
        <div className="presentation-badge">Presentation Ready</div>
        <h2>Robot Digital Twin</h2>
        <p className="presentation-subtitle">
          CNN-Adaptive Sliding Mode Control with Reinforcement Learning
        </p>

        <div className="presentation-steps">
          {steps.map((s) => (
            <div key={s.num} className="presentation-step">
              <span className="step-num">{s.num}</span>
              <div>
                <div className="step-title">{s.title}</div>
                <div className="step-desc">{s.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="presentation-actions">
          <button className="btn btn-primary btn-lg" onClick={onStartDemo}>
            ▶ Start Live Demo
          </button>
          <button className="btn btn-secondary" onClick={onDismiss}>
            Explore Manually
          </button>
        </div>

        <div className="presentation-shortcuts">
          <kbd>Space</kbd> Run/Pause &nbsp;·&nbsp;
          <kbd>R</kbd> Reset &nbsp;·&nbsp;
          <kbd>1-3</kbd> Switch controller
        </div>
      </div>
    </div>
  )
}
