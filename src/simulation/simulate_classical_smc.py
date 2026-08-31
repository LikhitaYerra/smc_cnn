import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.controllers.smc_controller import SlidingModeController
from src.simulation.trajectory_generator import generate_straight_trajectory
from src.visualization.plot_results import (
    plot_robot_path,
    plot_tracking_error,
    plot_sliding_surfaces,
    plot_control_signals,
)
from src.utils.logger import save_simulation_log


def run_classical_smc_simulation(
    switching_type: str = "tanh",
    phi: float = 0.5,
    omega_smoothing: float = 0.95,
):
    dt = 0.01
    total_time = 20.0
    desired_speed = 0.3

    t, x_d, y_d, theta_d = generate_straight_trajectory(
        total_time=total_time,
        dt=dt,
        speed=desired_speed,
    )

    robot = DifferentialDriveRobot(
        wheel_base=0.3,
        wheel_radius=0.05,
        initial_state=RobotState(x=0.0, y=0.5, theta=0.0),
    )

    controller = SlidingModeController(
        lambda_x=2.0,
        lambda_y=2.0,
        lambda_theta=1.0,
        k_v=0.3,
        k_omega=0.8,
        phi=phi,
        max_v=0.6,
        max_omega=1.5,
        switching_type=switching_type,
        omega_smoothing=omega_smoothing,
        position_dead_zone=0.01,
        theta_dead_zone=0.01,
    )

    xs = []
    ys = []
    errors = []
    sx_values = []
    sy_values = []
    stheta_values = []
    v_values = []
    omega_values = []

    log_data = []

    for i in range(len(t)):
        state = robot.state

        v, omega, error, surface = controller.compute_control(
            x=state.x,
            y=state.y,
            theta=state.theta,
            x_d=x_d[i],
            y_d=y_d[i],
            theta_d=theta_d[i],
            v_d=desired_speed,
            dt=dt,
        )

        robot.set_velocity(v=v, omega=omega)
        new_state = robot.update(dt)

        xs.append(new_state.x)
        ys.append(new_state.y)
        errors.append(error.distance_error)

        sx_values.append(surface.sx)
        sy_values.append(surface.sy)
        stheta_values.append(surface.stheta)

        v_values.append(v)
        omega_values.append(omega)

        log_data.append(
            {
                "time": t[i],
                "desired_x": x_d[i],
                "desired_y": y_d[i],
                "desired_theta": theta_d[i],
                "actual_x": new_state.x,
                "actual_y": new_state.y,
                "actual_theta": new_state.theta,
                "tracking_error": error.distance_error,
                "error_x": error.ex,
                "error_y": error.ey,
                "error_theta": error.etheta,
                "v": v,
                "omega": omega,
                "s_x": surface.sx,
                "s_y": surface.sy,
                "s_theta": surface.stheta,
                "switching_type": switching_type,
                "phi": phi,
                "omega_smoothing": omega_smoothing,
            }
        )

    os.makedirs("results/plots/classical_smc", exist_ok=True)
    os.makedirs("results/logs/classical_smc", exist_ok=True)

    suffix = f"{switching_type}_phi_{phi}_smooth_{omega_smoothing}".replace(".", "_")

    save_simulation_log(
        log_data,
        save_path=f"results/logs/classical_smc/log_{suffix}.csv",
    )

    plot_robot_path(
        xs,
        ys,
        title=f"Robot Path With Classical SMC ({switching_type})",
        save_path=f"results/plots/classical_smc/robot_path_{suffix}.png",
    )

    plot_tracking_error(
        t,
        errors,
        title=f"Tracking Error With Classical SMC ({switching_type})",
        save_path=f"results/plots/classical_smc/tracking_error_{suffix}.png",
    )

    plot_sliding_surfaces(
        t,
        sx_values,
        sy_values,
        stheta_values,
        save_path=f"results/plots/classical_smc/sliding_surfaces_{suffix}.png",
    )

    plot_control_signals(
        t,
        v_values,
        omega_values,
        title=f"Control Signals With Classical SMC ({switching_type})",
        save_path=f"results/plots/classical_smc/control_signals_{suffix}.png",
    )


def main():
    run_classical_smc_simulation(
        switching_type="tanh",
        phi=0.5,
        omega_smoothing=0.95,
    )


if __name__ == "__main__":
    main()