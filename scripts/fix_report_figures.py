#!/usr/bin/env python3
"""Regenerate report figures: consistent with paper tables, full time axes."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FIG_DIR = ROOT / "docs" / "assets" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

C_CLASSICAL = "#d62728"
C_CNN = "#00a98f"
C_RL = "#7c5cff"
C_FUZZY = "#ff9f40"
C_ORACLE = "#4a6080"
C_DESIRED = "#333333"

SCENARIOS = ["Normal", "Noise", "Disturbance", "Slip", "Combined"]

# Paper Table III — absolute metrics (classical, adaptive)
RMSE = {
    "Classical": [0.1465, 0.1599, 0.1876, 0.1796, 0.2357],
    "CNN-Adaptive": [0.1465, 0.1786, 0.1780, 0.1743, 0.2378],
}
CHATTER = {
    "Classical": [19.24, 76.48, 15.74, 7.88, 70.87],
    "CNN-Adaptive": [19.24, 49.14, 17.83, 9.72, 51.65],
}
# Paper Table IV — improvement (%) rows: scenario, cols: RMSE, Final, Effort, Chattering
IMPROVEMENT = np.array([
    [0.00, 0.00, 0.00, 0.00],
    [-11.65, -130.62, 5.84, 35.75],
    [5.12, 14.42, -5.57, -13.32],
    [2.94, 32.69, -10.94, -23.40],
    [-0.85, 1.20, -4.73, 27.12],
])
IMPROVEMENT_COLS = ["RMSE", "Final Error", "Effort", "Chattering"]

# Paper Table V — multi-controller comparison
MULTI = {
    "Noise\n(chattering)": [76.48, 70.50, 49.14, 49.32, 50.72],
    "Disturbance\n(final err, mm)": [20.92, 24.75, 17.90, 15.58, 32.75],
    "Slip\n(final err, mm)": [40.73, 30.39, 27.41, 27.44, 41.60],
    "Combined\n(chattering)": [72.79, 71.66, 51.65, 51.37, 48.88],
}
CONTROLLERS = ["Classical", "Fuzzy", "CNN", "Oracle", "RL"]
CTRL_COLORS = [C_CLASSICAL, C_FUZZY, C_CNN, C_ORACLE, C_RL]


def _run_simulation(controller_mode: str, total_time: float = 20.0):
    """Run a full simulation with aligned start, recording error every step."""
    from src.simulation.simulation_engine import SimulationEngine, SimulationConfig

    cfg = SimulationConfig(
        controller_mode=controller_mode,
        scenario_name="combined",
        trajectory_type="straight",
        enable_noise=True,
        enable_disturbance=True,
        enable_slip=True,
        total_time=total_time,
        initial_x=0.0,
        initial_y=0.0,
        initial_theta=0.0,
    )
    engine = SimulationEngine()
    engine.reset(cfg)
    engine.resume()

    times, errors = [], []
    while not engine.state.finished:
        engine.step()
        times.append(engine.state.time)
        errors.append(engine.state.tracking_error)

    path = engine.state.path_history
    desired = engine.state.desired_path
    return times, errors, path, desired


def fig_trajectory_and_error():
    """Fig 3 (trajectory) and Fig 4 (tracking error) with full time axes."""
    modes = [("classical", "Classical SMC", C_CLASSICAL),
             ("cnn_adaptive", "CNN-Adaptive SMC", C_CNN),
             ("rl_agent", "RL Agent (PPO)", C_RL)]

    results = {}
    for mode, label, color in modes:
        results[mode] = (_run_simulation(mode), label, color)

    # Trajectory
    fig, ax = plt.subplots(figsize=(9, 4.2))
    desired = results["classical"][0][3]
    dx = [p["x"] for p in desired]
    dy = [p["y"] for p in desired]
    ax.plot(dx, dy, color=C_DESIRED, linestyle="--", linewidth=1.4, label="Reference path", zorder=5)

    for mode, ((times, errors, path, _), label, color) in results.items():
        xs = [p["x"] for p in path]
        ys = [p["y"] for p in path]
        ax.plot(xs, ys, color=color, linewidth=1.7, label=label, alpha=0.9)

    ax.set_xlabel("x position [m]", fontsize=11)
    ax.set_ylabel("y position [m]", fontsize=11)
    ax.set_title("Robot Trajectories — Combined Scenario (noise + disturbance + slip)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best", fontsize=9)
    fig.savefig(FIG_DIR / "fig03_trajectory_comparison.png", dpi=200,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)

    # Tracking error, full 0..T axis
    fig, ax = plt.subplots(figsize=(9, 4.0))
    for mode, ((times, errors, _, _), label, color) in results.items():
        ax.plot(times, errors, color=color, linewidth=1.5, label=label, alpha=0.9)

    ax.set_xlabel("Time [s]", fontsize=11)
    ax.set_ylabel("Tracking error [m]", fontsize=11)
    ax.set_title("Tracking Error Over Time — Combined Scenario", fontsize=12, fontweight="bold")
    ax.set_xlim(0, max(times))
    ax.set_ylim(bottom=0)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    fig.savefig(FIG_DIR / "fig04_tracking_error.png", dpi=200,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  fig03, fig04 done")


def _grouped_bars(data: dict, ylabel: str, title: str, outname: str):
    x = np.arange(len(SCENARIOS))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9, 4.0))
    ax.bar(x - width / 2, data["Classical"], width, label="Classical SMC",
           color=C_CLASSICAL, alpha=0.88, edgecolor="#444", linewidth=0.5)
    ax.bar(x + width / 2, data["CNN-Adaptive"], width, label="CNN-Adaptive SMC",
           color=C_CNN, alpha=0.88, edgecolor="#444", linewidth=0.5)
    ax.set_xticks(x)
    ax.set_xticklabels(SCENARIOS)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    fig.savefig(FIG_DIR / outname, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_bars():
    _grouped_bars(RMSE, "RMSE tracking error [m]",
                  "RMSE Tracking Error per Scenario (Table 3)", "fig05_rmse_bars.png")
    _grouped_bars(CHATTER, "Chattering index",
                  "Chattering Index per Scenario (Table 3)", "fig06_chattering_bars.png")
    print("  fig05, fig06 done")


def fig_heatmap():
    """Improvement heatmap (paper Fig. 8 style)."""
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    vmax = 40
    im = ax.imshow(np.clip(IMPROVEMENT, -vmax, vmax), cmap="RdYlGn",
                   vmin=-vmax, vmax=vmax, aspect="auto")

    ax.set_xticks(range(len(IMPROVEMENT_COLS)))
    ax.set_xticklabels(IMPROVEMENT_COLS, fontsize=10)
    ax.set_yticks(range(len(SCENARIOS)))
    ax.set_yticklabels(SCENARIOS, fontsize=10)
    ax.set_title("CNN-Adaptive Improvement over Classical SMC (%)",
                 fontsize=12, fontweight="bold", pad=10)

    for i in range(len(SCENARIOS)):
        for j in range(len(IMPROVEMENT_COLS)):
            val = IMPROVEMENT[i, j]
            ax.text(j, i, f"{val:+.1f}", ha="center", va="center",
                    fontsize=9, fontweight="bold",
                    color="black" if abs(val) < 30 else "white")

    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Improvement (%)", fontsize=9)
    fig.savefig(FIG_DIR / "fig09_improvement_heatmap.png", dpi=200,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  fig09 done")


def fig_multicontroller():
    """Five-controller comparison (paper Fig. 9 style)."""
    groups = list(MULTI.keys())
    x = np.arange(len(groups))
    width = 0.15

    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    for k, (ctrl, color) in enumerate(zip(CONTROLLERS, CTRL_COLORS)):
        vals = [MULTI[g][k] for g in groups]
        offset = (k - 2) * width
        bars = ax.bar(x + offset, vals, width, label=ctrl, color=color,
                      alpha=0.88, edgecolor="#444", linewidth=0.5)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6,
                    f"{val:.0f}", ha="center", va="bottom", fontsize=6.5)

    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontsize=9)
    ax.set_ylabel("Metric value (lower is better)", fontsize=10)
    ax.set_title("Multi-Controller Comparison (Table 5)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.13))
    ax.grid(axis="y", alpha=0.3)
    fig.savefig(FIG_DIR / "fig10_multicontroller.png", dpi=200,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("  fig10 done")


if __name__ == "__main__":
    print("Regenerating report figures...")
    fig_trajectory_and_error()
    fig_bars()
    fig_heatmap()
    fig_multicontroller()
    print("Done.")
