# CNN-Adaptive Sliding Mode Control for Autonomous Robots

## Project Overview

This project implements and evaluates a **CNN-adaptive Sliding Mode Controller** for a differential-drive autonomous mobile robot.

The main goal is to compare:

1. Classical Sliding Mode Control
2. CNN-adaptive Sliding Mode Control

The comparison is performed under different operating conditions:

- Normal motion
- Sensor noise
- External disturbance
- Wheel slip
- Combined uncertainty

---

## Project Idea

Sliding Mode Control, also called **SMC**, is a robust nonlinear control technique. It is useful for autonomous robots because it can handle disturbances and model uncertainty.

However, classical SMC usually uses fixed control parameters. These fixed parameters may not be optimal under all conditions. For example, noisy sensors may require smoother control, while external disturbances may require stronger correction.

This project adds a **Convolutional Neural Network**, or **CNN**, module that classifies the environment condition and adapts the SMC parameters accordingly.

The complete pipeline is:

```text
environment map → CNN prediction → scenario class → adaptive SMC parameters → robot control
```

---

## Robot Model

The project uses a **differential-drive mobile robot**.

The robot state is defined as:

| Variable | Meaning |
|---|---|
| `x` | Position on the x-axis |
| `y` | Position on the y-axis |
| `theta` | Robot orientation angle |
| `v` | Linear velocity |
| `omega` | Angular velocity |

The kinematic model is:

```text
x_dot = v cos(theta)
y_dot = v sin(theta)
theta_dot = omega
```

At each simulation step, the robot state is updated using:

```text
x_new = x + v cos(theta) Δt
y_new = y + v sin(theta) Δt
theta_new = theta + omega Δt
```

---

## Controllers

### Classical Sliding Mode Control

The classical SMC controller uses fixed parameters during the whole simulation.

The main parameters are:

| Parameter | Meaning |
|---|---|
| `lambda_x` | Sliding surface gain for x-position error |
| `lambda_y` | Sliding surface gain for y-position error |
| `lambda_theta` | Sliding surface gain for orientation error |
| `k_v` | Linear velocity correction gain |
| `k_omega` | Angular velocity correction gain |
| `phi` | Boundary layer parameter for chattering reduction |
| `omega_smoothing` | Smoothing factor for angular velocity command |

### CNN-Adaptive Sliding Mode Control

The adaptive controller uses a CNN to classify the scenario.

The CNN predicts one of the following classes:

| Label | Scenario |
|---:|---|
| 0 | Normal |
| 1 | Noise |
| 2 | Disturbance |
| 3 | Slip |
| 4 | Combined |

Each predicted scenario is mapped to a different set of SMC parameters.

For example:

- In a noisy scenario, the controller uses smoother parameters to reduce chattering.
- In a disturbance scenario, the controller uses stronger correction gains.
- In a slip scenario, the controller adapts gains to handle reduced motion effectiveness.
- In a combined scenario, the controller balances smoothing and correction.

---

## Project Structure

```text
ai_smc_autonomous_robot/

├── data/
│   └── generated/

├── models/
│   └── cnn_environment_classifier.pt

├── results/
│   ├── cnn/
│   ├── logs/
│   ├── metrics/
│   ├── plots/
│   └── tables/

├── src/
│   ├── cnn/
│   │   ├── cnn_model.py
│   │   ├── dataset.py
│   │   ├── predictor.py
│   │   ├── train_cnn.py
│   │   └── test_cnn.py
│   │
│   ├── controllers/
│   │   ├── adaptive_parameters.py
│   │   ├── adaptive_smc_controller.py
│   │   ├── parameter_filter.py
│   │   ├── sliding_surface.py
│   │   ├── smc_controller.py
│   │   ├── switching_functions.py
│   │   └── tracking_error.py
│   │
│   ├── data_generation/
│   │   ├── environment_generator.py
│   │   ├── generate_dataset.py
│   │   ├── labels.py
│   │   ├── preview_dataset.py
│   │   └── split_dataset.py
│   │
│   ├── evaluation/
│   │   ├── compare_classical_vs_adaptive.py
│   │   ├── compare_issue_scenario_metrics.py
│   │   ├── compare_switching_metrics.py
│   │   ├── compute_adaptive_improvement.py
│   │   ├── create_report_tables.py
│   │   └── metrics.py
│   │
│   ├── robot/
│   │   ├── differential_drive.py
│   │   └── robot_state.py
│   │
│   ├── simulation/
│   │   ├── disturbances.py
│   │   ├── noise.py
│   │   ├── simulate_adaptive_smc.py
│   │   ├── simulate_classical_smc.py
│   │   ├── simulate_classical_smc_with_issues.py
│   │   ├── trajectory_generator.py
│   │   └── uncertainty.py
│   │
│   ├── utils/
│   │   └── logger.py
│   │
│   └── visualization/
│       ├── plot_controller_comparison.py
│       ├── plot_metric_bars.py
│       └── plot_results.py

├── requirements.txt
├── run_experiments.sh
├── run_simulations.sh
└── README.md
```

---

## Installation

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Run the Full Pipeline

To reproduce the full experiment, run:

```bash
./run_experiments.sh
```

This script performs the following steps:

1. Generate the CNN dataset
2. Split the dataset into train, validation, and test sets
3. Train the CNN
4. Test the CNN
5. Run classical SMC simulations
6. Run CNN-adaptive SMC simulations
7. Compute metrics
8. Generate comparison plots
9. Generate report tables

---

## Run Only Simulations and Evaluation

If the CNN is already trained, run:

```bash
./run_simulations.sh
```

This script runs:

- Classical SMC simulations
- CNN-adaptive SMC simulations
- Metrics computation
- Plots generation
- Report table generation

---

## Extended Multi-Controller Experiments

To run the full benchmark (classical, fuzzy-SMC, CNN-adaptive, oracle, and RL-adaptive controllers) plus realistic-map CNN training:

```bash
./run_major_experiments.sh
```

To regenerate metrics, plots, and the project report PDF:

```bash
./generate_report.sh
```

New modules include:

- `src/simulation/run_episode.py` — shared simulation loop
- `src/controllers/fuzzy_smc_controller.py` — fuzzy gain scheduling baseline
- `src/controllers/rl_adaptive_smc_controller.py` — PPO preset selector
- `src/rl/smc_parameter_env.py` — RL training environment
- `src/data_generation/realistic_map_generator.py` — cluttered occupancy maps
- `src/cnn/train_realistic_cnn.py` — retrain CNN on realistic maps
- `src/evaluation/compare_all_controllers.py` — multi-controller metrics

---

## Manual Commands

### Generate CNN Dataset

```bash
python src/data_generation/generate_dataset.py
python src/data_generation/split_dataset.py
python src/data_generation/preview_dataset.py
```

### Train and Test CNN

```bash
python src/cnn/train_cnn.py
python src/cnn/test_cnn.py
python src/cnn/plot_training_history.py
```

### Run Classical SMC

```bash
python src/simulation/simulate_classical_smc_with_issues.py
```

### Run CNN-Adaptive SMC

```bash
python src/simulation/simulate_adaptive_smc.py
```

### Compare Controllers

```bash
python src/evaluation/compare_classical_vs_adaptive.py
python src/evaluation/compute_adaptive_improvement.py
```

### Generate Plots and Tables

```bash
python src/visualization/plot_controller_comparison.py
python src/visualization/plot_metric_bars.py
python src/evaluation/create_report_tables.py
```

---

## Dataset

The CNN dataset is synthetically generated.

Each sample is a `64 × 64` grayscale environment map.

The generated classes are:

| Scenario | Label | Map Representation |
|---|---:|---|
| Normal | 0 | Clean path line |
| Noise | 1 | Path with noisy pixels |
| Disturbance | 2 | Path with disturbance marker |
| Slip | 3 | Path with slippery zone band |
| Combined | 4 | Noise, disturbance marker, and slip zone |

The dataset contains:

- 1500 total samples
- 300 samples per class
- 1050 training samples
- 225 validation samples
- 225 test samples

---

## CNN Architecture

The CNN input is:

```text
1 × 64 × 64
```

The output is:

```text
5
```

which corresponds to the five scenario classes.

The model contains:

- Three convolution blocks
- Batch normalization
- ReLU activation
- Max pooling
- A fully connected classifier
- Dropout for regularization

The CNN achieved perfect classification accuracy on the synthetic test set.

```text
Test Accuracy: 1.0000
```

This validates the CNN pipeline on the generated dataset. However, since the dataset is synthetic and visually simple, more realistic sensor maps should be used in future work.

---

## Simulation Scenarios

The project evaluates the controllers under five scenarios:

| Scenario | Description |
|---|---|
| Normal | No noise, no disturbance, no slip |
| Noise | Sensor noise is added to position and orientation measurements |
| Disturbance | A sudden external push is applied to the robot |
| Slip | Wheel slip reduces the effective velocity of the robot |
| Combined | Noise, disturbance, and slip are applied together |

---

## Evaluation Metrics

The controllers are evaluated using the following metrics:

| Metric | Meaning |
|---|---|
| Mean tracking error | Average tracking error during simulation |
| RMSE tracking error | Root mean square tracking error |
| Maximum tracking error | Worst tracking error during simulation |
| Final tracking error | Error at the final simulation time |
| Control effort | Total intensity of control commands |
| Chattering index | Oscillation level of the angular velocity command |
| Settling time | Time needed for the error to stay below a threshold |

---

## Main Results

The final result tables are saved in:

```text
results/tables/report_controller_metrics_table.csv
results/tables/report_improvement_table.csv
```

The latest improvement summary is:

| Scenario | RMSE Improvement | Final Error Improvement | Control Effort Improvement | Chattering Improvement |
|---|---:|---:|---:|---:|
| Normal | 0.00% | 0.00% | 0.00% | 0.00% |
| Noise | -10.98% | -15.02% | 6.89% | 35.53% |
| Disturbance | 2.22% | 36.96% | -11.10% | -12.22% |
| Slip | 1.57% | 32.27% | -12.83% | -22.52% |
| Combined | -2.00% | 2.16% | -5.62% | 27.67% |

---

## Result Interpretation

The results show that the CNN-adaptive SMC does not improve every metric equally. Instead, it demonstrates adaptive behavior depending on the scenario.

### Normal Scenario

In the normal scenario, the CNN-adaptive SMC behaves the same as the classical SMC because both use the same control parameters.

### Noise Scenario

In the noise scenario, the CNN-adaptive SMC reduces chattering by approximately `35.53%`. However, this comes with a loss in tracking accuracy, as RMSE increases by approximately `10.98%`.

This shows a trade-off between smoother control and precise tracking.

### Disturbance Scenario

In the disturbance scenario, the CNN-adaptive SMC improves RMSE by approximately `2.22%` and final tracking error by approximately `36.96%`.

This means the adaptive controller recovers better after external disturbance.

### Slip Scenario

In the slip scenario, the CNN-adaptive SMC improves RMSE by approximately `1.57%` and final error by approximately `32.27%`.

This indicates better recovery under wheel slip conditions.

### Combined Scenario

In the combined scenario, the CNN-adaptive SMC reduces chattering by approximately `27.67%` and slightly improves final error by approximately `2.16%`.

However, RMSE becomes slightly worse by approximately `2.00%`, showing that the combined condition remains challenging.

---

## Conclusion

This project successfully implements a complete CNN-adaptive Sliding Mode Control pipeline for an autonomous differential-drive robot.

The project includes:

- A differential-drive robot model
- A classical Sliding Mode Controller
- Anti-chattering switching functions
- Sensor noise, disturbance, slip, and combined uncertainty scenarios
- Synthetic environment maps for CNN training
- A CNN classifier for scenario recognition
- CNN-adaptive SMC parameter selection
- Quantitative comparison between classical SMC and CNN-adaptive SMC

The results show that CNN-adaptive SMC can:

- Reduce chattering in noisy and combined conditions
- Improve final recovery under disturbance and slip
- Adapt controller parameters based on predicted environment conditions

However, the results also show a trade-off between tracking precision and smoother control.

---

## Future Work

Possible extensions include:

- Test the controller in other simulation environments (PyBullet, Gazebo, ROS)
- Use reinforcement learning to improve scenario prediction and adaptive parameter selection
- Use real LiDAR or camera-based occupancy maps
- Deploy the method on a physical differential-drive robot

---

## Reproducibility Checklist

To reproduce the project from scratch:

1. Create and activate the virtual environment.
2. Install the dependencies.
3. Run:

```bash
./run_experiments.sh
```

4. Check CNN test results in:

```text
results/cnn/
```

5. Check controller metrics in:

```text
results/metrics/
```

6. Check plots in:

```text
results/plots/
```

7. Check report tables in:

```text
results/tables/
```

---

## Repository Commands

To commit the final project state:

```bash
git status
git add .
git commit -m "Clean project structure and add reproducible run commands"
git push
```