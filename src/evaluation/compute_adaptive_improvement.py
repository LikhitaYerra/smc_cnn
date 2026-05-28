import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def percentage_change(classical_value, adaptive_value):
    if classical_value == 0:
        return None

    return 100.0 * (classical_value - adaptive_value) / classical_value


def main():
    input_path = Path("results/metrics/classical_vs_adaptive_metrics.csv")
    output_dir = Path("results/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(
            "Missing comparison file. Run: "
            "python src/evaluation/compare_classical_vs_adaptive.py"
        )

    df = pd.read_csv(input_path)

    metrics_to_compare = [
        "mean_tracking_error",
        "rmse_tracking_error",
        "final_tracking_error",
        "control_effort",
        "chattering_index",
    ]

    scenarios = [
        "normal",
        "noise",
        "disturbance",
        "slip",
        "combined",
    ]

    rows = []

    for scenario in scenarios:
        scenario_df = df[df["scenario"] == scenario]

        classical = scenario_df[scenario_df["controller"] == "classical_smc"].iloc[0]
        adaptive = scenario_df[scenario_df["controller"] == "cnn_adaptive_smc"].iloc[0]

        row = {
            "scenario": scenario,
        }

        for metric in metrics_to_compare:
            classical_value = classical[metric]
            adaptive_value = adaptive[metric]

            row[f"classical_{metric}"] = classical_value
            row[f"adaptive_{metric}"] = adaptive_value
            row[f"{metric}_improvement_percent"] = percentage_change(
                classical_value,
                adaptive_value,
            )

        rows.append(row)

    improvement_df = pd.DataFrame(rows)

    save_path = output_dir / "adaptive_improvement_summary.csv"
    improvement_df.to_csv(save_path, index=False)

    print("\nAdaptive SMC improvement summary:")
    print(improvement_df.to_string(index=False))
    print(f"\nSaved improvement summary to: {save_path}")


if __name__ == "__main__":
    main()