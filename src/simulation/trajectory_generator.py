import numpy as np


def generate_straight_trajectory(total_time: float, dt: float, speed: float = 0.3):
    t = np.arange(0.0, total_time, dt)

    x_d = speed * t
    y_d = np.zeros_like(t)
    theta_d = np.zeros_like(t)

    return t, x_d, y_d, theta_d


def generate_circular_trajectory(
    total_time: float,
    dt: float,
    radius: float = 2.0,
    angular_speed: float = 0.2,
):
    t = np.arange(0.0, total_time, dt)

    x_d = radius * np.cos(angular_speed * t)
    y_d = radius * np.sin(angular_speed * t)

    dx = -radius * angular_speed * np.sin(angular_speed * t)
    dy = radius * angular_speed * np.cos(angular_speed * t)

    theta_d = np.arctan2(dy, dx)

    return t, x_d, y_d, theta_d


def generate_s_trajectory(
    total_time: float,
    dt: float,
    speed: float = 0.3,
    amplitude: float = 1.0,
    frequency: float = 0.5,
):
    t = np.arange(0.0, total_time, dt)

    x_d = speed * t
    y_d = amplitude * np.sin(frequency * t)

    dx = np.ones_like(t) * speed
    dy = amplitude * frequency * np.cos(frequency * t)

    theta_d = np.arctan2(dy, dx)

    return t, x_d, y_d, theta_d