# Digital Twin Demo Guide

Step-by-step guide for demonstrating the **Robot Digital Twin** interface.

---

## Before the Demo (5–10 min setup)

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Bootstrap models if missing (~5–10 min)
python bootstrap_models.py

# 3. Build frontend and launch
cd frontend && npm run build && cd ..
python run_digital_twin.py
```

Open **http://localhost:8000** in Chrome (hard refresh: `Cmd+Shift+R`, fullscreen: `F11`).

> Use port **8000 only** — the server serves the built frontend and API together.

---

## Recommended Demo Flow (10–15 minutes)

### 1. Introduction (1 min)

- Point out the pipeline in the header: `Environment → AI Agent → SMC Control → Robot`
- Mention: differential-drive robot in a hospital corridor digital twin

### 2. Controller Tour (3 min) — best opener

- Click **"Controller Tour"** in the control panel (or press `T`)
- Auto-runs Classical → CNN → RL sequentially at 5× speed
- Completion popup shows grade after each run

### 3. Classical SMC Baseline (2 min)

- Press `1` or select **Classical SMC**
- Click preset **"Classical vs Issues"** or set scenario to **Combined**
- Press `Space` or **Run Simulation** (3× speed)
- **Talking point:** Fixed parameters struggle under combined uncertainty

### 4. CNN-Adaptive SMC (3 min)

- Press `2` or select **CNN-Adaptive**
- Click preset **"Full Showcase"**
- Run simulation
- **Talking point:** CNN classifies environment every second → adapts SMC gains
- Show CNN scenario prediction and confidence in the metrics panel

### 5. RL Agent (3 min)

- Press `3` or select **RL Agent**
- Switch to **RL Agent** tab → explain the 6-step PPO workflow
- Run simulation on S-curve trajectory
- **Talking point:** PPO learns continuous parameter adaptation from reward signal

### 6. Controller Comparison (2 min)

- Switch to **Compare** tab
- Click **"Run Comparison Benchmark"** (~30 s headless benchmark)
- Click **"Dual Compare: Classical vs CNN"** — overlays both paths in 3D
- Click **"Export Comparison CSV"** for quantitative results

### 7. Replay & Export (1 min)

- Switch to **Replay** tab — saved runs appear after each simulation
- Click a recording to replay in the 3D view
- In **Metrics** tab, click **CSV** to export live metrics

### 8. Architecture Wrap-up (1 min)

- Show the architecture diagram in the Compare tab
- Mention future work: real LiDAR maps, physical robot deployment

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Run / Pause simulation |
| `R` | Reset |
| `1` | Classical SMC |
| `2` | CNN-Adaptive |
| `3` | RL Agent |
| `T` | Controller Tour |

---

## Key Talking Points

1. **Problem:** Classical SMC uses fixed gains — suboptimal under noise, disturbances, and wheel slip
2. **CNN solution:** Supervised environment classification → discrete parameter lookup
3. **RL solution:** PPO agent learns continuous gain adaptation from tracking reward
4. **Digital twin:** Real-time 3D visualization of robot navigation in a hospital corridor
5. **Metrics:** RMSE tracking error, chattering index, control effort
6. **Replay:** Every run is auto-recorded for playback and comparison

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Connecting..." forever | Run `python run_digital_twin.py` |
| CNN model missing | Run `python bootstrap_models.py` |
| RL shows heuristic | RL Agent tab → Quick Train or Bootstrap |
| Slow simulation | Set speed to 3× or 5× in the control panel |
| Page blank / old UI | Hard refresh at `http://localhost:8000` |
| 3D view empty | Ensure browser window is wide enough; check console |

---

## Elevator Pitch

> We built a CNN-adaptive sliding mode controller for autonomous robots, extended it with a PPO reinforcement learning agent for continuous parameter tuning, and wrapped it in a real-time 3D hospital digital twin with replay, comparison, and export for live demonstration and benchmarking.
