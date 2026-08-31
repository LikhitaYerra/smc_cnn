import math
from dataclasses import dataclass


@dataclass
class TrackingError:
    ex: float
    ey: float
    etheta: float
    distance_error: float


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


def compute_tracking_error(
    x: float,
    y: float,
    theta: float,
    x_d: float,
    y_d: float,
    theta_d: float,
) -> TrackingError:
    ex = x_d - x
    ey = y_d - y
    etheta = normalize_angle(theta_d - theta)

    distance_error = math.sqrt(ex**2 + ey**2)

    return TrackingError(
        ex=ex,
        ey=ey,
        etheta=etheta,
        distance_error=distance_error,
    )