import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.controllers.tracking_error import compute_tracking_error
from src.simulation.trajectory_generator import generate_straight_trajectory
from src.visualization.plot_results import plot_robot_path, plot_tracking_error


def main():
    dt = 0.01
    total_time = 20.0

    t, x_d, y_d, theta_d = generate_straight_trajectory(
        total_time=total_time,
        dt=dt,
        speed=0.3,
    )

    robot = DifferentialDriveRobot(
        wheel_base=0.3,
        wheel_radius=0.05,
        initial_state=RobotState(x=0.0, y=0.5, theta=0.0),
    )

    xs = []
    ys = []
    errors = []

    for i in range(len(t)):
        robot.set_velocity(v=0.3, omega=0.0)
        state = robot.update(dt)

        error = compute_tracking_error(
            x=state.x,
            y=state.y,
            theta=state.theta,
            x_d=x_d[i],
            y_d=y_d[i],
            theta_d=theta_d[i],
        )

        xs.append(state.x)
        ys.append(state.y)
        errors.append(error.distance_error)

    os.makedirs("results/plots", exist_ok=True)

    plot_robot_path(
        xs,
        ys,
        title="Robot Path Without Controller",
        save_path="results/plots/robot_path_without_controller.png",
    )

    plot_tracking_error(
        t,
        errors,
        title="Tracking Error Without Controller",
        save_path="results/plots/tracking_error_without_controller.png",
    )


if __name__ == "__main__":
    main()