"""Export multi-controller comparison tables for the project report."""

import os
import sys
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

SCENARIOS = ["normal", "noise", "disturbance", "slip", "combined"]
CONTROLLERS = [
    "classical_smc",
    "fuzzy_smc",
    "cnn_adaptive_smc",
    "oracle_adaptive_smc",
    "rl_adaptive_smc",
]


def main():
    metrics_path = Path("results/metrics/all_controllers_metrics.csv")
    if not metrics_path.exists():
        raise FileNotFoundError("Run compare_all_controllers.py first.")

    df = pd.read_csv(metrics_path)
    output_dir = Path("results/tables")
    output_dir.mkdir(parents=True, exist_ok=True)

    full_table = df[
        [
            "controller",
            "scenario",
            "rmse_tracking_error",
            "final_tracking_error",
            "control_effort",
            "chattering_index",
        ]
    ].round(4)
    full_table.to_csv(output_dir / "report_all_controllers_metrics.csv", index=False)

    pivot_chatter = df.pivot_table(
        index="scenario", columns="controller", values="chattering_index"
    ).reindex(SCENARIOS)[CONTROLLERS].round(2)
    pivot_final = df.pivot_table(
        index="scenario", columns="controller", values="final_tracking_error"
    ).reindex(SCENARIOS)[CONTROLLERS].round(4)

    pivot_chatter.to_csv(output_dir / "report_chattering_pivot.csv")
    pivot_final.to_csv(output_dir / "report_final_error_pivot.csv")

    classical = df[df["controller"] == "classical_smc"].set_index("scenario")
    cnn = df[df["controller"] == "cnn_adaptive_smc"].set_index("scenario")
    improvements = []
    for scenario in SCENARIOS:
        improvements.append(
            {
                "scenario": scenario,
                "chattering_improvement_pct": round(
                    (classical.loc[scenario, "chattering_index"] - cnn.loc[scenario, "chattering_index"])
                    / classical.loc[scenario, "chattering_index"]
                    * 100,
                    2,
                ),
                "final_error_improvement_pct": round(
                    (classical.loc[scenario, "final_tracking_error"] - cnn.loc[scenario, "final_tracking_error"])
                    / classical.loc[scenario, "final_tracking_error"]
                    * 100,
                    2,
                ),
            }
        )
    pd.DataFrame(improvements).to_csv(output_dir / "report_cnn_improvement_summary.csv", index=False)

    print(full_table.to_string(index=False))
    print(f"\nSaved tables to: {output_dir}")


if __name__ == "__main__":
    main()
