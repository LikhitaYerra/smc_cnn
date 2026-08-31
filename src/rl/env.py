"""Gymnasium environment for RL-based SMC parameter adaptation."""

from __future__ import annotations

import math
import random

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.controllers.adaptive_smc_controller import AdaptiveSlidingModeController
from src.controllers.adaptive_parameters import get_adaptive_smc_parameters
from src.rl.parameter_mapper import action_to_parameters
from src.rl.reward import compute_step_reward
from src.simulation.trajectory_generator import generate_straight_trajectory
from src.simulation.noise import SensorNoise
from src.simulation.disturbances import ExternalDisturbance
from src.simulation.uncertainty import WheelSlip


SCENARIOS = [
    {"name": "normal", "noise": False, "disturbance": False, "slip": False},
    {"name": "noise", "noise": True, "disturbance": False, "slip": False},
    {"name": "disturbance", "noise": False, "disturbance": True, "slip": False},
    {"name": "slip", "noise": False, "disturbance": False, "slip": True},
    {"name": "combined", "noise": True, "disturbance": True, "slip": True},
]


class SMCParameterEnv(gym.Env):
    """RL environment where the agent adapts SMC gains each control interval."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        dt: float = 0.01,
        episode_steps: int = 500,
        param_update_interval: int = 50,
        desired_speed: float = 0.3,
    ):
        super().__init__()
        self.dt = dt
        self.episode_steps = episode_steps
        self.param_update_interval = param_update_interval
        self.desired_speed = desired_speed

        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(10,), dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(7,), dtype=np.float32
        )

        self._robot = None
        self._controller = None
        self._noise = None
        self._disturbance = None
        self._slip = None
        self._scenario = None
        self._t = None
        self._x_d = None
        self._y_d = None
        self._theta_d = None
        self._step = 0
        self._prev_omega = 0.0
        self._episode_reward = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self._scenario = random.choice(SCENARIOS)
        total_time = self.episode_steps * self.dt
        self._t, self._x_d, self._y_d, self._theta_d = generate_straight_trajectory(
            total_time=total_time, dt=self.dt, speed=self.desired_speed
        )

        self._robot = DifferentialDriveRobot(
            wheel_base=0.3,
            wheel_radius=0.05,
            initial_state=RobotState(x=0.0, y=0.5, theta=0.0),
        )

        initial_params = get_adaptive_smc_parameters(self._scenario["name"])
        self._controller = AdaptiveSlidingModeController(
            initial_params=initial_params,
            switching_type="sat",
            position_dead_zone=0.01,
            theta_dead_zone=0.01,
            parameter_filter_alpha=0.8,
        )

        self._noise = SensorNoise(position_std=0.02, theta_std=0.01, seed=42)
        self._disturbance = ExternalDisturbance(
            start_time=4.0, duration=0.5, dx=0.0, dy=0.3, dtheta=0.0
        )
        self._slip = WheelSlip(start_time=6.0, end_time=9.0, slip_factor=0.7)

        self._step = 0
        self._prev_omega = 0.0
        self._episode_reward = 0.0

        obs = self._get_observation(tracking_error=0.5)
        info = {"scenario": self._scenario["name"]}
        return obs, info

    def step(self, action):
        i = self._step
        current_time = float(self._t[i])

        if self._scenario["disturbance"]:
            self._disturbance.apply(self._robot, current_time)

        true_state = self._robot.state
        if self._scenario["noise"]:
            mx, my, mtheta = self._noise.apply(
                true_state.x, true_state.y, true_state.theta
            )
        else:
            mx, my, mtheta = true_state.x, true_state.y, true_state.theta

        if i % self.param_update_interval == 0:
            params = action_to_parameters(np.array(action, dtype=np.float32))
            self._controller.update_parameters(params)

        v, omega, error, _ = self._controller.compute_control(
            x=mx, y=my, theta=mtheta,
            x_d=float(self._x_d[i]),
            y_d=float(self._y_d[i]),
            theta_d=float(self._theta_d[i]),
            v_d=self.desired_speed,
            dt=self.dt,
        )

        if self._scenario["slip"]:
            v, omega = self._slip.apply(v, omega, current_time)

        self._robot.set_velocity(v=v, omega=omega)
        new_state = self._robot.update(self.dt)

        true_error = math.sqrt(
            (float(self._x_d[i]) - new_state.x) ** 2
            + (float(self._y_d[i]) - new_state.y) ** 2
        )

        reward = compute_step_reward(true_error, v, omega, self._prev_omega)
        self._prev_omega = omega
        self._episode_reward += reward
        self._step += 1

        terminated = self._step >= self.episode_steps
        truncated = False
        obs = self._get_observation(tracking_error=true_error)
        info = {
            "scenario": self._scenario["name"],
            "tracking_error": true_error,
            "episode_reward": self._episode_reward,
        }

        return obs, reward, terminated, truncated, info

    def _get_observation(self, tracking_error: float) -> np.ndarray:
        i = min(self._step, len(self._t) - 1)
        state = self._robot.state
        return np.array(
            [
                state.x,
                state.y,
                math.sin(state.theta),
                math.cos(state.theta),
                float(self._x_d[i]),
                float(self._y_d[i]),
                math.sin(float(self._theta_d[i])),
                math.cos(float(self._theta_d[i])),
                tracking_error,
                float(SCENARIOS.index(self._scenario)),
            ],
            dtype=np.float32,
        )
