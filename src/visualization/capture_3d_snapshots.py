import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import art3d

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

SCENARIOS = ["normal", "noise", "disturbance", "slip", "combined"]
KEY_TIMES = [0.0, 8.0, 12.0, 20.0]


def load_logs(scenario: str):
    classical_path = Path(f"results/logs/classical_smc_issues/log_{scenario}.csv")
    adaptive_path = Path(f"results/logs/adaptive_smc/log_{scenario}.csv")
    return pd.read_csv(classical_path), pd.read_csv(adaptive_path)


def nearest_row(df: pd.DataFrame, target_time: float) -> pd.Series:
    index = (df["time"] - target_time).abs().idxmin()
    return df.loc[index]


def draw_3d_path(ax, x, y, z, color, label=None, linewidth=2.0, linestyle="-"):
    ax.plot(x, y, z, color=color, linewidth=linewidth, linestyle=linestyle, label=label)


def draw_robot_box(ax, x, y, z, theta, color, alpha=0.85):
    length, width, height = 0.36, 0.24, 0.16

    corners = np.array(
        [
            [-length / 2, -width / 2, 0.0],
            [length / 2, -width / 2, 0.0],
            [length / 2, width / 2, 0.0],
            [-length / 2, width / 2, 0.0],
        ]
    )

    rotation = np.array(
        [
            [np.cos(theta), -np.sin(theta), 0.0],
            [np.sin(theta), np.cos(theta), 0.0],
            [0.0, 0.0, 1.0],
        ]
    )

    rotated = corners @ rotation.T
    rotated[:, 0] += x
    rotated[:, 1] += y
    rotated[:, 2] += z

    faces = [
        [0, 1, 2, 3],
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
        [3, 0, 4, 7],
        [4, 5, 6, 7],
    ]

    top = rotated.copy()
    top[:, 2] += height

    vertices = np.vstack([rotated, top])

    for face in faces:
        square = art3d.Poly3DCollection([vertices[face]], alpha=alpha)
        square.set_facecolor(color)
        square.set_edgecolor("black")
        square.set_linewidth(0.4)
        ax.add_collection3d(square)


def setup_axes(ax, title: str):
    ax.set_xlim(-0.5, 6.5)
    ax.set_ylim(-2.0, 2.0)
    ax.set_zlim(0.0, 0.8)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_zlabel("z [m]")
    ax.set_title(title, fontsize=11, pad=10)
    ax.view_init(elev=28, azim=-55)
    ax.set_box_aspect((6.5, 2.5, 0.8))


def capture_3d_environment_snapshot(scenario: str, output_dir: Path):
    classical_df, adaptive_df = load_logs(scenario)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    xx, yy = np.meshgrid(np.linspace(-0.5, 6.5, 8), np.linspace(-2.0, 2.0, 6))
    zz = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, color="#d5d8dc", alpha=0.35, linewidth=0, shade=True)

    draw_3d_path(
        ax,
        classical_df["desired_x"],
        classical_df["desired_y"],
        np.full(len(classical_df), 0.02),
        color="black",
        label="Desired path",
        linewidth=1.5,
        linestyle="--",
    )
    draw_3d_path(
        ax,
        classical_df["actual_x"],
        classical_df["actual_y"],
        np.full(len(classical_df), 0.15),
        color="#2980b9",
        label="Classical SMC",
    )
    draw_3d_path(
        ax,
        adaptive_df["actual_x"],
        adaptive_df["actual_y"],
        np.full(len(adaptive_df), 0.35),
        color="#e67e22",
        label="CNN-adaptive SMC",
    )

    start_x = float(classical_df.iloc[0]["desired_x"])
    start_y = float(classical_df.iloc[0]["desired_y"])
    end_x = float(classical_df.iloc[-1]["desired_x"])
    end_y = float(classical_df.iloc[-1]["desired_y"])

    ax.scatter([start_x], [start_y], [0.12], s=60, c="green", label="Start")
    ax.scatter([end_x], [end_y], [0.12], s=60, c="red", label="End")

    c_row = classical_df.iloc[-1]
    a_row = adaptive_df.iloc[-1]
    draw_robot_box(ax, c_row["actual_x"], c_row["actual_y"], 0.15, c_row["actual_theta"], "#2980b9")
    draw_robot_box(ax, a_row["actual_x"], a_row["actual_y"], 0.35, a_row["actual_theta"], "#e67e22")

    setup_axes(ax, f"3D Simulation View — {scenario.capitalize()}")
    ax.legend(loc="upper left", fontsize=8)

    fig.text(
        0.5,
        0.02,
        "3D replay of saved simulation logs (same view as PyBullet replay). "
        "Blue robot = classical SMC, orange robot = CNN-adaptive SMC.",
        ha="center",
        fontsize=9,
        color="#444444",
    )

    fig.tight_layout()
    fig.savefig(output_dir / f"{scenario}_3d_environment.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def capture_3d_keyframes(scenario: str, output_dir: Path):
    classical_df, adaptive_df = load_logs(scenario)

    fig = plt.figure(figsize=(12, 10))

    for index, target_time in enumerate(KEY_TIMES, start=1):
        ax = fig.add_subplot(2, 2, index, projection="3d")

        xx, yy = np.meshgrid(np.linspace(-0.5, 6.5, 6), np.linspace(-2.0, 2.0, 4))
        zz = np.zeros_like(xx)
        ax.plot_surface(xx, yy, zz, color="#d5d8dc", alpha=0.25, linewidth=0)

        c_row = nearest_row(classical_df, target_time)
        a_row = nearest_row(adaptive_df, target_time)

        c_index = c_row.name
        a_index = a_row.name

        draw_3d_path(
            ax,
            classical_df.loc[:c_index, "desired_x"],
            classical_df.loc[:c_index, "desired_y"],
            np.full(c_index + 1, 0.02),
            color="black",
            linewidth=1.2,
            linestyle="--",
        )
        draw_3d_path(
            ax,
            classical_df.loc[:c_index, "actual_x"],
            classical_df.loc[:c_index, "actual_y"],
            np.full(c_index + 1, 0.15),
            color="#2980b9",
        )
        draw_3d_path(
            ax,
            adaptive_df.loc[:a_index, "actual_x"],
            adaptive_df.loc[:a_index, "actual_y"],
            np.full(a_index + 1, 0.35),
            color="#e67e22",
        )

        draw_robot_box(ax, c_row["actual_x"], c_row["actual_y"], 0.15, c_row["actual_theta"], "#2980b9")
        draw_robot_box(ax, a_row["actual_x"], a_row["actual_y"], 0.35, a_row["actual_theta"], "#e67e22")

        setup_axes(ax, f"t = {target_time:.0f} s")

    fig.suptitle(f"3D Keyframes — {scenario.capitalize()}", fontsize=14)
    fig.tight_layout()
    fig.savefig(output_dir / f"{scenario}_3d_keyframes.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def capture_all_3d_snapshots():
    output_dir = Path("results/snapshots/3d_simulation")
    output_dir.mkdir(parents=True, exist_ok=True)

    logs_dir = Path("results/logs/classical_smc_issues")
    if not logs_dir.exists():
        raise FileNotFoundError(
            "Simulation logs not found. Run the simulation scripts first."
        )

    for scenario in SCENARIOS:
        capture_3d_environment_snapshot(scenario, output_dir)
        if scenario in {"disturbance", "combined"}:
            capture_3d_keyframes(scenario, output_dir)
        print(f"Saved 3D snapshots for scenario: {scenario}")

    print(f"\nAll 3D snapshots saved to: {output_dir}")


if __name__ == "__main__":
    capture_all_3d_snapshots()
