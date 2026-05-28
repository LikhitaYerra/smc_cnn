import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.simulation.trajectory_generator import (
    generate_straight_trajectory,
    generate_circular_trajectory,
    generate_s_trajectory,
)
from src.visualization.plot_results import plot_reference_trajectory


def main():
    dt = 0.01
    total_time = 20.0

    os.makedirs("results/plots", exist_ok=True)

    _, x_straight, y_straight, _ = generate_straight_trajectory(
        total_time=total_time,
        dt=dt,
        speed=0.3,
    )

    plot_reference_trajectory(
        x_straight,
        y_straight,
        title="Straight Reference Trajectory",
        save_path="results/plots/straight_reference_trajectory.png",
    )

    _, x_circle, y_circle, _ = generate_circular_trajectory(
        total_time=total_time,
        dt=dt,
        radius=2.0,
        angular_speed=0.2,
    )

    plot_reference_trajectory(
        x_circle,
        y_circle,
        title="Circular Reference Trajectory",
        save_path="results/plots/circular_reference_trajectory.png",
    )

    _, x_s, y_s, _ = generate_s_trajectory(
        total_time=total_time,
        dt=dt,
        speed=0.3,
        amplitude=1.0,
        frequency=0.5,
    )

    plot_reference_trajectory(
        x_s,
        y_s,
        title="S-Shaped Reference Trajectory",
        save_path="results/plots/s_reference_trajectory.png",
    )


if __name__ == "__main__":
    main()