"""Unified simulation engine supporting classical, CNN-adaptive, and RL control modes."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from src.robot.robot_state import RobotState
from src.robot.differential_drive import DifferentialDriveRobot
from src.controllers.smc_controller import SlidingModeController
from src.controllers.adaptive_parameters import get_adaptive_smc_parameters
from src.controllers.adaptive_smc_controller import AdaptiveSlidingModeController
from src.runtime.lite_mode import is_lite_mode
from src.simulation.trajectory_generator import (
    generate_straight_trajectory,
    generate_circular_trajectory,
    generate_s_trajectory,
)
from src.simulation.noise import SensorNoise
from src.simulation.disturbances import ExternalDisturbance
from src.simulation.uncertainty import WheelSlip


CONTROLLER_MODES = ("classical", "cnn_adaptive", "rl_agent")


@dataclass
class SimulationConfig:
    dt: float = 0.01
    total_time: float = 20.0
    desired_speed: float = 0.3
    trajectory_type: str = "straight"
    controller_mode: str = "cnn_adaptive"
    scenario_name: str = "normal"
    enable_noise: bool = False
    enable_disturbance: bool = False
    enable_slip: bool = False
    wheel_base: float = 0.3
    wheel_radius: float = 0.05
    initial_x: float = 0.0
    initial_y: float = 0.5
    initial_theta: float = 0.0
    simulation_speed: float = 1.0


@dataclass
class SimulationState:
    time: float = 0.0
    step: int = 0
    running: bool = False
    finished: bool = False
    controller_mode: str = "cnn_adaptive"
    scenario_name: str = "normal"
    predicted_scenario: str = "normal"
    cnn_confidence: float = 0.0
    actual_x: float = 0.0
    actual_y: float = 0.0
    actual_theta: float = 0.0
    desired_x: float = 0.0
    desired_y: float = 0.0
    desired_theta: float = 0.0
    tracking_error: float = 0.0
    v: float = 0.0
    omega: float = 0.0
    s_x: float = 0.0
    s_y: float = 0.0
    s_theta: float = 0.0
    rl_reward: float = 0.0
    active_params: dict = field(default_factory=dict)
    path_history: list = field(default_factory=list)
    desired_path: list = field(default_factory=list)
    error_history: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)


class SimulationEngine:
    """Steppable simulation engine for real-time digital twin visualization."""

    def __init__(self, config: SimulationConfig | None = None):
        self.config = config or SimulationConfig()
        self.state = SimulationState()
        self._t = None
        self._x_d = None
        self._y_d = None
        self._theta_d = None
        self._robot: DifferentialDriveRobot | None = None
        self._controller = None
        self._predictor = None
        self._map_generator = None
        self._rl_adapter = None
        self._noise = None
        self._disturbance = None
        self._slip = None
        self._errors: list[float] = []
        self._v_history: list[float] = []
        self._omega_history: list[float] = []
        self._prediction = {"scenario": "normal", "confidence": 0.0}

    def reset(self, config: SimulationConfig | None = None) -> SimulationState:
        if config is not None:
            self.config = config

        cfg = self.config
        self._t, self._x_d, self._y_d, self._theta_d = self._generate_trajectory(cfg)

        self._robot = DifferentialDriveRobot(
            wheel_base=cfg.wheel_base,
            wheel_radius=cfg.wheel_radius,
            initial_state=RobotState(
                x=cfg.initial_x,
                y=cfg.initial_y,
                theta=cfg.initial_theta,
            ),
        )

        self._setup_controller(cfg.controller_mode)
        self._setup_disturbances(cfg)

        self._errors = []
        self._v_history = []
        self._omega_history = []
        self._prediction = {"scenario": cfg.scenario_name, "confidence": 1.0}

        desired_path = [
            {"x": float(x), "y": float(y)}
            for x, y in zip(self._x_d[::10], self._y_d[::10])
        ]

        self.state = SimulationState(
            running=False,
            finished=False,
            controller_mode=cfg.controller_mode,
            scenario_name=cfg.scenario_name,
            predicted_scenario=cfg.scenario_name,
            actual_x=cfg.initial_x,
            actual_y=cfg.initial_y,
            actual_theta=cfg.initial_theta,
            desired_x=float(self._x_d[0]) if len(self._x_d) else 0.0,
            desired_y=float(self._y_d[0]) if len(self._y_d) else 0.0,
            desired_theta=float(self._theta_d[0]) if len(self._theta_d) else 0.0,
            desired_path=desired_path,
            path_history=[{"x": cfg.initial_x, "y": cfg.initial_y, "t": 0.0}],
            active_params=self._get_current_params(),
            error_history=[],
        )
        return self.state

    def step(self) -> SimulationState:
        if self.state.finished or not self.state.running:
            return self.state

        i = self.state.step
        if i >= len(self._t):
            self.state.finished = True
            self.state.running = False
            self._update_metrics()
            return self.state

        cfg = self.config
        current_time = float(self._t[i])
        dt = cfg.dt

        if cfg.enable_disturbance:
            self._disturbance.apply(self._robot, current_time)

        true_state = self._robot.state

        if cfg.enable_noise:
            measured_x, measured_y, measured_theta = self._noise.apply(
                true_state.x, true_state.y, true_state.theta
            )
        else:
            measured_x, measured_y, measured_theta = (
                true_state.x,
                true_state.y,
                true_state.theta,
            )

        active_params = self._update_controller_params(i, dt, measured_x, measured_y, measured_theta)

        v, omega, error, surface = self._controller.compute_control(
            x=measured_x,
            y=measured_y,
            theta=measured_theta,
            x_d=float(self._x_d[i]),
            y_d=float(self._y_d[i]),
            theta_d=float(self._theta_d[i]),
            v_d=cfg.desired_speed,
            dt=dt,
        )

        commanded_v, commanded_omega = v, omega

        if cfg.enable_slip:
            v, omega = self._slip.apply(v, omega, current_time)

        self._robot.set_velocity(v=v, omega=omega)
        new_state = self._robot.update(dt)

        true_error = math.sqrt(
            (float(self._x_d[i]) - new_state.x) ** 2
            + (float(self._y_d[i]) - new_state.y) ** 2
        )

        self._errors.append(true_error)
        self._v_history.append(commanded_v)
        self._omega_history.append(commanded_omega)

        rl_reward = self._compute_step_reward(true_error, commanded_v, commanded_omega)

        error_history = self.state.error_history + [
            {"t": current_time, "error": true_error}
        ]
        # Keep last 300 points for live chart
        if len(error_history) > 300:
            error_history = error_history[-300:]

        self.state = SimulationState(
            time=current_time,
            step=i + 1,
            running=True,
            finished=False,
            controller_mode=cfg.controller_mode,
            scenario_name=cfg.scenario_name,
            predicted_scenario=self._prediction["scenario"],
            cnn_confidence=self._prediction["confidence"],
            actual_x=new_state.x,
            actual_y=new_state.y,
            actual_theta=new_state.theta,
            desired_x=float(self._x_d[i]),
            desired_y=float(self._y_d[i]),
            desired_theta=float(self._theta_d[i]),
            tracking_error=true_error,
            v=commanded_v,
            omega=commanded_omega,
            s_x=surface.sx,
            s_y=surface.sy,
            s_theta=surface.stheta,
            rl_reward=rl_reward,
            active_params=active_params,
            path_history=self.state.path_history
            + [{"x": new_state.x, "y": new_state.y, "t": current_time}],
            desired_path=self.state.desired_path,
            metrics=self.state.metrics,
            error_history=error_history,
        )
        return self.state

    def pause(self):
        self.state.running = False

    def resume(self):
        if not self.state.finished:
            self.state.running = True

    def to_dict(self) -> dict[str, Any]:
        s = self.state
        return {
            "time": s.time,
            "step": s.step,
            "total_steps": len(self._t) if self._t is not None else 0,
            "running": s.running,
            "finished": s.finished,
            "controller_mode": s.controller_mode,
            "scenario_name": s.scenario_name,
            "predicted_scenario": s.predicted_scenario,
            "cnn_confidence": s.cnn_confidence,
            "robot": {
                "x": s.actual_x,
                "y": s.actual_y,
                "theta": s.actual_theta,
            },
            "desired": {
                "x": s.desired_x,
                "y": s.desired_y,
                "theta": s.desired_theta,
            },
            "tracking_error": s.tracking_error,
            "control": {"v": s.v, "omega": s.omega},
            "sliding_surface": {"sx": s.s_x, "sy": s.s_y, "stheta": s.s_theta},
            "rl_reward": s.rl_reward,
            "active_params": s.active_params,
            "path_history": s.path_history[-500:],
            "desired_path": s.desired_path,
            "metrics": s.metrics,
            "error_history": s.error_history[-150:],
            "rl_model_loaded": self._rl_adapter.is_trained if self._rl_adapter else False,
        }

    def _generate_trajectory(self, cfg: SimulationConfig):
        if cfg.trajectory_type == "circle":
            return generate_circular_trajectory(cfg.total_time, cfg.dt)
        if cfg.trajectory_type == "s_curve":
            return generate_s_trajectory(cfg.total_time, cfg.dt, speed=cfg.desired_speed)
        return generate_straight_trajectory(cfg.total_time, cfg.dt, speed=cfg.desired_speed)

    def _setup_controller(self, mode: str):
        if mode == "classical":
            self._controller = SlidingModeController(
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
            return

        initial_params = get_adaptive_smc_parameters(self.config.scenario_name)
        self._controller = AdaptiveSlidingModeController(
            initial_params=initial_params,
            switching_type="sat",
            position_dead_zone=0.01,
            theta_dead_zone=0.01,
            parameter_filter_alpha=0.8,
        )

        if mode == "cnn_adaptive" and not is_lite_mode():
            try:
                from src.cnn.predictor import CNNEnvironmentPredictor
                from src.data_generation.environment_generator import EnvironmentMapGenerator

                self._predictor = CNNEnvironmentPredictor(
                    model_path="models/cnn_environment_classifier.pt"
                )
                self._map_generator = EnvironmentMapGenerator(map_size=64, seed=42)
            except Exception:
                self._predictor = None
                self._map_generator = None

        if mode == "rl_agent":
            if is_lite_mode():
                from src.rl.rl_adapter_lite import RLParameterAdapter
            else:
                from src.rl.rl_adapter import RLParameterAdapter

            self._rl_adapter = RLParameterAdapter()

    def _setup_disturbances(self, cfg: SimulationConfig):
        self._noise = SensorNoise(position_std=0.02, theta_std=0.01, seed=42)
        self._disturbance = ExternalDisturbance(
            start_time=8.0, duration=0.5, dx=0.0, dy=0.4, dtheta=0.0
        )
        self._slip = WheelSlip(start_time=10.0, end_time=14.0, slip_factor=0.7)

    def _update_controller_params(self, step: int, dt: float, x, y, theta) -> dict:
        cfg = self.config
        mode = cfg.controller_mode

        if mode == "classical":
            return self._get_classical_params()

        if mode == "cnn_adaptive" and self._predictor and self._map_generator:
            if step % int(1.0 / dt) == 0:
                env_map = self._map_generator.generate(cfg.scenario_name)
                self._prediction = self._predictor.predict(env_map)
                new_params = get_adaptive_smc_parameters(self._prediction["scenario"])
                return self._controller.update_parameters(new_params)
            return self._controller.parameter_filter.previous_params

        if mode == "rl_agent" and self._rl_adapter:
            if step % int(0.5 / dt) == 0:
                obs = self._rl_adapter.build_observation(
                    x, y, theta,
                    float(self._x_d[step]),
                    float(self._y_d[step]),
                    float(self._theta_d[step]),
                    self._errors[-1] if self._errors else 0.0,
                )
                new_params = self._rl_adapter.predict_parameters(obs)
                return self._controller.update_parameters(new_params)
            return self._controller.parameter_filter.previous_params

        new_params = get_adaptive_smc_parameters(cfg.scenario_name)
        if step == 0:
            return self._controller.update_parameters(new_params)
        return self._controller.parameter_filter.previous_params

    def _get_classical_params(self) -> dict:
        return {
            "lambda_x": 2.0,
            "lambda_y": 2.0,
            "lambda_theta": 1.0,
            "k_v": 0.3,
            "k_omega": 0.8,
            "phi": 0.5,
            "max_v": 0.6,
            "max_omega": 1.5,
            "omega_smoothing": 0.95,
        }

    def _get_current_params(self) -> dict:
        if self.config.controller_mode == "classical":
            return self._get_classical_params()
        return get_adaptive_smc_parameters(self.config.scenario_name)

    def _compute_step_reward(self, error: float, v: float, omega: float) -> float:
        from src.rl.reward import compute_step_reward

        prev_omega = self._omega_history[-1] if self._omega_history else 0.0
        return compute_step_reward(error, v, omega, prev_omega)

    def _update_metrics(self):
        if not self._errors:
            return
        import numpy as np

        errors = np.array(self._errors)
        omegas = np.array(self._omega_history)
        self.state.metrics = {
            "mean_tracking_error": float(np.mean(errors)),
            "rmse_tracking_error": float(np.sqrt(np.mean(errors**2))),
            "max_tracking_error": float(np.max(errors)),
            "chattering_index": float(np.sum(np.abs(np.diff(omegas)))),
            "control_effort": float(np.sum(omegas**2 + np.array(self._v_history) ** 2)),
        }
