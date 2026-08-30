"""RL policy adapter for real-time SMC parameter inference."""

from __future__ import annotations

import math
import os

import numpy as np

from src.controllers.adaptive_parameters import get_adaptive_smc_parameters
from src.rl.agent import PPOAgent


class RLParameterAdapter:
    """Loads trained PPO policy and predicts SMC parameters from observations."""

    DEFAULT_MODEL_PATH = "models/rl_smc_agent.pt"

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.agent = PPOAgent()
        self._loaded = self.agent.load(self.model_path)
        self._fallback_scenario = "combined"

    @property
    def is_trained(self) -> bool:
        return self._loaded

    def build_observation(
        self,
        x: float,
        y: float,
        theta: float,
        x_d: float,
        y_d: float,
        theta_d: float,
        tracking_error: float,
        scenario_idx: int = 4,
    ) -> np.ndarray:
        return np.array(
            [
                x,
                y,
                math.sin(theta),
                math.cos(theta),
                x_d,
                y_d,
                math.sin(theta_d),
                math.cos(theta_d),
                tracking_error,
                float(scenario_idx),
            ],
            dtype=np.float32,
        )

    def predict_parameters(self, obs: np.ndarray) -> dict:
        if self._loaded:
            action, params, _ = self.agent.select_action(obs, deterministic=True)
            return params
        return self._heuristic_parameters(obs)

    def _heuristic_parameters(self, obs: np.ndarray) -> dict:
        """Observation-driven heuristic when no trained model exists (demo-ready)."""
        error = float(obs[8])
        base = get_adaptive_smc_parameters(self._fallback_scenario).copy()

        # Adapt gains based on live tracking error — mimics RL behavior for demos
        error_scale = min(error / 0.3, 1.0)
        base["k_v"] = base["k_v"] * (1.0 + 0.15 * error_scale)
        base["k_omega"] = base["k_omega"] * (1.0 + 0.2 * error_scale)
        base["phi"] = base["phi"] * (1.0 + 0.1 * (1.0 - error_scale))
        base["omega_smoothing"] = min(0.99, base["omega_smoothing"] + 0.01 * (1.0 - error_scale))
        return base


def ensure_rl_model(path: str | None = None) -> bool:
    """Bootstrap a lightweight RL model if none exists."""
    model_path = path or RLParameterAdapter.DEFAULT_MODEL_PATH
    if os.path.exists(model_path):
        return True

    try:
        from src.rl.train_rl import train

        os.makedirs(os.path.dirname(model_path) or ".", exist_ok=True)
        train(n_iterations=15, rollout_steps=512, save_path=model_path)
        return True
    except Exception:
        return False

