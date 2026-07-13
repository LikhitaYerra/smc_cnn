"""Aggregate metrics for all controller logs."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.evaluation.metrics import compute_all_metrics


CONTROLLERS = [
    ("classical_smc", "classical_smc_issues"),
    ("fuzzy_smc", "fuzzy_smc"),
    ("cnn_adaptive_smc", "adaptive_smc"),
    ("oracle_adaptive_smc", "oracle_adaptive_smc"),
    ("rl_adaptive_smc", "rl_adaptive_smc"),
]

SCENARIOS = ["normal", "noise", "disturbance", "slip", "combined"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "v" not in df.columns and "v_commanded" in df.columns:
        df["v"] = df["v_commanded"]
    if "omega" not in df.columns and "omega_commanded" in df.columns:
        df["omega"] = df["omega_commanded"]
    return df


def main():
    rows = []
    logs_root = Path("results/logs")

    for controller, log_name in CONTROLLERS:
        controller_dir = logs_root / log_name
        if not controller_dir.exists():
            continue
        for scenario in SCENARIOS:
            log_path = controller_dir / f"log_{scenario}.csv"
            if not log_path.exists():
                continue
            df = normalize_columns(pd.read_csv(log_path))
            metrics = compute_all_metrics(df)
            rows.append({"controller": controller, "scenario": scenario, **metrics})

    if not rows:
        raise RuntimeError("No controller logs found. Run src/experiments/run_major_experiments.py first.")

    results_df = pd.DataFrame(rows)
    output_dir = Path("results/metrics")
    output_dir.mkdir(parents=True, exist_ok=True)

    save_path = output_dir / "all_controllers_metrics.csv"
    results_df.to_csv(save_path, index=False)

    pivot = results_df.pivot_table(
        index="scenario",
        columns="controller",
        values=["rmse_tracking_error", "final_tracking_error", "chattering_index"],
    )
    pivot.to_csv(output_dir / "all_controllers_metrics_pivot.csv")

    print(results_df.to_string(index=False))
    print(f"\nSaved: {save_path}")


if __name__ == "__main__":
    main()
