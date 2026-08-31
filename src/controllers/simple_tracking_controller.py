import math


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


class SimpleTrackingController:
    def __init__(
        self,
        linear_speed: float = 0.3,
        k_y: float = 1.5,
        k_theta: float = 2.0,
        max_omega: float = 2.0,
    ):
        self.linear_speed = linear_speed
        self.k_y = k_y
        self.k_theta = k_theta
        self.max_omega = max_omega

    def compute_control(
        self,
        x: float,
        y: float,
        theta: float,
        x_d: float,
        y_d: float,
        theta_d: float,
    ):
        ex = x_d - x
        ey = y_d - y

        error_heading = math.atan2(ey, ex)
        heading_error = normalize_angle(error_heading - theta)
        trajectory_heading_error = normalize_angle(theta_d - theta)

        omega = self.k_y * heading_error + self.k_theta * trajectory_heading_error
        omega = max(min(omega, self.max_omega), -self.max_omega)

        v = self.linear_speed

        return v, omega