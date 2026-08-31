"""Bar charts comparing all adaptive controller variants."""

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

SCENARIOS = ["normal", "noise", "disturbance", "slip", "combined"]
CONTROLLERS = [
    ("classical_smc", "Classical"),
    ("fuzzy_smc", "Fuzzy"),
    ("cnn_adaptive_smc", "CNN"),
    ("oracle_adaptive_smc", "Oracle"),
    ("rl_adaptive_smc", "RL"),
]
COLORS = ["#3498db", "#9b59b6", "#2ecc71", "#e67e22", "#e74c3c"]


def plot_metric(df: pd.DataFrame, metric: str, ylabel: str, title: str, save_path: Path):
    x = np.arange(len(SCENARIOS))
    width = 0.15
    offsets = np.linspace(-(len(CONTROLLERS) - 1) / 2, (len(CONTROLLERS) - 1) / 2, len(CONTROLLERS))

    fig, ax = plt.subplots(figsize=(12, 5))
    for (key, label), color, offset in zip(CONTROLLERS, COLORS, offsets):
        values = []
        for scenario in SCENARIOS:
            row = df[(df["controller"] == key) & (df["scenario"] == scenario)]
            values.append(row[metric].iloc[0] if not row.empty else 0.0)
        ax.bar(x + offset * width, values, width=width, label=label, color=color)

    ax.set_xticks(x)
    ax.set_xticklabels(SCENARIOS)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.3)
    ax.legend(ncol=5, fontsize=9)
    fig.tight_layout()
    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_cnn_improvement_heatmap(df: pd.DataFrame, save_path: Path):
    classical = df[df["controller"] == "classical_smc"].set_index("scenario")
    cnn = df[df["controller"] == "cnn_adaptive_smc"].set_index("scenario")

    metrics = ["rmse_tracking_error", "final_tracking_error", "control_effort", "chattering_index"]
    labels = ["RMSE", "Final Error", "Control Effort", "Chattering"]
    data = []
    for metric in metrics:
        row = []
        for scenario in SCENARIOS:
            base = classical.loc[scenario, metric]
            val = cnn.loc[scenario, metric]
            if metric in ("rmse_tracking_error", "final_tracking_error", "chattering_index"):
                imp = (base - val) / base * 100 if base else 0.0
            else:
                imp = (val - base) / base * 100 if base else 0.0
            row.append(imp)
        data.append(row)

    data = np.array(data)
    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(data, aspect="auto", cmap="RdYlGn", vmin=-25, vmax=40)
    ax.set_xticks(range(len(SCENARIOS)))
    ax.set_xticklabels(SCENARIOS)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("CNN-Adaptive Improvement over Classical SMC (%)")
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            ax.text(j, i, f"{data[i, j]:.1f}", ha="center", va="center", fontsize=9)
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.tight_layout()
    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    metrics_path = Path("results/metrics/all_controllers_metrics.csv")
    if not metrics_path.exists():
        raise FileNotFoundError("Run compare_all_controllers.py first.")

    df = pd.read_csv(metrics_path)
    output_dir = Path("results/plots/multi_controller")
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_metric(df, "chattering_index", "Chattering index", "Multi-Controller Chattering Comparison", output_dir / "chattering_all_controllers.png")
    plot_metric(df, "final_tracking_error", "Final tracking error [m]", "Multi-Controller Final Error Comparison", output_dir / "final_error_all_controllers.png")
    plot_metric(df, "rmse_tracking_error", "RMSE tracking error [m]", "Multi-Controller RMSE Comparison", output_dir / "rmse_all_controllers.png")
    plot_cnn_improvement_heatmap(df, output_dir / "cnn_improvement_heatmap.png")

    print(f"Saved multi-controller plots to: {output_dir}")


if __name__ == "__main__":
    main()
