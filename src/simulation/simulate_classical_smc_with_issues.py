import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.controllers.smc_controller import SlidingModeController
from src.simulation.trajectory_generator import generate_straight_trajectory
from src.simulation.noise import SensorNoise
from src.simulation.disturbances import ExternalDisturbance
from src.simulation.uncertainty import WheelSlip
from src.visualization.plot_results import (
    plot_robot_path,
    plot_tracking_error,
    plot_sliding_surfaces,
    plot_control_signals,
)
from src.utils.logger import save_simulation_log


def run_classical_smc_with_issues(
    scenario_name: str,
    enable_noise: bool = False,
    enable_disturbance: bool = False,
    enable_slip: bool = False,
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
        phi=0.5,
        max_v=0.6,
        max_omega=1.5,
        switching_type="sat",
        omega_smoothing=0.95,
        position_dead_zone=0.01,
        theta_dead_zone=0.01,
    )

    noise = SensorNoise(position_std=0.02, theta_std=0.01, seed=42)
    disturbance = ExternalDisturbance(
        start_time=8.0,
        duration=0.5,
        dx=0.0,
        dy=0.4,
        dtheta=0.0,
    )
    slip = WheelSlip(
        start_time=10.0,
        end_time=14.0,
        slip_factor=0.7,
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
        current_time = t[i]

        if enable_disturbance:
            disturbance.apply(robot, current_time)

        true_state = robot.state

        if enable_noise:
            measured_x, measured_y, measured_theta = noise.apply(
                true_state.x,
                true_state.y,
                true_state.theta,
            )
        else:
            measured_x, measured_y, measured_theta = (
                true_state.x,
                true_state.y,
                true_state.theta,
            )

        v, omega, error, surface = controller.compute_control(
            x=measured_x,
            y=measured_y,
            theta=measured_theta,
            x_d=x_d[i],
            y_d=y_d[i],
            theta_d=theta_d[i],
            v_d=desired_speed,
            dt=dt,
        )

        commanded_v = v
        commanded_omega = omega

        if enable_slip:
            v, omega = slip.apply(v, omega, current_time)

        robot.set_velocity(v=v, omega=omega)
        new_state = robot.update(dt)

        xs.append(new_state.x)
        ys.append(new_state.y)

        true_error = ((x_d[i] - new_state.x) ** 2 + (y_d[i] - new_state.y) ** 2) ** 0.5
        errors.append(true_error)

        sx_values.append(surface.sx)
        sy_values.append(surface.sy)
        stheta_values.append(surface.stheta)

        v_values.append(commanded_v)
        omega_values.append(commanded_omega)

        log_data.append(
            {
                "time": current_time,
                "scenario": scenario_name,
                "desired_x": x_d[i],
                "desired_y": y_d[i],
                "desired_theta": theta_d[i],
                "actual_x": new_state.x,
                "actual_y": new_state.y,
                "actual_theta": new_state.theta,
                "measured_x": measured_x,
                "measured_y": measured_y,
                "measured_theta": measured_theta,
                "tracking_error": true_error,
                "v_commanded": commanded_v,
                "omega_commanded": commanded_omega,
                "v_applied": v,
                "omega_applied": omega,
                "s_x": surface.sx,
                "s_y": surface.sy,
                "s_theta": surface.stheta,
                "noise_enabled": enable_noise,
                "disturbance_enabled": enable_disturbance,
                "slip_enabled": enable_slip,
            }
        )

    plot_dir = f"results/plots/classical_smc_issues/{scenario_name}"
    log_dir = "results/logs/classical_smc_issues"

    os.makedirs(plot_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    save_simulation_log(
        log_data,
        save_path=f"{log_dir}/log_{scenario_name}.csv",
    )

    plot_robot_path(
        xs,
        ys,
        title=f"Classical SMC Path - {scenario_name}",
        save_path=f"{plot_dir}/robot_path.png",
    )

    plot_tracking_error(
        t,
        errors,
        title=f"Tracking Error - {scenario_name}",
        save_path=f"{plot_dir}/tracking_error.png",
    )

    plot_sliding_surfaces(
        t,
        sx_values,
        sy_values,
        stheta_values,
        save_path=f"{plot_dir}/sliding_surfaces.png",
    )

    plot_control_signals(
        t,
        v_values,
        omega_values,
        title=f"Control Signals - {scenario_name}",
        save_path=f"{plot_dir}/control_signals.png",
    )


def main():
    scenarios = [
        {
            "scenario_name": "normal",
            "enable_noise": False,
            "enable_disturbance": False,
            "enable_slip": False,
        },
        {
            "scenario_name": "noise",
            "enable_noise": True,
            "enable_disturbance": False,
            "enable_slip": False,
        },
        {
            "scenario_name": "disturbance",
            "enable_noise": False,
            "enable_disturbance": True,
            "enable_slip": False,
        },
        {
            "scenario_name": "slip",
            "enable_noise": False,
            "enable_disturbance": False,
            "enable_slip": True,
        },
        {
            "scenario_name": "combined",
            "enable_noise": True,
            "enable_disturbance": True,
            "enable_slip": True,
        },
    ]

    for scenario in scenarios:
        run_classical_smc_with_issues(**scenario)


if __name__ == "__main__":
    main()