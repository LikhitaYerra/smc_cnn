import argparse
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def normalize_classical_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "v" not in df.columns and "v_commanded" in df.columns:
        df["v"] = df["v_commanded"]

    if "omega" not in df.columns and "omega_commanded" in df.columns:
        df["omega"] = df["omega_commanded"]

    return df


def load_logs(scenario: str):
    classical_path = Path(f"results/logs/classical_smc_issues/log_{scenario}.csv")
    adaptive_path = Path(f"results/logs/adaptive_smc/log_{scenario}.csv")

    if not classical_path.exists():
        raise FileNotFoundError(f"Missing classical log: {classical_path}")

    if not adaptive_path.exists():
        raise FileNotFoundError(f"Missing adaptive log: {adaptive_path}")

    classical_df = pd.read_csv(classical_path)
    adaptive_df = pd.read_csv(adaptive_path)

    classical_df = normalize_classical_columns(classical_df)

    return classical_df, adaptive_df


def create_animation(
    scenario: str,
    output_path: str | None = None,
    frame_step: int = 10,
    fps: int = 20,
):
    classical_df, adaptive_df = load_logs(scenario)

    if output_path is None:
        output_path = f"results/animations/{scenario}_comparison.gif"

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    classical_df = classical_df.iloc[::frame_step].reset_index(drop=True)
    adaptive_df = adaptive_df.iloc[::frame_step].reset_index(drop=True)

    n_frames = min(len(classical_df), len(adaptive_df))

    desired_x = classical_df["desired_x"]
    desired_y = classical_df["desired_y"]

    x_min = min(
        classical_df["actual_x"].min(),
        adaptive_df["actual_x"].min(),
        desired_x.min(),
    ) - 0.5

    x_max = max(
        classical_df["actual_x"].max(),
        adaptive_df["actual_x"].max(),
        desired_x.max(),
    ) + 0.5

    y_min = min(
        classical_df["actual_y"].min(),
        adaptive_df["actual_y"].min(),
        desired_y.min(),
    ) - 0.5

    y_max = max(
        classical_df["actual_y"].max(),
        adaptive_df["actual_y"].max(),
        desired_y.max(),
    ) + 0.5

    fig, ax = plt.subplots(figsize=(9, 6))

    ax.plot(
        desired_x,
        desired_y,
        linestyle="--",
        linewidth=2,
        label="Desired trajectory",
    )

    classical_line, = ax.plot([], [], linewidth=2, label="Classical SMC path")
    adaptive_line, = ax.plot([], [], linewidth=2, label="CNN-adaptive SMC path")

    classical_point, = ax.plot([], [], marker="o", markersize=8, label="Classical robot")
    adaptive_point, = ax.plot([], [], marker="s", markersize=8, label="Adaptive robot")

    time_text = ax.text(
        0.02,
        0.95,
        "",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
    )

    error_text = ax.text(
        0.02,
        0.88,
        "",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x position [m]")
    ax.set_ylabel("y position [m]")
    ax.set_title(f"Classical SMC vs CNN-adaptive SMC - {scenario}")
    ax.grid(True)
    ax.legend(loc="upper right")

    def init():
        classical_line.set_data([], [])
        adaptive_line.set_data([], [])
        classical_point.set_data([], [])
        adaptive_point.set_data([], [])
        time_text.set_text("")
        error_text.set_text("")

        return (
            classical_line,
            adaptive_line,
            classical_point,
            adaptive_point,
            time_text,
            error_text,
        )

    def update(frame):
        classical_data = classical_df.iloc[: frame + 1]
        adaptive_data = adaptive_df.iloc[: frame + 1]

        classical_line.set_data(
            classical_data["actual_x"],
            classical_data["actual_y"],
        )

        adaptive_line.set_data(
            adaptive_data["actual_x"],
            adaptive_data["actual_y"],
        )

        classical_point.set_data(
            [classical_df.loc[frame, "actual_x"]],
            [classical_df.loc[frame, "actual_y"]],
        )

        adaptive_point.set_data(
            [adaptive_df.loc[frame, "actual_x"]],
            [adaptive_df.loc[frame, "actual_y"]],
        )

        current_time = classical_df.loc[frame, "time"]
        classical_error = classical_df.loc[frame, "tracking_error"]
        adaptive_error = adaptive_df.loc[frame, "tracking_error"]

        time_text.set_text(f"Time: {current_time:.2f} s")
        error_text.set_text(
            f"Classical error: {classical_error:.3f} m\n"
            f"Adaptive error: {adaptive_error:.3f} m"
        )

        return (
            classical_line,
            adaptive_line,
            classical_point,
            adaptive_point,
            time_text,
            error_text,
        )

    animation = FuncAnimation(
        fig,
        update,
        frames=n_frames,
        init_func=init,
        blit=True,
        interval=1000 / fps,
    )

    animation.save(
        output_path,
        writer=PillowWriter(fps=fps),
    )

    plt.close(fig)

    print(f"Animation saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Create 2D animation comparing Classical SMC and CNN-adaptive SMC."
    )

    parser.add_argument(
        "--scenario",
        type=str,
        default="combined",
        choices=["normal", "noise", "disturbance", "slip", "combined"],
        help="Scenario to animate.",
    )

    parser.add_argument(
        "--frame-step",
        type=int,
        default=10,
        help="Use every Nth frame to reduce animation size.",
    )

    parser.add_argument(
        "--fps",
        type=int,
        default=20,
        help="Frames per second.",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional output GIF path.",
    )

    args = parser.parse_args()

    create_animation(
        scenario=args.scenario,
        output_path=args.output,
        frame_step=args.frame_step,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()