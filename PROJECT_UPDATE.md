# Project Update — CNN-Adaptive Sliding Mode Control for Autonomous Robots

**Project:** AI-SMC Autonomous Robot  
**Status:** Complete  
**Last updated:** May 27, 2026

---

## 1. Project Summary

This project implements and evaluates a **CNN-adaptive Sliding Mode Controller (SMC)** for a differential-drive autonomous mobile robot. The system compares classical SMC (fixed parameters) against CNN-adaptive SMC (parameters tuned per environment scenario) under five operating conditions: normal, sensor noise, external disturbance, wheel slip, and combined uncertainty.

The full pipeline is:

```text
Synthetic environment map → CNN scenario classification → Adaptive SMC parameters → Robot control → Metrics & comparison
```

---

## 2. Objectives

| Objective | Status |
|---|---|
| Model a differential-drive robot with kinematic simulation | Done |
| Implement classical SMC with anti-chattering switching | Done |
| Generate synthetic CNN training data for 5 scenario classes | Done |
| Train and evaluate a CNN environment classifier | Done |
| Map CNN predictions to scenario-specific SMC parameters | Done |
| Simulate both controllers under all 5 scenarios | Done |
| Quantitatively compare classical vs adaptive SMC | Done |
| Generate plots, tables, and reproducible run scripts | Done |
| Optional PyBullet path replay visualization | Done |

---

## 3. What Was Implemented

### 3.1 Robot Model (`src/robot/`)

- **`RobotState`** — Stores position `(x, y)`, orientation `theta`, and velocities.
- **`DifferentialDriveRobot`** — Kinematic model with wheel base and radius; updates state each timestep using linear and angular velocity commands.

### 3.2 Controllers (`src/controllers/`)

- **`SlidingModeController`** — Classical SMC with sliding surface, tracking error, and velocity limits.
- **`AdaptiveSlidingModeController`** — Wraps SMC and supports runtime parameter updates with smoothing via a parameter filter.
- **`switching_functions.py`** — Sign, saturation, and tanh switching to reduce chattering.
- **`sliding_surface.py`** — Sliding surface computation for position and orientation errors.
- **`tracking_error.py`** — Reference vs actual state error with angle normalization.
- **`adaptive_parameters.py`** — Pre-tuned SMC parameter sets for each of the 5 scenarios.
- **`parameter_filter.py`** — Exponential smoothing to avoid abrupt parameter jumps during adaptation.
- **`SimpleTrackingController`** — Baseline controller for initial validation.

### 3.3 Simulation Environment (`src/simulation/`)

- **`trajectory_generator.py`** — Straight, circular, and S-curve reference trajectories.
- **`noise.py`** — Gaussian sensor noise on position and orientation measurements.
- **`disturbances.py`** — External push applied at a configurable time window.
- **`uncertainty.py`** — Wheel slip model that reduces effective motion.
- **`simulate_classical_smc_with_issues.py`** — Classical SMC runs for all 5 scenarios.
- **`simulate_adaptive_smc.py`** — CNN-adaptive SMC runs for all 5 scenarios.
- **`compare_switching_functions.py`** — Comparison of sign vs sat vs tanh switching.
- Unit-style test scripts for trajectories, sliding surface, tracking error, and robot motion.

### 3.4 CNN Module (`src/cnn/`)

- **`EnvironmentMapGenerator`** (in data generation) produces 64×64 grayscale maps per scenario.
- **`EnvironmentCNN`** — 3 conv blocks (BatchNorm + ReLU + MaxPool) + FC classifier with dropout.
- **`EnvironmentMapDataset`** — PyTorch dataset loader for train/val/test splits.
- **`train_cnn.py`** — Training loop with MPS/CUDA/CPU device support.
- **`test_cnn.py`** — Test-set evaluation and accuracy reporting.
- **`predictor.py`** — Loads trained model and returns scenario label + confidence at inference time.

**CNN classes:**

| Label | Scenario |
|---:|---|
| 0 | Normal |
| 1 | Noise |
| 2 | Disturbance |
| 3 | Slip |
| 4 | Combined |

**Dataset:** 1,500 samples (300 per class), split 70% / 15% / 15% for train / validation / test.

### 3.5 Data Generation (`src/data_generation/`)

- **`generate_dataset.py`** — Creates synthetic maps and saves images + NumPy arrays.
- **`split_dataset.py`** — Produces train, validation, and test CSV manifests.
- **`preview_dataset.py`** — Visual preview of generated samples.
- **`labels.py`** — Scenario name to label mapping.

### 3.6 Evaluation (`src/evaluation/`)

- **`metrics.py`** — Tracking error (mean, RMSE, max, final), control effort, chattering index, settling time.
- **`compare_classical_vs_adaptive.py`** — Side-by-side metrics for both controllers.
- **`compute_adaptive_improvement.py`** — Percentage improvement of adaptive over classical.
- **`create_report_tables.py`** — Exports final CSV report tables.
- **`compare_issue_scenario_metrics.py`** — Per-scenario issue analysis.
- **`compare_switching_metrics.py`** — Switching function comparison metrics.

### 3.7 Visualization (`src/visualization/`)

- **`plot_results.py`** — Robot path, tracking error, sliding surfaces, control signals.
- **`plot_controller_comparison.py`** — Trajectory, error, and control comparisons per scenario.
- **`plot_metric_bars.py`** — Grouped bar charts for key metrics.
- **`animate_robot.py`** — 2D animation of classical vs adaptive paths.

### 3.8 PyBullet Visualization (`src/pybullet_sim/`)

- **`replay_controller_paths.py`** — Replays saved simulation logs in PyBullet for side-by-side classical vs adaptive path visualization.

### 3.9 Utilities & Configuration

- **`config.yaml`** — Simulation timing, robot geometry, controller defaults, trajectory and noise settings.
- **`utils/logger.py`** — Saves per-timestep simulation logs to CSV.
- **`utils/config_loader.py`** — YAML config loader.
- **`run_experiments.sh`** — Full end-to-end pipeline (11 steps).
- **`run_simulations.sh`** — Simulations + evaluation only (skips CNN training).

---

## 4. End-to-End Pipeline

Running `./run_experiments.sh` executes:

1. Generate CNN dataset  
2. Split dataset (train / val / test)  
3. Train CNN classifier  
4. Test CNN on held-out data  
5. Run classical SMC simulations (all scenarios)  
6. Run CNN-adaptive SMC simulations (all scenarios)  
7. Compare controllers and compute metrics  
8. Compute adaptive improvement percentages  
9. Generate comparison plots  
10. Generate metric bar charts  
11. Export report tables  

Output locations:

| Artifact | Path |
|---|---|
| CNN training results | `results/cnn/` |
| Simulation logs | `results/logs/` |
| Computed metrics | `results/metrics/` |
| Plots | `results/plots/` |
| Report tables | `results/tables/` |
| Trained model | `models/cnn_environment_classifier.pt` |

---

## 5. Key Results

CNN test accuracy on the synthetic dataset: **100%** (validates the classification pipeline on generated data).

Adaptive SMC improvement over classical SMC (from report tables):

| Scenario | RMSE | Final Error | Control Effort | Chattering |
|---|---:|---:|---:|---:|
| Normal | 0.00% | 0.00% | 0.00% | 0.00% |
| Noise | -10.98% | -15.02% | +6.89% | **+35.53%** |
| Disturbance | **+2.22%** | **+36.96%** | -11.10% | -12.22% |
| Slip | **+1.57%** | **+32.27%** | -12.83% | -22.52% |
| Combined | -2.00% | +2.16% | -5.62% | **+27.67%** |

Positive percentages mean adaptive SMC performed better on that metric.

### Interpretation

- **Normal:** Both controllers use the same parameters — no difference expected.
- **Noise:** Adaptive SMC reduces chattering (~36%) at the cost of slightly worse tracking accuracy (trade-off for smoother control).
- **Disturbance / Slip:** Adaptive SMC improves final tracking error recovery (~33–37%).
- **Combined:** Chattering reduction (~28%) with mixed tracking results — combined uncertainty remains the hardest case.

---

## 6. Technical Highlights

1. **Scenario-aware control** — CNN output selects from five pre-tuned parameter sets rather than using one fixed gain schedule.
2. **Parameter smoothing** — `ParameterFilter` prevents discontinuous control when parameters change.
3. **Anti-chattering design** — Saturation-based switching, boundary layer `phi`, angular velocity smoothing, and dead zones.
4. **Reproducibility** — Shell scripts, fixed random seeds, CSV logs, and centralized config.
5. **Modular architecture** — Robot, controller, simulation, CNN, evaluation, and visualization are separated for independent testing.

---

## 7. Dependencies

Core stack (see `requirements.txt`):

- Python scientific stack: NumPy, SciPy, Pandas, Matplotlib  
- Deep learning: PyTorch, TorchVision  
- ML utilities: scikit-learn, tqdm  
- Config: PyYAML  
- Image: OpenCV, Pillow  
- Optional RL stack: Gymnasium, Stable-Baselines3  
- Optional visualization: PyBullet (for `replay_controller_paths.py`)

---

## 8. How to Reproduce

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
./run_experiments.sh
```

For simulation and evaluation only (CNN already trained):

```bash
./run_simulations.sh
```

---

## 9. Known Limitations

- CNN training data uses **synthetic** 64×64 maps, not real sensor data (LiDAR/camera).
- Scenario classification is based on map appearance, not live sensor feedback during motion.
- Adaptive parameters are **hand-tuned** per scenario, not learned end-to-end.
- Combined scenario shows trade-offs — not all metrics improve simultaneously.
- PyBullet replay is visualization-only; physics is not re-simulated in PyBullet.

---

## 10. Future Work

- Test the controller in other simulation environments (PyBullet, Gazebo, ROS).
- Use reinforcement learning to improve scenario prediction and adaptive SMC parameter selection.
- Replace synthetic maps with real sensor-based occupancy grids.
- Deploy on a physical differential-drive robot.

---

## 11. File Inventory (Source Modules)

```text
src/
├── cnn/                  # CNN model, training, testing, inference
├── controllers/          # SMC, adaptive SMC, switching, parameters
├── data_generation/      # Synthetic dataset creation and splitting
├── evaluation/           # Metrics and comparison scripts
├── pybullet_sim/         # 3D path replay
├── robot/                # Differential-drive kinematic model
├── simulation/           # Scenarios, disturbances, simulation runners
├── utils/                # Logging and config
└── visualization/        # Plots and animations
```

---

## 12. Conclusion

The project delivers a complete, reproducible pipeline from synthetic environment classification to adaptive robot control and quantitative evaluation. Classical SMC and CNN-adaptive SMC were implemented, tested under five uncertainty scenarios, and compared using tracking, control effort, and chattering metrics. Results confirm that CNN-adaptive SMC can reduce chattering in noisy conditions and improve recovery after disturbances and slip, while highlighting the inherent trade-off between smooth control and tracking precision.

For setup and command reference, see [README.md](README.md).
