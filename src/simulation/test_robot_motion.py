import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.visualization.plot_results import plot_robot_path


def run_motion_test():
    dt = 0.01
    total_time = 10.0
    steps = int(total_time / dt)

    robot = DifferentialDriveRobot(
        wheel_base=0.3,
        wheel_radius=0.05,
        initial_state=RobotState(x=0.0, y=0.0, theta=0.0),
    )

    xs = []
    ys = []
    thetas = []

    for i in range(steps):
        t = i * dt

        if t < 3.0:
            v = 0.5
            omega = 0.0
        elif t < 6.0:
            v = 0.5
            omega = 0.7
        else:
            v = 0.0
            omega = 1.0

        robot.set_velocity(v, omega)
        state = robot.update(dt)

        xs.append(state.x)
        ys.append(state.y)
        thetas.append(state.theta)

    os.makedirs("results/plots", exist_ok=True)

    plot_robot_path(
        xs,
        ys,
        title="Basic Differential-Drive Robot Motion",
        save_path="results/plots/basic_robot_motion.png",
    )


if __name__ == "__main__":
    run_motion_test()