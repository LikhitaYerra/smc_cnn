"""Map RL agent actions to SMC controller parameters."""

import numpy as np

PARAM_BOUNDS = {
    "lambda_x": (1.5, 2.5),
    "lambda_y": (1.5, 2.5),
    "lambda_theta": (0.8, 1.3),
    "k_v": (0.2, 0.45),
    "k_omega": (0.6, 1.0),
    "phi": (0.4, 0.7),
    "omega_smoothing": (0.9, 0.99),
}

FIXED_PARAMS = {
    "max_v": 0.65,
    "max_omega": 1.55,
}

PARAM_KEYS = list(PARAM_BOUNDS.keys())


def action_to_parameters(action: np.ndarray) -> dict:
    """Convert normalized action vector [-1, 1] to SMC parameter dict."""
    action = np.clip(action, -1.0, 1.0)
    params = FIXED_PARAMS.copy()

    for i, key in enumerate(PARAM_KEYS):
        low, high = PARAM_BOUNDS[key]
        normalized = (action[i] + 1.0) / 2.0
        params[key] = float(low + normalized * (high - low))

    return params


def parameters_to_action(params: dict) -> np.ndarray:
    """Convert SMC parameters back to normalized action vector."""
    action = np.zeros(len(PARAM_KEYS), dtype=np.float32)
    for i, key in enumerate(PARAM_KEYS):
        low, high = PARAM_BOUNDS[key]
        value = params.get(key, (low + high) / 2)
        normalized = (value - low) / (high - low)
        action[i] = float(normalized * 2.0 - 1.0)
    return action
