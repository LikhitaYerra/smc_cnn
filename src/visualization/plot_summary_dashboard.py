import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

SCENARIOS = ["normal", "noise", "disturbance", "slip", "combined"]


def plot_training_history(output_path: Path):
    history_path = Path("results/cnn/training_history.json")
    if not history_path.exists():
        return

    with open(history_path) as f:
        history = json.load(f)

    epochs = range(1, len(history["train_loss"]) + 1)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(epochs, history["train_loss"], label="Train loss", marker="o", markersize=3)
    axes[0].plot(epochs, history["val_loss"], label="Val loss", marker="o", markersize=3)
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].set_title("CNN Training Loss")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(epochs, history["train_accuracy"], label="Train accuracy", marker="o", markersize=3)
    axes[1].plot(epochs, history["val_accuracy"], label="Val accuracy", marker="o", markersize=3)
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_title("CNN Training Accuracy")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_improvement_heatmap(output_path: Path):
    improvement_path = Path("results/metrics/adaptive_improvement_summary.csv")
    if not improvement_path.exists():
        return

    df = pd.read_csv(improvement_path)

    metrics = [
        "rmse_tracking_error_improvement_percent",
        "final_tracking_error_improvement_percent",
        "control_effort_improvement_percent",
        "chattering_index_improvement_percent",
    ]

    labels = ["RMSE", "Final Error", "Control Effort", "Chattering"]
    data = df.set_index("scenario")[metrics].loc[SCENARIOS].to_numpy().T

    fig, ax = plt.subplots(figsize=(10, 4))
    norm = TwoSlopeNorm(vmin=-20, vcenter=0, vmax=40)
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn", norm=norm)

    ax.set_xticks(range(len(SCENARIOS)))
    ax.set_xticklabels(SCENARIOS)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("Adaptive SMC Improvement over Classical SMC (%)")

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = data[i, j]
            text_color = "white" if abs(value) > 18 else "black"
            ax.text(j, i, f"{value:.1f}", ha="center", va="center", color=text_color, fontsize=9)

    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.set_label("Improvement (%)")

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_trajectory_grid(output_path: Path):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for index, scenario in enumerate(SCENARIOS):
        ax = axes[index]
        classical_path = Path(f"results/logs/classical_smc_issues/log_{scenario}.csv")
        adaptive_path = Path(f"results/logs/adaptive_smc/log_{scenario}.csv")

        classical_df = pd.read_csv(classical_path)
        adaptive_df = pd.read_csv(adaptive_path)

        ax.plot(
            classical_df["desired_x"],
            classical_df["desired_y"],
            linestyle="--",
            color="gray",
            linewidth=1.5,
            label="Desired",
        )
        ax.plot(
            classical_df["actual_x"],
            classical_df["actual_y"],
            label="Classical SMC",
            linewidth=1.5,
        )
        ax.plot(
            adaptive_df["actual_x"],
            adaptive_df["actual_y"],
            label="CNN-adaptive SMC",
            linewidth=1.5,
        )
        ax.set_title(scenario.capitalize())
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.axis("equal")
        ax.grid(True, alpha=0.3)

        if index == 0:
            ax.legend(fontsize=8)

    axes[-1].axis("off")
    axes[-1].text(
        0.5,
        0.5,
        "CNN-Adaptive SMC\nvs Classical SMC\nTrajectory Overview",
        ha="center",
        va="center",
        fontsize=14,
        transform=axes[-1].transAxes,
    )

    fig.suptitle("Robot Trajectories Across All Scenarios", fontsize=14, y=0.98)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_tracking_error_grid(output_path: Path):
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()

    for index, scenario in enumerate(SCENARIOS):
        ax = axes[index]
        classical_path = Path(f"results/logs/classical_smc_issues/log_{scenario}.csv")
        adaptive_path = Path(f"results/logs/adaptive_smc/log_{scenario}.csv")

        classical_df = pd.read_csv(classical_path)
        adaptive_df = pd.read_csv(adaptive_path)

        ax.plot(
            classical_df["time"],
            classical_df["tracking_error"],
            label="Classical SMC",
            linewidth=1.5,
        )
        ax.plot(
            adaptive_df["time"],
            adaptive_df["tracking_error"],
            label="CNN-adaptive SMC",
            linewidth=1.5,
        )
        ax.set_title(scenario.capitalize())
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Tracking error [m]")
        ax.grid(True, alpha=0.3)

        if index == 0:
            ax.legend(fontsize=8)

    axes[-1].axis("off")

    fig.suptitle("Tracking Error Over Time", fontsize=14, y=0.98)
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_chattering_comparison(output_path: Path):
    metrics_path = Path("results/metrics/classical_vs_adaptive_metrics.csv")
    if not metrics_path.exists():
        return

    df = pd.read_csv(metrics_path)

    classical_values = []
    adaptive_values = []

    for scenario in SCENARIOS:
        scenario_df = df[df["scenario"] == scenario]
        classical_values.append(
            scenario_df[scenario_df["controller"] == "classical_smc"]["chattering_index"].iloc[0]
        )
        adaptive_values.append(
            scenario_df[scenario_df["controller"] == "cnn_adaptive_smc"]["chattering_index"].iloc[0]
        )

    x = np.arange(len(SCENARIOS))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(x - width / 2, classical_values, width, label="Classical SMC", color="#e74c3c")
    ax.bar(x + width / 2, adaptive_values, width, label="CNN-adaptive SMC", color="#2ecc71")

    ax.set_xticks(x)
    ax.set_xticklabels(SCENARIOS)
    ax.set_ylabel("Chattering index")
    ax.set_title("Chattering Reduction: Classical vs CNN-Adaptive SMC")
    ax.grid(axis="y", alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    output_dir = Path("results/plots/summary")
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_training_history(output_dir / "cnn_training_history.png")
    plot_improvement_heatmap(output_dir / "improvement_heatmap.png")
    plot_trajectory_grid(output_dir / "trajectory_grid.png")
    plot_tracking_error_grid(output_dir / "tracking_error_grid.png")
    plot_chattering_comparison(output_dir / "chattering_comparison.png")

    print(f"Summary dashboard plots saved to: {output_dir}")


if __name__ == "__main__":
    main()
