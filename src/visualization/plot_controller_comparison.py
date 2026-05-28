import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


SCENARIOS = [
    "normal",
    "noise",
    "disturbance",
    "slip",
    "combined",
]


def load_logs(scenario: str):
    classical_path = Path(f"results/logs/classical_smc_issues/log_{scenario}.csv")
    adaptive_path = Path(f"results/logs/adaptive_smc/log_{scenario}.csv")

    if not classical_path.exists():
        raise FileNotFoundError(f"Missing file: {classical_path}")

    if not adaptive_path.exists():
        raise FileNotFoundError(f"Missing file: {adaptive_path}")

    classical_df = pd.read_csv(classical_path)
    adaptive_df = pd.read_csv(adaptive_path)

    if "v" not in classical_df.columns and "v_commanded" in classical_df.columns:
        classical_df["v"] = classical_df["v_commanded"]

    if "omega" not in classical_df.columns and "omega_commanded" in classical_df.columns:
        classical_df["omega"] = classical_df["omega_commanded"]

    return classical_df, adaptive_df


def plot_trajectory_comparison(scenario: str, classical_df: pd.DataFrame, adaptive_df: pd.DataFrame):
    output_dir = Path(f"results/plots/comparison/{scenario}")
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))

    plt.plot(
        classical_df["desired_x"],
        classical_df["desired_y"],
        linestyle="--",
        label="Desired trajectory",
    )

    plt.plot(
        classical_df["actual_x"],
        classical_df["actual_y"],
        label="Classical SMC",
    )

    plt.plot(
        adaptive_df["actual_x"],
        adaptive_df["actual_y"],
        label="CNN-adaptive SMC",
    )

    plt.xlabel("x position [m]")
    plt.ylabel("y position [m]")
    plt.title(f"Trajectory Comparison - {scenario}")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.savefig(output_dir / "trajectory_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_tracking_error_comparison(scenario: str, classical_df: pd.DataFrame, adaptive_df: pd.DataFrame):
    output_dir = Path(f"results/plots/comparison/{scenario}")
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 5))

    plt.plot(
        classical_df["time"],
        classical_df["tracking_error"],
        label="Classical SMC",
    )

    plt.plot(
        adaptive_df["time"],
        adaptive_df["tracking_error"],
        label="CNN-adaptive SMC",
    )

    plt.xlabel("Time [s]")
    plt.ylabel("Tracking error [m]")
    plt.title(f"Tracking Error Comparison - {scenario}")
    plt.grid(True)
    plt.legend()
    plt.savefig(output_dir / "tracking_error_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_control_signal_comparison(scenario: str, classical_df: pd.DataFrame, adaptive_df: pd.DataFrame):
    output_dir = Path(f"results/plots/comparison/{scenario}")
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 5))

    plt.plot(
        classical_df["time"],
        classical_df["omega"],
        label="Classical SMC omega",
    )

    plt.plot(
        adaptive_df["time"],
        adaptive_df["omega"],
        label="CNN-adaptive SMC omega",
    )

    plt.xlabel("Time [s]")
    plt.ylabel("Angular velocity command omega [rad/s]")
    plt.title(f"Control Signal Comparison - {scenario}")
    plt.grid(True)
    plt.legend()
    plt.savefig(output_dir / "omega_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()


def generate_all_comparison_plots():
    for scenario in SCENARIOS:
        classical_df, adaptive_df = load_logs(scenario)

        plot_trajectory_comparison(
            scenario=scenario,
            classical_df=classical_df,
            adaptive_df=adaptive_df,
        )

        plot_tracking_error_comparison(
            scenario=scenario,
            classical_df=classical_df,
            adaptive_df=adaptive_df,
        )

        plot_control_signal_comparison(
            scenario=scenario,
            classical_df=classical_df,
            adaptive_df=adaptive_df,
        )

        print(f"Saved comparison plots for scenario: {scenario}")


def main():
    generate_all_comparison_plots()


if __name__ == "__main__":
    main()