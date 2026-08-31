import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.evaluation.metrics import compute_all_metrics


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "v" not in df.columns and "v_commanded" in df.columns:
        df["v"] = df["v_commanded"]

    if "omega" not in df.columns and "omega_commanded" in df.columns:
        df["omega"] = df["omega_commanded"]

    return df


def load_and_compute_metrics(log_path: Path, controller_name: str, scenario: str) -> dict:
    df = pd.read_csv(log_path)
    df = normalize_columns(df)

    metrics = compute_all_metrics(df)

    return {
        "controller": controller_name,
        "scenario": scenario,
        **metrics,
    }


def main():
    classical_dir = Path("results/logs/classical_smc_issues")
    adaptive_dir = Path("results/logs/adaptive_smc")
    output_dir = Path("results/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)

    scenarios = [
        "normal",
        "noise",
        "disturbance",
        "slip",
        "combined",
    ]

    rows = []

    for scenario in scenarios:
        classical_log = classical_dir / f"log_{scenario}.csv"
        adaptive_log = adaptive_dir / f"log_{scenario}.csv"

        if not classical_log.exists():
            raise FileNotFoundError(f"Missing classical log: {classical_log}")

        if not adaptive_log.exists():
            raise FileNotFoundError(f"Missing adaptive log: {adaptive_log}")

        rows.append(
            load_and_compute_metrics(
                log_path=classical_log,
                controller_name="classical_smc",
                scenario=scenario,
            )
        )

        rows.append(
            load_and_compute_metrics(
                log_path=adaptive_log,
                controller_name="cnn_adaptive_smc",
                scenario=scenario,
            )
        )

    results_df = pd.DataFrame(rows)

    scenario_order = {
        "normal": 0,
        "noise": 1,
        "disturbance": 2,
        "slip": 3,
        "combined": 4,
    }

    controller_order = {
        "classical_smc": 0,
        "cnn_adaptive_smc": 1,
    }

    results_df["scenario_order"] = results_df["scenario"].map(scenario_order)
    results_df["controller_order"] = results_df["controller"].map(controller_order)

    results_df = results_df.sort_values(
        by=["scenario_order", "controller_order"]
    ).drop(columns=["scenario_order", "controller_order"])

    save_path = output_dir / "classical_vs_adaptive_metrics.csv"
    results_df.to_csv(save_path, index=False)

    print("\nClassical SMC vs CNN-Adaptive SMC metrics:")
    print(results_df.to_string(index=False))
    print(f"\nSaved comparison to: {save_path}")

    pivot_df = results_df.pivot(
        index="scenario",
        columns="controller",
        values=[
            "rmse_tracking_error",
            "mean_tracking_error",
            "final_tracking_error",
            "control_effort",
            "chattering_index",
        ],
    )

    pivot_path = output_dir / "classical_vs_adaptive_metrics_pivot.csv"
    pivot_df.to_csv(pivot_path)

    print(f"Saved pivot comparison to: {pivot_path}")


if __name__ == "__main__":
    main()