"""RL policy wrapper that selects SMC parameter presets online."""

from __future__ import annotations

import os

import numpy as np

from src.controllers.adaptive_parameters import ADAPTIVE_SMC_PARAMETERS
from src.controllers.adaptive_smc_controller import AdaptiveSlidingModeController
from src.rl.smc_parameter_env import SCENARIO_NAMES


class RLAdaptiveSlidingModeController:
    def __init__(
        self,
        model_path: str = "models/rl_smc_parameter_policy.zip",
        state_path: str = "models/rl_smc_parameter_policy_state.pt",
        switching_type: str = "tanh",
        update_interval_steps: int = 20,
    ):
        from stable_baselines3 import PPO
        import torch

        from src.rl.smc_parameter_env import SMCParameterSelectionEnv

        if not os.path.exists(state_path) and not os.path.exists(model_path):
            raise FileNotFoundError(
                "RL policy not found. Run src/rl/train_rl_policy.py first."
            )

        env = SMCParameterSelectionEnv(randomize_scenario=True, seed=42)
        self.model = PPO("MlpPolicy", env, verbose=0)
        if os.path.exists(state_path):
            state_dict = torch.load(state_path, map_location="cpu", weights_only=True)
            self.model.policy.load_state_dict(state_dict)
        else:
            self.model = PPO.load(model_path)
        self.update_interval_steps = update_interval_steps
        self._step_counter = 0
        self.prev_error = 0.0
        self.prev_omega = 0.0
        self.omega_jitter = 0.0
        self._scenario_flags = (0.0, 0.0)

        self.adaptive = AdaptiveSlidingModeController(
            initial_params=ADAPTIVE_SMC_PARAMETERS["normal"],
            switching_type=switching_type,
            parameter_filter_alpha=0.8,
        )

    def set_scenario_flags(self, enable_noise: bool, enable_slip: bool):
        self._scenario_flags = (float(enable_noise), float(enable_slip))

    def reset(self):
        self._step_counter = 0
        self.prev_error = 0.0
        self.prev_omega = 0.0
        self.omega_jitter = 0.0
        self.adaptive.reset()

    def compute_control(self, *args, **kwargs):
        v, omega, error, surface = self.adaptive.compute_control(*args, **kwargs)

        tracking_error = (error.ex ** 2 + error.ey ** 2) ** 0.5
        error_rate = (tracking_error - self.prev_error) / kwargs.get("dt", 0.01)
        self.omega_jitter = 0.9 * self.omega_jitter + 0.1 * abs(omega - self.prev_omega)

        self._step_counter += 1
        if self._step_counter % self.update_interval_steps == 0:
            obs = np.array(
                [
                    min(tracking_error, 1.0),
                    np.clip(error_rate, -5.0, 5.0),
                    min(self.omega_jitter, 1.0),
                    self._scenario_flags[0],
                    self._scenario_flags[1],
                ],
                dtype=np.float32,
            )
            action, _ = self.model.predict(obs, deterministic=True)
            preset = SCENARIO_NAMES[int(action)]
            self.adaptive.update_parameters(ADAPTIVE_SMC_PARAMETERS[preset])

        self.prev_error = tracking_error
        self.prev_omega = omega
        return v, omega, error, surface
