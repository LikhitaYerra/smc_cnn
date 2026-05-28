import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.evaluation.metrics import compute_all_metrics


def main():
    logs_dir = Path("results/logs/classical_smc")
    output_dir = Path("results/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)

    log_files = sorted(logs_dir.glob("log_*_phi_0_5_smooth_0_95.csv"))

    if not log_files:
        raise FileNotFoundError(
            "No log files found. Run: python src/simulation/compare_switching_functions.py"
        )

    rows = []

    for log_file in log_files:
        df = pd.read_csv(log_file)

        metrics = compute_all_metrics(df)

        switching_type = df["switching_type"].iloc[0]
        phi = df["phi"].iloc[0]
        omega_smoothing = df["omega_smoothing"].iloc[0]

        row = {
            "switching_type": switching_type,
            "phi": phi,
            "omega_smoothing": omega_smoothing,
            **metrics,
        }

        rows.append(row)

    results_df = pd.DataFrame(rows)

    results_df = results_df.sort_values(
        by=["rmse_tracking_error", "chattering_index"],
        ascending=[True, True],
    )

    save_path = output_dir / "switching_function_metrics.csv"
    results_df.to_csv(save_path, index=False)

    print("\nSwitching function metrics:")
    print(results_df.to_string(index=False))
    print(f"\nSaved metrics to: {save_path}")


if __name__ == "__main__":
    main()