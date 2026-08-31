"""Mamdani-style fuzzy scheduler for SMC gain adaptation."""

from __future__ import annotations

import math


def _triangular(x: float, a: float, b: float, c: float) -> float:
    if x <= a or x >= c:
        return 0.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a) if b != a else 0.0
    return (c - x) / (c - b) if c != b else 0.0


class FuzzyGainScheduler:
    """Maps tracking error and chattering proxy to SMC parameter adjustments."""

    BASE_PARAMS = {
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

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self._omega_history: list[float] = []

    def reset(self):
        self._omega_history.clear()

    def _chattering_index(self) -> float:
        if len(self._omega_history) < 2:
            return 0.0
        diffs = [
            abs(self._omega_history[i] - self._omega_history[i - 1])
            for i in range(1, len(self._omega_history))
        ]
        return sum(diffs) / len(diffs)

    def observe(self, tracking_error: float, omega_command: float):
        self._omega_history.append(omega_command)
        if len(self._omega_history) > self.window_size:
            self._omega_history.pop(0)

    def infer(self, tracking_error: float) -> dict:
        err = min(max(tracking_error, 0.0), 0.5)
        chatter = min(self._chattering_index(), 0.5)

        err_low = _triangular(err, 0.0, 0.0, 0.06)
        err_med = _triangular(err, 0.03, 0.10, 0.20)
        err_high = _triangular(err, 0.12, 0.25, 0.50)

        chatter_low = _triangular(chatter, 0.0, 0.0, 0.08)
        chatter_high = _triangular(chatter, 0.05, 0.15, 0.50)

        # Rule strengths (aligned with hand-tuned presets in adaptive_parameters.py)
        noise_mode = min(1.0, chatter_high * 0.9 + err_low * 0.2)
        disturbance_mode = min(1.0, err_high * 0.95)
        slip_mode = min(1.0, err_med * 0.7 + chatter_low * 0.3)
        normal_mode = max(0.0, 1.0 - (noise_mode + disturbance_mode + slip_mode))
        total = normal_mode + noise_mode + disturbance_mode + slip_mode + 1e-9

        w_norm = normal_mode / total
        w_noise = noise_mode / total
        w_dist = disturbance_mode / total
        w_slip = slip_mode / total

        phi = (
            w_norm * 0.50
            + w_noise * 0.58
            + w_dist * 0.52
            + w_slip * 0.62
        )
        k_omega = (
            w_norm * 0.80
            + w_noise * 0.78
            + w_dist * 0.88
            + w_slip * 0.86
        )
        lambda_y = (
            w_norm * 2.00
            + w_noise * 2.10
            + w_dist * 2.30
            + w_slip * 2.20
        )
        omega_smoothing = (
            w_norm * 0.950
            + w_noise * 0.965
            + w_dist * 0.945
            + w_slip * 0.960
        )
        k_v = (
            w_norm * 0.30
            + w_noise * 0.30
            + w_dist * 0.33
            + w_slip * 0.35
        )

        params = self.BASE_PARAMS.copy()
        params.update(
            {
                "phi": phi,
                "k_omega": k_omega,
                "lambda_y": lambda_y,
                "lambda_x": 2.0 + 0.2 * w_dist + 0.2 * w_slip,
                "lambda_theta": 1.0 + 0.05 * w_dist - 0.05 * w_noise,
                "k_v": k_v,
                "omega_smoothing": omega_smoothing,
            }
        )
        return params
