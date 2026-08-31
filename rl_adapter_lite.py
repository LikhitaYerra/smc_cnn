"""Lightweight RL adapter — no PyTorch, for Render free tier."""

from __future__ import annotations

import math

import numpy as np

from src.controllers.adaptive_parameters import get_adaptive_smc_parameters


class RLParameterAdapter:
    """Heuristic RL-style parameter adapter (no trained model required)."""

    def __init__(self, model_path: str | None = None):
        self._fallback_scenario = "combined"

    @property
    def is_trained(self) -> bool:
        return True

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
        error = float(obs[8])
        base = get_adaptive_smc_parameters(self._fallback_scenario).copy()

        error_scale = min(error / 0.3, 1.0)
        base["k_v"] = base["k_v"] * (1.0 + 0.15 * error_scale)
        base["k_omega"] = base["k_omega"] * (1.0 + 0.2 * error_scale)
        base["phi"] = base["phi"] * (1.0 + 0.1 * (1.0 - error_scale))
        base["omega_smoothing"] = min(0.99, base["omega_smoothing"] + 0.01 * (1.0 - error_scale))
        return base
