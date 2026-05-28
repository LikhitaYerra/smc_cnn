import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.data_generation.environment_generator import EnvironmentMapGenerator

SCENARIOS = ["normal", "noise", "disturbance", "slip", "combined"]

SCENARIO_CONFIG = {
    "normal": {"noise": False, "disturbance": False, "slip": False},
    "noise": {"noise": True, "disturbance": False, "slip": False},
    "disturbance": {"noise": False, "disturbance": True, "slip": False},
    "slip": {"noise": False, "disturbance": False, "slip": True},
    "combined": {"noise": True, "disturbance": True, "slip": True},
}

KEY_TIMES = [0.0, 8.0, 12.0, 20.0]


def load_logs(scenario: str):
    classical_path = Path(f"results/logs/classical_smc_issues/log_{scenario}.csv")
    adaptive_path = Path(f"results/logs/adaptive_smc/log_{scenario}.csv")

    classical_df = pd.read_csv(classical_path)
    adaptive_df = pd.read_csv(adaptive_path)

    return classical_df, adaptive_df


def nearest_row(df: pd.DataFrame, target_time: float) -> pd.Series:
    index = (df["time"] - target_time).abs().idxmin()
    return df.loc[index]


def draw_robot_arrow(ax, x, y, theta, color, label=None):
    dx = 0.25 * np.cos(theta)
    dy = 0.25 * np.sin(theta)

    arrow = FancyArrowPatch(
        (x, y),
        (x + dx, y + dy),
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=2.0,
        color=color,
    )
    ax.add_patch(arrow)

    if label:
        ax.scatter(x, y, s=30, color=color, label=label, zorder=5)


def draw_sim_zones(ax, config: dict):
    if config["disturbance"]:
        ax.axvline(x=2.4, color="#e74c3c", linestyle=":", linewidth=1.5, alpha=0.8)
        ax.text(2.45, ax.get_ylim()[1] * 0.85, "Disturbance\nt=8s", fontsize=8, color="#c0392b")

    if config["slip"]:
        slip_rect = Rectangle(
            (3.0, ax.get_ylim()[0]),
            1.2,
            ax.get_ylim()[1] - ax.get_ylim()[0],
            facecolor="#f39c12",
            alpha=0.12,
            edgecolor="#e67e22",
            linestyle="--",
            linewidth=1.2,
        )
        ax.add_patch(slip_rect)
        ax.text(3.6, ax.get_ylim()[1] * 0.7, "Slip zone\nt=10–14s", fontsize=8, color="#d35400", ha="center")


def capture_environment_overview(output_dir: Path):
    generator = EnvironmentMapGenerator(map_size=64, seed=42)

    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    axes = axes.flatten()

    for index, scenario in enumerate(SCENARIOS):
        ax = axes[index]
        env_map = generator.generate(scenario)
        config = SCENARIO_CONFIG[scenario]

        ax.imshow(env_map, cmap="gray", vmin=0.0, vmax=1.0)
        ax.set_title(scenario.capitalize(), fontsize=12, fontweight="bold")

        flags = []
        if config["noise"]:
            flags.append("Sensor noise")
        if config["disturbance"]:
            flags.append("Push at t=8s")
        if config["slip"]:
            flags.append("Wheel slip t=10–14s")
        if not flags:
            flags.append("No uncertainty")

        ax.text(
            0.02,
            0.98,
            "\n".join(flags),
            transform=ax.transAxes,
            va="top",
            ha="left",
            fontsize=8,
            color="white",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.55),
        )
        ax.axis("off")

    axes[-1].axis("off")
    axes[-1].text(
        0.5,
        0.55,
        "Simulation Environments\n\n"
        "Top: CNN input maps\n"
        "Bottom row: keyframe views\n\n"
        "Straight path, 20 s, 0.3 m/s",
        ha="center",
        va="center",
        fontsize=11,
        transform=axes[-1].transAxes,
    )

    fig.suptitle("Simulation Environment Overview — 5 Scenarios", fontsize=15, y=0.98)
    fig.tight_layout()
    fig.savefig(output_dir / "simulation_environment_overview.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def capture_scenario_snapshot(scenario: str, output_dir: Path):
    classical_df, adaptive_df = load_logs(scenario)
    config = SCENARIO_CONFIG[scenario]
    generator = EnvironmentMapGenerator(map_size=64, seed=42)
    env_map = generator.generate(scenario)

    fig = plt.figure(figsize=(14, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.3], hspace=0.28, wspace=0.2)

    ax_map = fig.add_subplot(gs[0, 0])
    ax_map.imshow(env_map, cmap="gray", vmin=0.0, vmax=1.0)
    ax_map.set_title("CNN Environment Map", fontsize=11)
    ax_map.axis("off")

    ax_info = fig.add_subplot(gs[0, 1])
    ax_info.axis("off")

    info_lines = [
        f"Scenario: {scenario.upper()}",
        "",
        "Simulation setup:",
        "• Differential-drive robot",
        "• Reference: straight line, 0.3 m/s",
        "• Duration: 20 seconds, dt = 0.01 s",
        "• Start pose: (0, 0.5, θ=0)",
        "",
        "Active effects:",
    ]

    if config["noise"]:
        info_lines.append("• Sensor noise on x, y, θ")
    if config["disturbance"]:
        info_lines.append("• External push: dy = +0.4 m at t = 8 s")
    if config["slip"]:
        info_lines.append("• Wheel slip: 70% velocity, t = 10–14 s")
    if not any(config.values()):
        info_lines.append("• None (ideal conditions)")

    info_lines.extend(
        [
            "",
            "Controllers compared:",
            "• Classical SMC (blue)",
            "• CNN-adaptive SMC (orange)",
        ]
    )

    ax_info.text(
        0.05,
        0.95,
        "\n".join(info_lines),
        va="top",
        ha="left",
        fontsize=10,
        family="monospace",
        transform=ax_info.transAxes,
    )
    ax_info.set_title("Environment Settings", fontsize=11)

    ax_path = fig.add_subplot(gs[1, :])

    ax_path.plot(
        classical_df["desired_x"],
        classical_df["desired_y"],
        "k--",
        linewidth=1.5,
        label="Desired path",
    )
    ax_path.plot(
        classical_df["actual_x"],
        classical_df["actual_y"],
        color="#2980b9",
        linewidth=1.8,
        label="Classical SMC",
    )
    ax_path.plot(
        adaptive_df["actual_x"],
        adaptive_df["actual_y"],
        color="#e67e22",
        linewidth=1.8,
        label="CNN-adaptive SMC",
    )

    ax_path.scatter(classical_df.iloc[0]["actual_x"], classical_df.iloc[0]["actual_y"], c="green", s=50, zorder=5)
    ax_path.scatter(classical_df.iloc[-1]["actual_x"], classical_df.iloc[-1]["actual_y"], c="red", s=50, zorder=5)

    draw_sim_zones(ax_path, config)

    ax_path.set_xlabel("x [m]")
    ax_path.set_ylabel("y [m]")
    ax_path.set_title("Top-Down Simulation View", fontsize=11)
    ax_path.axis("equal")
    ax_path.grid(True, alpha=0.3)
    ax_path.legend(loc="upper right", fontsize=9)

    green_patch = mpatches.Patch(color="green", label="Start")
    red_patch = mpatches.Patch(color="red", label="End")
    ax_path.legend(handles=ax_path.get_legend_handles_labels()[0][:3] + [green_patch, red_patch], fontsize=8)

    fig.suptitle(f"Simulation Environment — {scenario.capitalize()}", fontsize=14, y=0.98)
    fig.savefig(output_dir / f"{scenario}_environment.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def capture_keyframe_snapshot(scenario: str, output_dir: Path):
    classical_df, adaptive_df = load_logs(scenario)
    config = SCENARIO_CONFIG[scenario]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()

    for ax, target_time in zip(axes, KEY_TIMES):
        c_row = nearest_row(classical_df, target_time)
        a_row = nearest_row(adaptive_df, target_time)

        ax.plot(
            classical_df["desired_x"],
            classical_df["desired_y"],
            "k--",
            linewidth=1.2,
            alpha=0.6,
        )

        c_index = c_row.name
        a_index = a_row.name

        ax.plot(
            classical_df.loc[:c_index, "actual_x"],
            classical_df.loc[:c_index, "actual_y"],
            color="#2980b9",
            linewidth=1.5,
            label="Classical trail",
        )
        ax.plot(
            adaptive_df.loc[:a_index, "actual_x"],
            adaptive_df.loc[:a_index, "actual_y"],
            color="#e67e22",
            linewidth=1.5,
            label="Adaptive trail",
        )

        draw_robot_arrow(
            ax,
            c_row["actual_x"],
            c_row["actual_y"],
            c_row["actual_theta"],
            "#2980b9",
            label="Classical",
        )
        draw_robot_arrow(
            ax,
            a_row["actual_x"],
            a_row["actual_y"],
            a_row["actual_theta"],
            "#e67e22",
            label="Adaptive",
        )

        draw_sim_zones(ax, config)

        ax.set_title(f"t = {target_time:.0f} s", fontsize=11)
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.axis("equal")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7, loc="upper left")

    fig.suptitle(f"Simulation Keyframes — {scenario.capitalize()}", fontsize=14)
    fig.tight_layout()
    fig.savefig(output_dir / f"{scenario}_keyframes.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def capture_all_snapshots():
    output_dir = Path("results/snapshots/simulation")
    output_dir.mkdir(parents=True, exist_ok=True)

    logs_dir = Path("results/logs/classical_smc_issues")
    if not logs_dir.exists():
        raise FileNotFoundError(
            "Simulation logs not found. Run: python3 src/simulation/simulate_classical_smc_with_issues.py"
        )

    capture_environment_overview(output_dir)

    for scenario in SCENARIOS:
        capture_scenario_snapshot(scenario, output_dir)
        capture_keyframe_snapshot(scenario, output_dir)
        print(f"Saved snapshots for scenario: {scenario}")

    print(f"\nAll simulation snapshots saved to: {output_dir}")


if __name__ == "__main__":
    capture_all_snapshots()
