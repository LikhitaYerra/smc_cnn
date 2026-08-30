import { useCallback, useEffect, useState } from 'react'
import { Scene3D } from './components/Scene3D'
import { SceneErrorBoundary } from './components/SceneErrorBoundary'
import { ControlPanel } from './components/ControlPanel'
import { MetricsDashboard } from './components/MetricsDashboard'
import { RLWorkflowPanel } from './components/RLWorkflowPanel'
import { ComparisonPanel } from './components/ComparisonPanel'
import { ReplayPanel } from './components/ReplayPanel'
import { CompletionSummary } from './components/CompletionSummary'
import { Toast } from './components/Toast'
import { useSimulation } from './hooks/useSimulation'

const DEMO_CONFIG = {
  controller_mode: 'cnn_adaptive',
  scenario_name: 'combined',
  trajectory_type: 'straight',
  enable_noise: true,
  enable_disturbance: true,
  enable_slip: true,
  total_time: 18.0,
  desired_speed: 0.3,
  simulation_speed: 3.0,
}

const DEFAULT_CONFIG = {
  controller_mode: 'cnn_adaptive',
  scenario_name: 'normal',
  trajectory_type: 'straight',
  enable_noise: false,
  enable_disturbance: false,
  enable_slip: false,
  total_time: 20.0,
  desired_speed: 0.3,
  simulation_speed: 2.0,
}

const TOUR_CONFIGS = [
  { ...DEMO_CONFIG, controller_mode: 'classical', total_time: 12.0, simulation_speed: 5.0 },
  { ...DEMO_CONFIG, controller_mode: 'cnn_adaptive', total_time: 12.0, simulation_speed: 5.0 },
  { ...DEMO_CONFIG, controller_mode: 'rl_agent', total_time: 12.0, simulation_speed: 5.0 },
]

export default function App() {
  const [config, setConfig] = useState(DEFAULT_CONFIG)
  const [activeTab, setActiveTab] = useState('metrics')
  const [showSummary, setShowSummary] = useState(false)
  const [tourIndex, setTourIndex] = useState(-1)

  const {
    connected,
    simState,
    running,
    rlStatus,
    comparisonStatus,
    dualCompare,
    recordings,
    presets,
    toast,
    reset,
    start,
    pause,
    replayRecording,
    runDualCompare,
    exportMetrics,
    exportComparison,
    bootstrapModels,
    trainRL,
    pollRLStatus,
    runComparison,
    pollComparison,
    showToast,
  } = useSimulation()

  useEffect(() => {
    if (connected && !simState) {
      reset(DEFAULT_CONFIG)
    }
  }, [connected])

  useEffect(() => {
    if (simState?.finished && !running) setShowSummary(true)
  }, [simState?.finished, running])

  useEffect(() => {
    if (tourIndex < 0 || running || !simState?.finished) return
    if (tourIndex >= TOUR_CONFIGS.length - 1) {
      setTourIndex(-1)
      showToast('Controller tour complete!', 'success')
      return
    }
    const next = tourIndex + 1
    const cfg = TOUR_CONFIGS[next]
    setConfig(cfg)
    setTourIndex(next)
    setShowSummary(false)
    setTimeout(() => start(cfg), 500)
  }, [simState?.finished, running, tourIndex, start, showToast])

  const handleStartTour = useCallback(() => {
    setShowSummary(false)
    setTourIndex(0)
    const cfg = TOUR_CONFIGS[0]
    setConfig(cfg)
    start(cfg)
    showToast('Controller tour: Classical → CNN → RL', 'info')
  }, [start, showToast])

  const handleReset = useCallback(() => {
    setShowSummary(false)
    reset(config)
    showToast('Simulation reset', 'info')
  }, [config, reset, showToast])

  const handleStart = useCallback(() => {
    setShowSummary(false)
    start(config)
  }, [config, start])

  const handleTrain = useCallback(async (quick) => {
    await trainRL(quick)
    const interval = setInterval(async () => {
      const status = await pollRLStatus()
      if (!status.running) clearInterval(interval)
    }, 1000)
  }, [trainRL, pollRLStatus])

  const handleBootstrap = useCallback(async () => {
    await bootstrapModels()
    const interval = setInterval(async () => {
      const status = await pollRLStatus()
      if (!status.running) {
        clearInterval(interval)
        showToast(status.message || 'Bootstrap complete', 'success')
      }
    }, 2000)
  }, [bootstrapModels, pollRLStatus, showToast])

  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return
      if (e.code === 'Space') {
        e.preventDefault()
        running ? pause() : handleStart()
      }
      if (e.code === 'KeyR') handleReset()
      if (e.code === 'Digit1') setConfig((c) => ({ ...c, controller_mode: 'classical' }))
      if (e.code === 'Digit2') setConfig((c) => ({ ...c, controller_mode: 'cnn_adaptive' }))
      if (e.code === 'Digit3') setConfig((c) => ({ ...c, controller_mode: 'rl_agent' }))
      if (e.code === 'KeyT') handleStartTour()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [running, pause, handleStart, handleReset, handleStartTour])

  return (
    <div className="app">
      <Toast toast={toast} />

      {showSummary && (
        <CompletionSummary
          simState={simState}
          controllerMode={config.controller_mode}
          onDismiss={() => setShowSummary(false)}
          onRunAgain={handleStart}
        />
      )}

      <header className="app-header">
        <div className="header-left">
          <div className="logo">
            <div className="logo-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="#00d4aa" strokeWidth="1.5" />
                <path d="M8 14l2-4 2 3 2-5" stroke="#00d4aa" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </div>
            <div>
              <h1>Robot Digital Twin</h1>
              <p>CNN-Adaptive SMC + Reinforcement Learning Agent</p>
            </div>
          </div>
        </div>
        <div className="header-center">
          <div className="pipeline-pill">
            <span>Environment</span>
            <span className="pill-arrow">→</span>
            <span>AI Agent</span>
            <span className="pill-arrow">→</span>
            <span>SMC Control</span>
            <span className="pill-arrow">→</span>
            <span>Robot</span>
          </div>
        </div>
        <div className="header-right">
          <div className={`connection-status ${connected ? 'connected' : ''}`}>
            <span className="status-dot" />
            {connected ? 'Live' : 'Connecting...'}
          </div>
        </div>
      </header>

      <main className="app-main">
        <aside className="sidebar left">
          <ControlPanel
            config={config}
            setConfig={setConfig}
            presets={presets}
            onReset={handleReset}
            onStart={handleStart}
            onPause={pause}
            onStartTour={handleStartTour}
            tourActive={tourIndex >= 0}
            running={running}
            connected={connected}
            rlModelLoaded={simState?.rl_model_loaded}
          />
        </aside>

        <section className="center-stage">
          <SceneErrorBoundary>
            <Scene3D
              simState={simState}
              controllerMode={config.controller_mode}
              running={running}
              config={config}
              dualCompare={dualCompare}
            />
          </SceneErrorBoundary>
          {!connected && (
            <div className="connection-overlay">
              <div className="loading-spinner" />
              <p>Connecting to simulation server...</p>
              <code>python run_digital_twin.py</code>
            </div>
          )}
        </section>

        <aside className="sidebar right">
          <div className="tab-bar">
            {[
              { id: 'metrics', label: 'Metrics' },
              { id: 'compare', label: 'Compare' },
              { id: 'replay', label: 'Replay' },
              { id: 'rl', label: 'RL Agent' },
            ].map((tab) => (
              <button
                key={tab.id}
                className={`tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>
          {activeTab === 'metrics' && (
            <MetricsDashboard
              simState={simState}
              controllerMode={config.controller_mode}
              onExport={exportMetrics}
            />
          )}
          {activeTab === 'compare' && (
            <ComparisonPanel
              comparisonStatus={comparisonStatus}
              dualCompare={dualCompare}
              onRunComparison={runComparison}
              onRunDualCompare={runDualCompare}
              onExportComparison={exportComparison}
              onPoll={pollComparison}
            />
          )}
          {activeTab === 'replay' && (
            <ReplayPanel
              recordings={recordings}
              onReplay={replayRecording}
              running={running}
            />
          )}
          {activeTab === 'rl' && (
            <RLWorkflowPanel
              rlStatus={rlStatus}
              onTrain={handleTrain}
              onBootstrap={handleBootstrap}
              onPollStatus={pollRLStatus}
              rlModelLoaded={simState?.rl_model_loaded}
            />
          )}
        </aside>
      </main>
    </div>
  )
}
