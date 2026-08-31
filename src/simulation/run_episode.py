"""Shared kinematic simulation loop for all SMC controller variants."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.simulation.trajectory_generator import generate_straight_trajectory
from src.simulation.noise import SensorNoise
from src.simulation.disturbances import ExternalDisturbance
from src.simulation.uncertainty import WheelSlip


@dataclass
class ScenarioConfig:
    name: str
    enable_noise: bool = False
    enable_disturbance: bool = False
    enable_slip: bool = False


@dataclass
class SimulationConfig:
    dt: float = 0.01
    total_time: float = 20.0
    desired_speed: float = 0.3
    initial_y: float = 0.5


def default_scenarios() -> list[ScenarioConfig]:
    return [
        ScenarioConfig("normal"),
        ScenarioConfig("noise", enable_noise=True),
        ScenarioConfig("disturbance", enable_disturbance=True),
        ScenarioConfig("slip", enable_slip=True),
        ScenarioConfig("combined", enable_noise=True, enable_disturbance=True, enable_slip=True),
    ]


def run_tracking_episode(
    controller_factory: Callable[[], Any],
    scenario: ScenarioConfig,
    sim_config: SimulationConfig = SimulationConfig(),
    on_step: Optional[Callable[[int, float, dict], None]] = None,
    extra_log_fields: Optional[Callable[[int, float, dict], dict]] = None,
) -> list[dict]:
    dt = sim_config.dt
    total_time = sim_config.total_time

    t, x_d, y_d, theta_d = generate_straight_trajectory(
        total_time=total_time,
        dt=dt,
        speed=sim_config.desired_speed,
    )

    robot = DifferentialDriveRobot(
        wheel_base=0.3,
        wheel_radius=0.05,
        initial_state=RobotState(x=0.0, y=sim_config.initial_y, theta=0.0),
    )

    controller = controller_factory()

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

    log_data: list[dict] = []

    for i, current_time in enumerate(t):
        if scenario.enable_disturbance:
            disturbance.apply(robot, current_time)

        true_state = robot.state

        if scenario.enable_noise:
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

        step_context = {
            "index": i,
            "time": current_time,
            "robot": robot,
            "true_state": true_state,
            "measured": (measured_x, measured_y, measured_theta),
            "reference": (x_d[i], y_d[i], theta_d[i]),
            "controller": controller,
            "scenario": scenario.name,
        }

        if on_step is not None:
            on_step(i, current_time, step_context)

        v, omega, error, surface = controller.compute_control(
            x=measured_x,
            y=measured_y,
            theta=measured_theta,
            x_d=x_d[i],
            y_d=y_d[i],
            theta_d=theta_d[i],
            v_d=sim_config.desired_speed,
            dt=dt,
        )

        commanded_v = v
        commanded_omega = omega

        if scenario.enable_slip:
            v, omega = slip.apply(v, omega, current_time)

        robot.set_velocity(v=v, omega=omega)
        new_state = robot.update(dt)

        true_error = ((x_d[i] - new_state.x) ** 2 + (y_d[i] - new_state.y) ** 2) ** 0.5

        row = {
            "time": current_time,
            "scenario": scenario.name,
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
            "v": commanded_v,
            "omega": commanded_omega,
            "v_applied": v,
            "omega_applied": omega,
            "s_x": surface.sx,
            "s_y": surface.sy,
            "s_theta": surface.stheta,
            "noise_enabled": scenario.enable_noise,
            "disturbance_enabled": scenario.enable_disturbance,
            "slip_enabled": scenario.enable_slip,
        }

        if extra_log_fields is not None:
            row.update(extra_log_fields(i, current_time, step_context))

        log_data.append(row)

    return log_data
