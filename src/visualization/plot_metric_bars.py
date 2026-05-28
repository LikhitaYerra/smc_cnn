import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def plot_grouped_bar(df, metric: str, ylabel: str, title: str, save_path: Path):
    scenarios = ["normal", "noise", "disturbance", "slip", "combined"]

    classical_values = []
    adaptive_values = []

    for scenario in scenarios:
        scenario_df = df[df["scenario"] == scenario]

        classical_value = scenario_df[
            scenario_df["controller"] == "classical_smc"
        ][metric].iloc[0]

        adaptive_value = scenario_df[
            scenario_df["controller"] == "cnn_adaptive_smc"
        ][metric].iloc[0]

        classical_values.append(classical_value)
        adaptive_values.append(adaptive_value)

    x = range(len(scenarios))
    width = 0.35

    plt.figure(figsize=(10, 5))
    plt.bar([i - width / 2 for i in x], classical_values, width=width, label="Classical SMC")
    plt.bar([i + width / 2 for i in x], adaptive_values, width=width, label="CNN-adaptive SMC")

    plt.xticks(list(x), scenarios)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis="y")
    plt.legend()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    metrics_path = Path("results/metrics/classical_vs_adaptive_metrics.csv")
    output_dir = Path("results/plots/comparison/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not metrics_path.exists():
        raise FileNotFoundError(
            "Missing metrics file. Run: python src/evaluation/compare_classical_vs_adaptive.py"
        )

    df = pd.read_csv(metrics_path)

    plot_grouped_bar(
        df=df,
        metric="rmse_tracking_error",
        ylabel="RMSE tracking error [m]",
        title="RMSE Tracking Error Comparison",
        save_path=output_dir / "rmse_tracking_error_comparison.png",
    )

    plot_grouped_bar(
        df=df,
        metric="mean_tracking_error",
        ylabel="Mean tracking error [m]",
        title="Mean Tracking Error Comparison",
        save_path=output_dir / "mean_tracking_error_comparison.png",
    )

    plot_grouped_bar(
        df=df,
        metric="final_tracking_error",
        ylabel="Final tracking error [m]",
        title="Final Tracking Error Comparison",
        save_path=output_dir / "final_tracking_error_comparison.png",
    )

    plot_grouped_bar(
        df=df,
        metric="control_effort",
        ylabel="Control effort",
        title="Control Effort Comparison",
        save_path=output_dir / "control_effort_comparison.png",
    )

    plot_grouped_bar(
        df=df,
        metric="chattering_index",
        ylabel="Chattering index",
        title="Chattering Index Comparison",
        save_path=output_dir / "chattering_index_comparison.png",
    )

    print(f"Saved metric bar charts to: {output_dir}")


if __name__ == "__main__":
    main()