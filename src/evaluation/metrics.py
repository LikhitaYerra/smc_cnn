import numpy as np
import pandas as pd


def compute_tracking_metrics(df: pd.DataFrame) -> dict:
    error = df["tracking_error"].to_numpy()

    return {
        "mean_tracking_error": float(np.mean(error)),
        "rmse_tracking_error": float(np.sqrt(np.mean(error**2))),
        "max_tracking_error": float(np.max(error)),
        "final_tracking_error": float(error[-1]),
    }


def compute_control_metrics(df: pd.DataFrame) -> dict:
    v = df["v"].to_numpy()
    omega = df["omega"].to_numpy()

    control_effort = np.sum(v**2 + omega**2)

    return {
        "mean_abs_v": float(np.mean(np.abs(v))),
        "mean_abs_omega": float(np.mean(np.abs(omega))),
        "max_abs_omega": float(np.max(np.abs(omega))),
        "control_effort": float(control_effort),
    }


def compute_chattering_index(df: pd.DataFrame) -> dict:
    omega = df["omega"].to_numpy()

    omega_diff = np.diff(omega)
    chattering_index = np.sum(np.abs(omega_diff))

    return {
        "chattering_index": float(chattering_index),
    }


def compute_settling_time(
    df: pd.DataFrame,
    threshold: float = 0.02,
    hold_time: float = 1.0,
) -> dict:
    time = df["time"].to_numpy()
    error = df["tracking_error"].to_numpy()

    dt = time[1] - time[0]
    hold_steps = int(hold_time / dt)

    settling_time = None

    for i in range(len(error) - hold_steps):
        window = error[i : i + hold_steps]
        if np.all(window < threshold):
            settling_time = time[i]
            break

    return {
        "settling_time": float(settling_time) if settling_time is not None else None,
        "settling_threshold": threshold,
    }


def compute_all_metrics(df: pd.DataFrame) -> dict:
    metrics = {}

    metrics.update(compute_tracking_metrics(df))
    metrics.update(compute_control_metrics(df))
    metrics.update(compute_chattering_index(df))
    metrics.update(compute_settling_time(df))

    return metrics