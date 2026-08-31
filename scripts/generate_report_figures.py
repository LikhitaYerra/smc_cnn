#!/usr/bin/env python3
"""Generate all figures for the research report PDF."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FIG_DIR = ROOT / "docs" / "assets" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Consistent colour palette
C_CLASSICAL = "#ff6b6b"
C_CNN = "#00d4aa"
C_RL = "#7c5cff"
C_DESIRED = "#4a6080"


def fig_architecture():
    """System architecture flowchart."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("System Architecture — CNN-Adaptive SMC Pipeline", fontsize=13, fontweight="bold", pad=12)

    boxes = [
        (0.3, 3.8, "Environment\nMap\n64×64", "#1a2332", "white"),
        (2.2, 3.8, "CNN\nClassifier\n5 classes", C_CNN, "black"),
        (4.1, 3.8, "Parameter\nLookup\nTable", "#ffd93d", "black"),
        (6.0, 3.8, "SMC\nController", "#3498db", "white"),
        (7.9, 3.8, "Differential\nDrive Robot", C_CLASSICAL, "white"),
    ]
    for x, y, label, bg, fg in boxes:
        rect = mpatches.FancyBboxPatch(
            (x, y), 1.5, 1.2, boxstyle="round,pad=0.08",
            facecolor=bg, edgecolor="#333", linewidth=1.5,
        )
        ax.add_patch(rect)
        ax.text(x + 0.75, y + 0.6, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=fg)

    for x in [1.8, 3.7, 5.6, 7.5]:
        ax.annotate("", xy=(x + 0.35, 4.4), xytext=(x, 4.4),
                    arrowprops=dict(arrowstyle="->", color="#333", lw=2))

    # RL branch
    ax.text(5.0, 2.5, "Alternative: PPO RL Agent", ha="center", fontsize=10,
            fontweight="bold", color=C_RL)
    rl_boxes = [
        (2.2, 1.0, "Robot State\n+ Error", "#1a2332", "white"),
        (4.1, 1.0, "PPO\nPolicy", C_RL, "white"),
        (6.0, 1.0, "Continuous\nSMC Gains", "#3498db", "white"),
    ]
    for x, y, label, bg, fg in rl_boxes:
        rect = mpatches.FancyBboxPatch(
            (x, y), 1.5, 1.0, boxstyle="round,pad=0.08",
            facecolor=bg, edgecolor=C_RL, linewidth=1.5, linestyle="--",
        )
        ax.add_patch(rect)
        ax.text(x + 0.75, y + 0.5, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=fg)

    for x in [3.7, 5.6]:
        ax.annotate("", xy=(x + 0.35, 1.5), xytext=(x, 1.5),
                    arrowprops=dict(arrowstyle="->", color=C_RL, lw=1.5))

    ax.annotate("", xy=(6.75, 3.8), xytext=(6.75, 2.0),
                arrowprops=dict(arrowstyle="->", color=C_RL, lw=1.5, linestyle="dashed"))

    # Digital twin banner
    rect = mpatches.FancyBboxPatch(
        (0.3, 0.1), 9.1, 0.6, boxstyle="round,pad=0.05",
        facecolor="#0b3d5c", edgecolor=C_CNN, linewidth=1.5,
    )
    ax.add_patch(rect)
    ax.text(4.85, 0.4, "3D Digital Twin — React + Three.js + FastAPI WebSocket",
            ha="center", va="center", fontsize=9, color="white", fontweight="bold")

    out = FIG_DIR / "fig01_architecture.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def fig_cnn_samples():
    """Grid of CNN environment map samples."""
    from src.data_generation.environment_generator import EnvironmentMapGenerator

    gen = EnvironmentMapGenerator(map_size=64, seed=42)
    scenarios = ["normal", "noise", "disturbance", "slip", "combined"]
    titles = ["Normal", "Noise", "Disturbance", "Slip", "Combined"]

    fig, axes = plt.subplots(1, 5, figsize=(10, 2.5))
    fig.suptitle("CNN Environment Map Samples (64×64 grayscale)", fontsize=12, fontweight="bold")

    for ax, scenario, title in zip(axes, scenarios, titles):
        img = gen.generate(scenario)
        ax.imshow(img, cmap="gray", vmin=0, vmax=1)
        ax.set_title(title, fontsize=10)
        ax.axis("off")

    out = FIG_DIR / "fig02_cnn_samples.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def _run_simulation(controller_mode: str, scenario: str = "combined", total_time: float = 15.0):
    from src.simulation.simulation_engine import SimulationEngine, SimulationConfig

    cfg = SimulationConfig(
        controller_mode=controller_mode,
        scenario_name=scenario,
        trajectory_type="straight",
        enable_noise=True,
        enable_disturbance=True,
        enable_slip=True,
        total_time=total_time,
    )
    engine = SimulationEngine()
    engine.reset(cfg)
    engine.resume()
    while not engine.state.finished:
        engine.step()
    return engine


def fig_trajectory_comparison():
    """Overlay trajectories for 3 controllers."""
    modes = [("classical", "Classical SMC", C_CLASSICAL),
             ("cnn_adaptive", "CNN-Adaptive", C_CNN),
             ("rl_agent", "RL Agent (PPO)", C_RL)]

    fig, ax = plt.subplots(figsize=(9, 5))
    desired = None

    for mode, label, color in modes:
        engine = _run_simulation(mode)
        path = engine.state.path_history
        xs = [p["x"] for p in path]
        ys = [p["y"] for p in path]
        ax.plot(xs, ys, color=color, linewidth=2, label=label, alpha=0.85)
        if desired is None:
            desired = engine.state.desired_path
            dx = [p["x"] for p in desired]
            dy = [p["y"] for p in desired]
            ax.plot(dx, dy, color=C_DESIRED, linestyle="--", linewidth=1.5, label="Desired path")

    ax.set_xlabel("x position [m]", fontsize=11)
    ax.set_ylabel("y position [m]", fontsize=11)
    ax.set_title("Trajectory Comparison — Combined Scenario (noise + disturbance + slip)",
                 fontsize=12, fontweight="bold")
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)

    out = FIG_DIR / "fig03_trajectory_comparison.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def fig_tracking_error():
    """Tracking error over time for 3 controllers."""
    modes = [("classical", "Classical SMC", C_CLASSICAL),
             ("cnn_adaptive", "CNN-Adaptive", C_CNN),
             ("rl_agent", "RL Agent (PPO)", C_RL)]

    fig, ax = plt.subplots(figsize=(9, 4.5))

    for mode, label, color in modes:
        engine = _run_simulation(mode)
        history = engine.state.error_history
        times = [h["t"] for h in history]
        errors = [h["error"] for h in history]
        ax.plot(times, errors, color=color, linewidth=1.8, label=label, alpha=0.9)

    ax.set_xlabel("Time [s]", fontsize=11)
    ax.set_ylabel("Tracking error [m]", fontsize=11)
    ax.set_title("Tracking Error Over Time — Combined Scenario", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)
    ax.set_ylim(bottom=0)

    out = FIG_DIR / "fig04_tracking_error.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def fig_rmse_bars():
    """RMSE bar chart across scenarios."""
    from src.simulation.comparison_runner import run_single_benchmark

    scenarios = ["normal", "noise", "disturbance", "slip", "combined"]
    classical = []
    cnn = []

    for sc in scenarios:
        flags = dict(
            enable_noise=sc in ("noise", "combined"),
            enable_disturbance=sc in ("disturbance", "combined"),
            enable_slip=sc in ("slip", "combined"),
        )
        c = run_single_benchmark("classical", scenario_name=sc, total_time=10.0, **flags)
        a = run_single_benchmark("cnn_adaptive", scenario_name=sc, total_time=10.0, **flags)
        classical.append(c["metrics"]["rmse_tracking_error"])
        cnn.append(a["metrics"]["rmse_tracking_error"])

    x = np.arange(len(scenarios))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x - width / 2, classical, width, label="Classical SMC", color=C_CLASSICAL, alpha=0.85)
    ax.bar(x + width / 2, cnn, width, label="CNN-Adaptive SMC", color=C_CNN, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in scenarios])
    ax.set_ylabel("RMSE tracking error [m]", fontsize=11)
    ax.set_title("RMSE Comparison Across Scenarios", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    out = FIG_DIR / "fig05_rmse_bars.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def fig_chattering_bars():
    """Chattering index bar chart."""
    from src.simulation.comparison_runner import run_single_benchmark

    scenarios = ["normal", "noise", "disturbance", "slip", "combined"]
    classical = []
    cnn = []

    for sc in scenarios:
        flags = dict(
            enable_noise=sc in ("noise", "combined"),
            enable_disturbance=sc in ("disturbance", "combined"),
            enable_slip=sc in ("slip", "combined"),
        )
        c = run_single_benchmark("classical", scenario_name=sc, total_time=10.0, **flags)
        a = run_single_benchmark("cnn_adaptive", scenario_name=sc, total_time=10.0, **flags)
        classical.append(c["metrics"]["chattering_index"])
        cnn.append(a["metrics"]["chattering_index"])

    x = np.arange(len(scenarios))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(x - width / 2, classical, width, label="Classical SMC", color=C_CLASSICAL, alpha=0.85)
    ax.bar(x + width / 2, cnn, width, label="CNN-Adaptive SMC", color=C_CNN, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels([s.capitalize() for s in scenarios])
    ax.set_ylabel("Chattering index", fontsize=11)
    ax.set_title("Chattering Index Comparison Across Scenarios", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    out = FIG_DIR / "fig06_chattering_bars.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def fig_controller_benchmark():
    """3-controller combined-scenario benchmark."""
    from src.simulation.comparison_runner import run_controller_comparison

    result = run_controller_comparison(total_time=12.0)
    ranked = sorted(result["results"], key=lambda r: r.get("rank", 99))

    labels = [r["label"] for r in ranked]
    rmse = [r["metrics"]["rmse_tracking_error"] for r in ranked]
    colors_list = [C_CLASSICAL, C_CNN, C_RL]

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))
    fig.suptitle("Three-Controller Benchmark — Combined Scenario", fontsize=12, fontweight="bold")

    metrics = [
        ("rmse_tracking_error", "RMSE [m]"),
        ("chattering_index", "Chattering"),
        ("control_effort", "Control Effort"),
    ]
    bar_colors = colors_list

    for ax, (metric, ylabel) in zip(axes, metrics):
        vals = [r["metrics"][metric] for r in ranked]
        bars = ax.bar(labels, vals, color=bar_colors, alpha=0.85, edgecolor="#333")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.tick_params(axis="x", labelsize=7, rotation=15)
        ax.grid(axis="y", alpha=0.3)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:.2f}", ha="center", va="bottom", fontsize=7)

    fig.tight_layout()
    out = FIG_DIR / "fig07_controller_benchmark.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def fig_digital_twin_mockup():
    """Stylized digital twin UI mockup."""
    fig = plt.figure(figsize=(10, 5.5))
    fig.patch.set_facecolor("#0a0f1a")

    # Header
    ax_header = fig.add_axes([0, 0.88, 1, 0.12])
    ax_header.set_facecolor("#111827")
    ax_header.axis("off")
    ax_header.text(0.02, 0.5, "Robot Digital Twin", color="#00d4aa",
                   fontsize=14, fontweight="bold", va="center")
    ax_header.text(0.55, 0.5, "Environment → AI Agent → SMC Control → Robot",
                   color="#8899aa", fontsize=9, va="center")
    ax_header.text(0.95, 0.5, "● Live", color="#00d4aa", fontsize=10,
                   va="center", ha="right", fontweight="bold")

    # 3D view area
    ax_3d = fig.add_axes([0.02, 0.12, 0.55, 0.74])
    ax_3d.set_facecolor("#0a0f1a")
    # Corridor floor
    ax_3d.fill_between([0, 12], 0, 3, color="#1a2332", alpha=0.8)
    ax_3d.axhline(1.5, color="#2a4a68", linewidth=0.5, alpha=0.5)
    for i in range(0, 13, 2):
        ax_3d.axvline(i, color="#1e3048", linewidth=0.3, alpha=0.5)
    # Walls
    ax_3d.fill_between([0, 12], 2.8, 3.2, color="#2a3a4f")
    ax_3d.fill_between([0, 12], -0.2, 0.2, color="#2a3a4f")
    # Robot path
    t = np.linspace(0, 10, 100)
    x = t * 0.9
    y = 1.5 + 0.1 * np.sin(t * 0.8)
    ax_3d.plot(x, y, color=C_CNN, linewidth=2.5, label="Robot path")
    ax_3d.plot(x, np.full_like(x, 1.5), color=C_DESIRED, linestyle="--", linewidth=1, alpha=0.5)
    ax_3d.scatter(x[-1], y[-1], s=120, color=C_CNN, marker="s", zorder=5, label="Robot")
    ax_3d.set_xlim(-0.5, 11)
    ax_3d.set_ylim(-0.5, 3.5)
    ax_3d.set_title("3D Digital Twin — Hospital Corridor", color="white", fontsize=10, pad=6)
    ax_3d.tick_params(colors="#556677", labelsize=7)
    for spine in ax_3d.spines.values():
        spine.set_color("#2a4a68")
    ax_3d.legend(loc="upper left", fontsize=7, facecolor="#111827",
                 labelcolor="white", framealpha=0.8)

    # Metrics panel
    ax_met = fig.add_axes([0.60, 0.12, 0.38, 0.74])
    ax_met.set_facecolor("#111827")
    ax_met.axis("off")
    ax_met.text(0.05, 0.95, "Live Metrics", color="#00d4aa", fontsize=11,
                fontweight="bold", va="top")
    ax_met.text(0.05, 0.85, "Tracking Error", color="#8899aa", fontsize=8)
    ax_met.text(0.05, 0.78, "0.0421 m", color="#00d4aa", fontsize=18, fontweight="bold")
    ax_met.text(0.05, 0.65, "CNN Scenario: combined (94%)", color="#8899aa", fontsize=8)
    ax_met.text(0.05, 0.58, "Controller: CNN-Adaptive SMC", color="#8899aa", fontsize=8)

    # Mini error chart
    ax_chart = fig.add_axes([0.62, 0.25, 0.34, 0.25])
    ax_chart.set_facecolor("#0a0f1a")
    err_t = np.linspace(0, 15, 80)
    err = 0.05 + 0.15 * np.exp(-err_t / 3) + 0.02 * np.random.default_rng(1).normal(size=80)
    ax_chart.plot(err_t, err, color=C_CNN, linewidth=1.5)
    ax_chart.fill_between(err_t, err, alpha=0.2, color=C_CNN)
    ax_chart.set_xlabel("Time [s]", color="#8899aa", fontsize=7)
    ax_chart.set_ylabel("Error [m]", color="#8899aa", fontsize=7)
    ax_chart.tick_params(colors="#556677", labelsize=6)
    for spine in ax_chart.spines.values():
        spine.set_color("#2a4a68")

    out = FIG_DIR / "fig08_digital_twin.png"
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor="#0a0f1a")
    plt.close(fig)
    return out


def generate_all():
    print("Generating report figures...")
    figures = [
        ("Architecture diagram", fig_architecture),
        ("CNN samples", fig_cnn_samples),
        ("Trajectory comparison", fig_trajectory_comparison),
        ("Tracking error", fig_tracking_error),
        ("RMSE bar chart", fig_rmse_bars),
        ("Chattering bar chart", fig_chattering_bars),
        ("Controller benchmark", fig_controller_benchmark),
        ("Digital twin mockup", fig_digital_twin_mockup),
    ]
    paths = []
    for name, fn in figures:
        print(f"  → {name}...")
        paths.append(fn())
    print(f"\nSaved {len(paths)} figures to {FIG_DIR}")
    return paths


if __name__ == "__main__":
    generate_all()
