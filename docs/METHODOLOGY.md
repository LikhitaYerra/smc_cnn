# Methodology

Technical reference for the CNN-adaptive sliding mode control pipeline.

---

## Project Idea

Sliding Mode Control (SMC) is a robust nonlinear control technique suited to autonomous robots because it handles disturbances and model uncertainty.

Classical SMC uses **fixed control parameters** that may not be optimal under all conditions. Noisy sensors may require smoother control, while external disturbances may require stronger correction.

This project adds a **Convolutional Neural Network (CNN)** that classifies the operating scenario and adapts SMC parameters accordingly. A **PPO reinforcement learning agent** extends this with continuous, learned parameter adaptation.

```text
environment map → CNN / PPO prediction → scenario or gains → adaptive SMC → robot control
```

---

## Robot Model

The project uses a **differential-drive mobile robot**.

| Variable | Meaning |
|---|---|
| `x` | Position on the x-axis |
| `y` | Position on the y-axis |
| `theta` | Robot orientation |
| `v` | Linear velocity |
| `omega` | Angular velocity |

Kinematic model:

```text
ẋ = v cos(θ)
ẏ = v sin(θ)
θ̇ = ω
```

Discrete update (timestep Δt):

```text
x ← x + v cos(θ) Δt
y ← y + v sin(θ) Δt
θ ← θ + ω Δt
```

Implementation: `src/robot/differential_drive.py`, `src/robot/robot_state.py`

---

## Controllers

### Classical Sliding Mode Control

Uses fixed parameters for the entire simulation.

| Parameter | Meaning |
|---|---|
| `lambda_x`, `lambda_y`, `lambda_theta` | Sliding surface gains |
| `k_v`, `k_omega` | Velocity correction gains |
| `phi` | Boundary layer (chattering reduction) |
| `omega_smoothing` | Angular velocity smoothing |

Implementation: `src/controllers/smc_controller.py`

### CNN-Adaptive Sliding Mode Control

A CNN predicts one of five scenario classes and maps each to a distinct SMC parameter set.

| Label | Scenario |
|---:|---|
| 0 | Normal |
| 1 | Noise |
| 2 | Disturbance |
| 3 | Slip |
| 4 | Combined |

Behavior by scenario:

- **Noise** — smoother parameters to reduce chattering
- **Disturbance** — stronger correction gains
- **Slip** — adapted gains for reduced motion effectiveness
- **Combined** — balanced smoothing and correction

Implementation: `src/controllers/adaptive_smc_controller.py`, `src/controllers/adaptive_parameters.py`

### RL Agent (PPO)

Proximal Policy Optimization learns continuous SMC gain adaptation from a reward signal:

```text
Gymnasium Env → observation (state + error) → PPO policy → SMC parameters → reward
```

| Component | Location |
|---|---|
| Environment | `src/rl/env.py` |
| Reward | `−α·error² − β·effort − γ·chattering` |
| Policy | Actor-critic PPO with GAE |
| Runtime adapter | `src/rl/rl_adapter.py` |

---

## CNN Dataset

Synthetic dataset of 64×64 grayscale environment maps.

| Scenario | Label | Map representation |
|---|---:|---|
| Normal | 0 | Clean path line |
| Noise | 1 | Path with noisy pixels |
| Disturbance | 2 | Path with disturbance marker |
| Slip | 3 | Path with slippery zone band |
| Combined | 4 | Noise, disturbance, and slip combined |

Split: 1500 total samples (300 per class) → 1050 train / 225 val / 225 test.

Generation: `src/data_generation/generate_dataset.py`, `src/data_generation/split_dataset.py`

---

## CNN Architecture

| | |
|---|---|
| Input | 1 × 64 × 64 grayscale map |
| Output | 5-class softmax |
| Layers | 3 conv blocks (BatchNorm, ReLU, MaxPool) + FC classifier + Dropout |

Test accuracy on the synthetic test set: **100%** (1.0000).

Implementation: `src/cnn/cnn_model.py`, `src/cnn/train_cnn.py`

> The dataset is synthetic and visually simple. Real sensor maps should be used in future work.

---

## Simulation Scenarios

| Scenario | Description |
|---|---|
| Normal | No noise, disturbance, or slip |
| Noise | Sensor noise on position and orientation |
| Disturbance | Sudden external push |
| Slip | Wheel slip reduces effective velocity |
| Combined | All three applied together |

Implementation: `src/simulation/noise.py`, `disturbances.py`, `uncertainty.py`

---

## Evaluation Metrics

| Metric | Meaning |
|---|---|
| Mean tracking error | Average error over the simulation |
| RMSE tracking error | Root mean square error |
| Maximum tracking error | Peak error |
| Final tracking error | Error at simulation end |
| Control effort | Total control command intensity |
| Chattering index | Oscillation in angular velocity |
| Settling time | Time to stay below error threshold |

Implementation: `src/evaluation/metrics.py`

---

## Digital Twin Architecture

| Layer | Technology | Location |
|---|---|---|
| Backend API | FastAPI + WebSocket | `src/api/server.py` |
| Simulation engine | Python | `src/simulation/simulation_engine.py` |
| Frontend | React + Three.js | `frontend/` |
| Config | YAML | `config.yaml` |

The server on port 8000 serves both the built frontend and the API. WebSocket endpoint: `/ws/simulation`.
