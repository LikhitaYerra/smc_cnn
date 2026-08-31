# CNN-Adaptive Sliding Mode Control for Autonomous Robots

**Author:** Likhita Yerra  
**Institution:** aivancity (Paris, France) · Indrashil University (Kadi, India)  
**Repository:** [github.com/LikhitaYerra/smc_cnn](https://github.com/LikhitaYerra/smc_cnn)

---

## Overview

This project implements and evaluates adaptive sliding mode control (SMC) for a differential-drive autonomous mobile robot. Three controllers are compared under five operating conditions:

| Controller | Approach |
|---|---|
| **Classical SMC** | Fixed control gains throughout the simulation |
| **CNN-Adaptive SMC** | CNN classifies the environment scenario and switches SMC parameters |
| **RL Agent (PPO)** | Proximal Policy Optimization learns continuous gain adaptation |

The pipeline is:

```text
environment map → AI agent (CNN or PPO) → adaptive SMC parameters → robot control
```

A **3D digital twin** web interface provides live simulation, controller comparison, replay, and export for demonstration and benchmarking.

---

## Quick Start

### 1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Launch the digital twin (recommended entry point)

```bash
python run_digital_twin.py
```

Open **[http://localhost:8000](http://localhost:8000)** in your browser.

Pre-trained CNN and RL models are included in `models/`. If they are missing, run:

```bash
python bootstrap_models.py
```

For frontend development with hot reload:

```bash
./run_digital_twin.sh
# UI at http://localhost:5173  ·  API at http://localhost:8000
```

### 3. Reproduce the full experiment pipeline

```bash
./run_experiments.sh
```

This generates the CNN dataset, trains the classifier, runs classical and adaptive SMC simulations, computes metrics, and writes plots and tables to `results/`.

If the CNN is already trained:

```bash
./run_simulations.sh
```

---

## Key Results

CNN-adaptive SMC shows scenario-dependent improvements over classical SMC:

| Scenario | RMSE | Final Error | Chattering |
|---|--:|--:|--:|
| Normal | 0.00% | 0.00% | 0.00% |
| Noise | −10.98% | −15.02% | **+35.53%** |
| Disturbance | +2.22% | **+36.96%** | −12.22% |
| Slip | +1.57% | **+32.27%** | −22.52% |
| Combined | −2.00% | +2.16% | **+27.67%** |

Positive percentages indicate improvement for the adaptive controller. Full tables and interpretation: [docs/RESULTS.md](docs/RESULTS.md).

---

## Repository Structure

```text
├── bootstrap_models.py       # One-shot CNN + RL model training
├── config.yaml               # Simulation, controller, and RL settings
├── docs/                     # Reports, presentation, and technical docs
├── frontend/                 # React + Three.js digital twin UI
├── models/                   # Pre-trained CNN and RL weights
├── run_digital_twin.py       # Start the web server (port 8000)
├── run_experiments.sh        # Full reproducible experiment pipeline
├── run_simulations.sh        # Simulations + evaluation only
├── scripts/                  # Report and presentation generators
├── src/
│   ├── api/                  # FastAPI + WebSocket server
│   ├── cnn/                  # Environment classifier
│   ├── controllers/          # SMC and adaptive parameter logic
│   ├── data_generation/      # Synthetic CNN dataset
│   ├── evaluation/           # Metrics and comparison scripts
│   ├── rl/                   # PPO agent and Gymnasium environment
│   ├── robot/                # Differential-drive kinematics
│   ├── simulation/           # Simulation engine and scenarios
│   └── visualization/        # Plotting utilities
└── requirements.txt
```

---

## Documentation

| Document | Description |
|---|---|
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/METHODOLOGY.md](docs/METHODOLOGY.md) | Robot model, controllers, CNN, dataset, metrics |
| [docs/RESULTS.md](docs/RESULTS.md) | Result tables and interpretation |
| [docs/DEMO.md](docs/DEMO.md) | Step-by-step digital twin demo guide |
| [docs/AI_Clinic_Research_Report.pdf](docs/AI_Clinic_Research_Report.pdf) | Full research report (PDF) |
| [docs/AI_Clinic_Defense_Presentation.pdf](docs/AI_Clinic_Defense_Presentation.pdf) | Defense presentation (PDF) |

---

## Manual Commands

<details>
<summary>Individual pipeline steps</summary>

```bash
# Dataset
python src/data_generation/generate_dataset.py
python src/data_generation/split_dataset.py

# CNN
python src/cnn/train_cnn.py
python src/cnn/test_cnn.py

# Simulations
python src/simulation/simulate_classical_smc_with_issues.py
python src/simulation/simulate_adaptive_smc.py

# Evaluation
python src/evaluation/compare_classical_vs_adaptive.py
python src/evaluation/compute_adaptive_improvement.py
python src/visualization/plot_controller_comparison.py
python src/evaluation/create_report_tables.py

# RL training
python -m src.rl.train_rl --quick          # ~2 min
python -m src.rl.train_rl --iterations 100 # full training
```

</details>

---

## Requirements

- Python 3.10+
- Node.js 18+ (optional — only for frontend development)
- PyTorch, FastAPI, Gymnasium, React, Three.js (see `requirements.txt` and `frontend/package.json`)

---

## Reproducibility

1. Create and activate a virtual environment.
2. `pip install -r requirements.txt`
3. `./run_experiments.sh`
4. Inspect outputs:
   - `results/cnn/` — classifier training and test results
   - `results/metrics/` — controller metrics
   - `results/plots/` — comparison figures
   - `results/tables/` — report CSV tables

---

## Future Work

- Real LiDAR or camera-based occupancy maps
- More realistic simulation environments (PyBullet, Gazebo, ROS)
- Physical differential-drive robot deployment
- Extended RL training with larger domain randomization

---

## Acknowledgement

The authors thank **aivancity** (Paris, France) and **Indrashil University** (Kadi, India) for providing the computational resources that supported this work.
