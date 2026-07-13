"""Gymnasium environment for RL-based SMC parameter selection."""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from src.controllers.adaptive_parameters import ADAPTIVE_SMC_PARAMETERS
from src.controllers.adaptive_smc_controller import AdaptiveSlidingModeController
from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.simulation.trajectory_generator import generate_straight_trajectory
from src.simulation.noise import SensorNoise
from src.simulation.disturbances import ExternalDisturbance
from src.simulation.uncertainty import WheelSlip


SCENARIO_NAMES = ["normal", "noise", "disturbance", "slip", "combined"]
SCENARIO_FLAGS = {
    "normal": {"enable_noise": False, "enable_disturbance": False, "enable_slip": False},
    "noise": {"enable_noise": True, "enable_disturbance": False, "enable_slip": False},
    "disturbance": {"enable_noise": False, "enable_disturbance": True, "enable_slip": False},
    "slip": {"enable_noise": False, "enable_disturbance": False, "enable_slip": True},
    "combined": {"enable_noise": True, "enable_disturbance": True, "enable_slip": True},
}


class SMCParameterSelectionEnv(gym.Env):
    metadata = {"render_modes": []}

    def __init__(
        self,
        dt: float = 0.01,
        episode_seconds: float = 20.0,
        desired_speed: float = 0.3,
        randomize_scenario: bool = True,
        fixed_scenario: str | None = None,
        seed: int | None = None,
    ):
        super().__init__()
        self.dt = dt
        self.episode_steps = int(episode_seconds / dt)
        self.desired_speed = desired_speed
        self.randomize_scenario = randomize_scenario
        self.fixed_scenario = fixed_scenario
        self.rng = np.random.default_rng(seed)

        self.action_space = spaces.Discrete(len(SCENARIO_NAMES))
        self.observation_space = spaces.Box(
            low=np.array([0.0, -5.0, 0.0, 0.0, 0.0], dtype=np.float32),
            high=np.array([1.0, 5.0, 1.0, 1.0, 1.0], dtype=np.float32),
            dtype=np.float32,
        )

        self._reset_simulation()

    def _reset_simulation(self):
        if self.fixed_scenario is not None:
            self.scenario_name = self.fixed_scenario
        elif self.randomize_scenario:
            self.scenario_name = self.rng.choice(SCENARIO_NAMES)
        else:
            self.scenario_name = "normal"

        flags = SCENARIO_FLAGS[self.scenario_name]
        self.enable_noise = flags["enable_noise"]
        self.enable_disturbance = flags["enable_disturbance"]
        self.enable_slip = flags["enable_slip"]

        t, x_d, y_d, theta_d = generate_straight_trajectory(
            total_time=self.episode_steps * self.dt,
            dt=self.dt,
            speed=self.desired_speed,
        )
        self.t = t
        self.x_d = x_d
        self.y_d = y_d
        self.theta_d = theta_d

        self.robot = DifferentialDriveRobot(
            wheel_base=0.3,
            wheel_radius=0.05,
            initial_state=RobotState(x=0.0, y=0.5, theta=0.0),
        )

        initial_params = ADAPTIVE_SMC_PARAMETERS["normal"]
        self.controller = AdaptiveSlidingModeController(
            initial_params=initial_params,
            switching_type="tanh",
            parameter_filter_alpha=0.8,
        )

        self.noise = SensorNoise(position_std=0.02, theta_std=0.01, seed=42)
        self.disturbance = ExternalDisturbance(start_time=8.0, duration=0.5, dx=0.0, dy=0.4, dtheta=0.0)
        self.slip = WheelSlip(start_time=10.0, end_time=14.0, slip_factor=0.7)

        self.step_idx = 0
        self.prev_error = 0.0
        self.prev_omega = 0.0
        self.omega_jitter = 0.0

    def _get_obs(self, tracking_error: float, error_rate: float) -> np.ndarray:
        return np.array(
            [
                min(tracking_error, 1.0),
                np.clip(error_rate, -5.0, 5.0),
                min(self.omega_jitter, 1.0),
                float(self.enable_noise),
                float(self.enable_slip),
            ],
            dtype=np.float32,
        )

    def reset(self, *, seed=None, options=None):
        if seed is not None:
            self.rng = np.random.default_rng(seed)
        self._reset_simulation()
        return self._get_obs(0.0, 0.0), {}

    def step(self, action: int):
        if self.step_idx >= self.episode_steps:
            return self._get_obs(self.prev_error, 0.0), 0.0, True, False, {}

        current_time = self.t[self.step_idx]

        if self.enable_disturbance:
            self.disturbance.apply(self.robot, current_time)

        state = self.robot.state
        if self.enable_noise:
            mx, my, mtheta = self.noise.apply(state.x, state.y, state.theta)
        else:
            mx, my, mtheta = state.x, state.y, state.theta

        if self.step_idx % 20 == 0:
            preset = SCENARIO_NAMES[int(action)]
            self.controller.update_parameters(ADAPTIVE_SMC_PARAMETERS[preset])

        v, omega, error, _ = self.controller.compute_control(
            x=mx,
            y=my,
            theta=mtheta,
            x_d=self.x_d[self.step_idx],
            y_d=self.y_d[self.step_idx],
            theta_d=self.theta_d[self.step_idx],
            v_d=self.desired_speed,
            dt=self.dt,
        )

        if self.enable_slip:
            v, omega = self.slip.apply(v, omega, current_time)

        self.robot.set_velocity(v=v, omega=omega)
        new_state = self.robot.update(self.dt)

        tracking_error = (
            (self.x_d[self.step_idx] - new_state.x) ** 2
            + (self.y_d[self.step_idx] - new_state.y) ** 2
        ) ** 0.5
        error_rate = (tracking_error - self.prev_error) / self.dt
        self.omega_jitter = 0.9 * self.omega_jitter + 0.1 * abs(omega - self.prev_omega)

        reward = -tracking_error - 0.05 * self.omega_jitter - 0.001 * abs(omega)

        self.prev_error = tracking_error
        self.prev_omega = omega
        self.step_idx += 1
        terminated = self.step_idx >= self.episode_steps

        return self._get_obs(tracking_error, error_rate), float(reward), terminated, False, {}
