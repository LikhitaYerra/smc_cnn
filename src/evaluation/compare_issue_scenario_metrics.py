import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.evaluation.metrics import compute_all_metrics


def normalize_issue_log_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "v" not in df.columns and "v_commanded" in df.columns:
        df["v"] = df["v_commanded"]

    if "omega" not in df.columns and "omega_commanded" in df.columns:
        df["omega"] = df["omega_commanded"]

    return df


def main():
    logs_dir = Path("results/logs/classical_smc_issues")
    output_dir = Path("results/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)

    log_files = sorted(logs_dir.glob("log_*.csv"))

    if not log_files:
        raise FileNotFoundError(
            "No issue scenario logs found. Run: "
            "python src/simulation/simulate_classical_smc_with_issues.py"
        )

    rows = []

    for log_file in log_files:
        df = pd.read_csv(log_file)
        df = normalize_issue_log_columns(df)

        metrics = compute_all_metrics(df)

        if "scenario" in df.columns:
            scenario = df["scenario"].iloc[0]
        else:
            scenario = log_file.stem.replace("log_", "")

        row = {
            "scenario": scenario,
            **metrics,
        }

        rows.append(row)

    results_df = pd.DataFrame(rows)

    scenario_order = {
        "normal": 0,
        "noise": 1,
        "disturbance": 2,
        "slip": 3,
        "combined": 4,
    }

    results_df["scenario_order"] = results_df["scenario"].map(scenario_order)
    results_df = results_df.sort_values("scenario_order").drop(columns=["scenario_order"])

    save_path = output_dir / "classical_smc_issue_scenario_metrics.csv"
    results_df.to_csv(save_path, index=False)

    print("\nClassical SMC issue scenario metrics:")
    print(results_df.to_string(index=False))
    print(f"\nSaved metrics to: {save_path}")


if __name__ == "__main__":
    main()