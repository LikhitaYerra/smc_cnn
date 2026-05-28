import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def round_numeric_columns(df: pd.DataFrame, decimals: int = 4) -> pd.DataFrame:
    df = df.copy()

    numeric_columns = df.select_dtypes(include=["float", "int"]).columns

    for column in numeric_columns:
        df[column] = df[column].round(decimals)

    return df


def main():
    metrics_path = Path("results/metrics/classical_vs_adaptive_metrics.csv")
    improvement_path = Path("results/metrics/adaptive_improvement_summary.csv")

    output_dir = Path("results/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    if not metrics_path.exists():
        raise FileNotFoundError(
            "Missing metrics file. Run: python src/evaluation/compare_classical_vs_adaptive.py"
        )

    if not improvement_path.exists():
        raise FileNotFoundError(
            "Missing improvement file. Run: python src/evaluation/compute_adaptive_improvement.py"
        )

    metrics_df = pd.read_csv(metrics_path)
    improvement_df = pd.read_csv(improvement_path)

    selected_metrics = metrics_df[
        [
            "controller",
            "scenario",
            "mean_tracking_error",
            "rmse_tracking_error",
            "final_tracking_error",
            "control_effort",
            "chattering_index",
            "settling_time",
        ]
    ]

    selected_improvements = improvement_df[
        [
            "scenario",
            "rmse_tracking_error_improvement_percent",
            "final_tracking_error_improvement_percent",
            "control_effort_improvement_percent",
            "chattering_index_improvement_percent",
        ]
    ]

    selected_metrics = round_numeric_columns(selected_metrics, decimals=4)
    selected_improvements = round_numeric_columns(selected_improvements, decimals=2)

    metrics_table_path = output_dir / "report_controller_metrics_table.csv"
    improvement_table_path = output_dir / "report_improvement_table.csv"

    selected_metrics.to_csv(metrics_table_path, index=False)
    selected_improvements.to_csv(improvement_table_path, index=False)

    print("\nReport controller metrics table:")
    print(selected_metrics.to_string(index=False))

    print("\nReport improvement table:")
    print(selected_improvements.to_string(index=False))

    print()
    print(f"Saved: {metrics_table_path}")
    print(f"Saved: {improvement_table_path}")


if __name__ == "__main__":
    main()