export function RLWorkflowPanel({ rlStatus, onTrain, onBootstrap, onPollStatus, rlModelLoaded }) {
  const steps = [
    { id: 1, title: 'Environment', desc: 'Gymnasium SMC parameter env with domain randomization' },
    { id: 2, title: 'Observation', desc: 'Robot state, desired pose, tracking error, scenario' },
    { id: 3, title: 'Action', desc: 'Continuous SMC gains (λ, k, φ, smoothing)' },
    { id: 4, title: 'Reward', desc: '−α·error² − β·effort − γ·chattering' },
    { id: 5, title: 'Policy', desc: 'PPO actor-critic with GAE advantage estimation' },
    { id: 6, title: 'Deploy', desc: 'Trained policy replaces CNN lookup at runtime' },
  ]

  return (
    <div className="panel rl-panel">
      <div className="panel-header">
        <h2>RL Agent Workflow</h2>
        <span className="rl-badge">PPO</span>
      </div>

      <div className={`rl-model-banner ${rlModelLoaded ? 'loaded' : 'pending'}`}>
        {rlModelLoaded
          ? '✓ PPO model ready — RL Agent uses trained policy'
          : '◎ No trained model — heuristic policy active (run Quick Train)'}
      </div>

      <div className="workflow-pipeline">
        {steps.map((step, i) => (
          <div key={step.id} className="workflow-step">
            <div className="workflow-node">
              <span className="workflow-num">{step.id}</span>
            </div>
            {i < steps.length - 1 && <div className="workflow-connector" />}
            <div className="workflow-content">
              <div className="workflow-title">{step.title}</div>
              <div className="workflow-desc">{step.desc}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="rl-training-section">
        <div className="training-header">
          <span>Model Training</span>
          {rlStatus.running && <span className="training-pulse">Training...</span>}
        </div>

        {rlStatus.running && (
          <div className="training-progress">
            <div className="progress-bar">
              <div
                className="progress-fill rl-fill"
                style={{ width: `${rlStatus.progress}%` }}
              />
            </div>
            <span className="progress-label">{rlStatus.message}</span>
          </div>
        )}

        <div className="rl-actions">
          <button
            className="btn btn-rl"
            onClick={() => onTrain(true)}
            disabled={rlStatus.running}
          >
            Quick Train (20 iter)
          </button>
          <button
            className="btn btn-rl-outline"
            onClick={onBootstrap}
            disabled={rlStatus.running}
          >
            Bootstrap CNN + RL
          </button>
          <button
            className="btn btn-rl-outline"
            onClick={onPollStatus}
          >
            Refresh Status
          </button>
        </div>

        <div className="rl-info">
          <code>python -m src.rl.train_rl --quick</code>
        </div>
      </div>
    </div>
  )
}
