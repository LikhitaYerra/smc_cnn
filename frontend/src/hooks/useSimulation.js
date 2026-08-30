import { useCallback, useEffect, useRef, useState } from 'react'

function getWsUrl() {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return `${protocol}://${window.location.host}/ws/simulation`
}

const API_URL = '/api'

export function useSimulation() {
  const wsRef = useRef(null)
  const reconnectRef = useRef(null)
  const mountedRef = useRef(true)
  const [connected, setConnected] = useState(false)
  const [simState, setSimState] = useState(null)
  const [running, setRunning] = useState(false)
  const [rlStatus, setRlStatus] = useState({ running: false, progress: 0, message: 'Idle' })
  const [comparisonStatus, setComparisonStatus] = useState({ running: false, progress: 0, results: null })
  const [dualCompare, setDualCompare] = useState(null)
  const [recordings, setRecordings] = useState([])
  const [presets, setPresets] = useState([])
  const [toast, setToast] = useState(null)

  const showToast = useCallback((message, type = 'info') => {
    if (!mountedRef.current) return
    setToast({ message, type, id: Date.now() })
    setTimeout(() => { if (mountedRef.current) setToast(null) }, 3500)
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN ||
        wsRef.current?.readyState === WebSocket.CONNECTING) return

    const ws = new WebSocket(getWsUrl())
    wsRef.current = ws

    ws.onopen = () => { if (mountedRef.current) setConnected(true) }
    ws.onclose = () => {
      if (!mountedRef.current) return
      setConnected(false)
      setRunning(false)
      reconnectRef.current = setTimeout(connect, 2000)
    }
    ws.onerror = () => { if (mountedRef.current) setConnected(false) }
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'error') {
          showToast(data.message || 'Simulation error', 'error')
          setRunning(false)
          return
        }
        if (data.type === 'state' || data.type === 'finished') {
          setSimState(data)
          if (data.type === 'finished') {
            setRunning(false)
            fetchRecordings()
          }
        }
      } catch {
        showToast('Bad message from server', 'error')
      }
    }
  }, [showToast])

  const fetchRecordings = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/recordings`)
      const data = await res.json()
      if (mountedRef.current) setRecordings(data)
    } catch { /* ignore */ }
  }, [])

  useEffect(() => {
    mountedRef.current = true
    connect()
    fetch(`${API_URL}/presets`).then((r) => r.json()).then((d) => { if (mountedRef.current) setPresets(d) }).catch(() => {})
    fetchRecordings()
    pollRLStatus()
    return () => {
      mountedRef.current = false
      clearTimeout(reconnectRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  const send = useCallback((msg) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg))
      return true
    }
    showToast('Not connected — run: python run_digital_twin.py', 'error')
    return false
  }, [showToast])

  const reset = useCallback((config) => {
    setRunning(false)
    setDualCompare(null)
    send({ type: 'reset', ...config })
  }, [send])

  const start = useCallback((config) => {
    setRunning(true)
    setDualCompare(null)
    send({ type: 'start', ...config })
  }, [send])

  const pause = useCallback(() => {
    setRunning(false)
    send({ type: 'pause' })
  }, [send])

  const replayRecording = useCallback((recordingId, speed = 3) => {
    setRunning(true)
    setDualCompare(null)
    send({ type: 'replay', recording_id: recordingId, simulation_speed: speed })
  }, [send])

  const runDualCompare = useCallback(async () => {
    showToast('Running dual comparison...', 'info')
    try {
      const res = await fetch(`${API_URL}/dual-compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_name: 'combined',
          trajectory_type: 'straight',
          enable_noise: true,
          enable_disturbance: true,
          enable_slip: true,
          total_time: 12.0,
        }),
      })
      const data = await res.json()
      setDualCompare(data)
      showToast('Dual comparison ready — Classical vs CNN', 'success')
      return data
    } catch {
      showToast('Dual comparison failed', 'error')
    }
  }, [showToast])

  const exportMetrics = useCallback(() => {
    window.open(`${API_URL}/export/metrics`, '_blank')
  }, [])

  const exportComparison = useCallback(() => {
    window.open(`${API_URL}/export/comparison`, '_blank')
  }, [])

  const bootstrapModels = useCallback(async () => {
    await fetch(`${API_URL}/bootstrap`, { method: 'POST' })
    showToast('Training CNN + RL models... (~5-10 min)', 'info')
  }, [showToast])

  const trainRL = useCallback(async (quick = true) => {
    await fetch(`${API_URL}/rl/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ iterations: 20, quick }),
    })
    showToast('RL training started', 'info')
  }, [showToast])

  const pollRLStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/rl/status`)
      const data = await res.json()
      if (mountedRef.current) setRlStatus(data)
      return data
    } catch {
      return rlStatus
    }
  }, [rlStatus])

  const runComparison = useCallback(async (opts = {}) => {
    await fetch(`${API_URL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_name: 'combined', trajectory_type: 'straight',
        enable_noise: true, enable_disturbance: true, enable_slip: true,
        total_time: 8.0, ...opts,
      }),
    })
    showToast('Running controller comparison...', 'info')
  }, [showToast])

  const pollComparison = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/compare/status`)
      const data = await res.json()
      if (mountedRef.current) setComparisonStatus(data)
      if (!data.running && data.results) {
        const winner = data.results.results?.find((r) => r.rank === 1)?.label
        if (winner) showToast(`Winner: ${winner}`, 'success')
      }
      return data
    } catch {
      return comparisonStatus
    }
  }, [comparisonStatus, showToast])

  return {
    connected, simState, running, rlStatus, comparisonStatus, dualCompare,
    recordings, presets, toast, reset, start, pause, replayRecording,
    runDualCompare, exportMetrics, exportComparison, bootstrapModels,
    trainRL, pollRLStatus, runComparison, pollComparison, showToast, fetchRecordings,
  }
}
