"""Reward functions for RL-based SMC parameter adaptation."""

import numpy as np


def compute_step_reward(
    tracking_error: float,
    v: float,
    omega: float,
    prev_omega: float,
    alpha: float = 10.0,
    beta: float = 0.05,
    gamma: float = 0.1,
) -> float:
    """Compute per-step reward for the RL agent."""
    error_penalty = -alpha * (tracking_error**2)
    effort_penalty = -beta * (v**2 + omega**2)
    chattering_penalty = -gamma * abs(omega - prev_omega)
    return float(error_penalty + effort_penalty + chattering_penalty)


def compute_episode_reward(
    errors: np.ndarray,
    v_commands: np.ndarray,
    omega_commands: np.ndarray,
    alpha: float = 10.0,
    beta: float = 0.05,
    gamma: float = 0.1,
) -> float:
    """Compute total episode reward from logged trajectories."""
    error_penalty = -alpha * np.sum(errors**2)
    effort_penalty = -beta * np.sum(v_commands**2 + omega_commands**2)
    chattering_penalty = -gamma * np.sum(np.abs(np.diff(omega_commands)))
    return float(error_penalty + effort_penalty + chattering_penalty)
