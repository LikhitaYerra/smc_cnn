import math

from src.controllers.tracking_error import compute_tracking_error
from src.controllers.sliding_surface import SlidingSurfaceCalculator
from src.controllers.switching_functions import apply_switching


def normalize_angle(angle: float) -> float:
    return math.atan2(math.sin(angle), math.cos(angle))


class SlidingModeController:
    def __init__(
        self,
        lambda_x: float = 2.0,
        lambda_y: float = 2.0,
        lambda_theta: float = 1.0,
        k_v: float = 0.3,
        k_omega: float = 0.8,
        phi: float = 0.5,
        max_v: float = 0.6,
        max_omega: float = 1.5,
        switching_type: str = "tanh",
        omega_smoothing: float = 0.95,
        position_dead_zone: float = 0.01,
        theta_dead_zone: float = 0.01,
    ):
        self.lambda_x = lambda_x
        self.lambda_y = lambda_y
        self.lambda_theta = lambda_theta

        self.k_v = k_v
        self.k_omega = k_omega
        self.phi = phi

        self.max_v = max_v
        self.max_omega = max_omega
        self.switching_type = switching_type

        self.omega_smoothing = omega_smoothing
        self.previous_omega = 0.0

        self.position_dead_zone = position_dead_zone
        self.theta_dead_zone = theta_dead_zone

        self.surface_calculator = SlidingSurfaceCalculator(
            lambda_x=lambda_x,
            lambda_y=lambda_y,
            lambda_theta=lambda_theta,
        )

    def reset(self):
        self.surface_calculator.reset()
        self.previous_omega = 0.0

    def _switch(self, value: float) -> float:
        return apply_switching(
            value=value,
            phi=self.phi,
            switching_type=self.switching_type,
        )

    def compute_control(
        self,
        x: float,
        y: float,
        theta: float,
        x_d: float,
        y_d: float,
        theta_d: float,
        v_d: float,
        dt: float,
    ):
        error = compute_tracking_error(
            x=x,
            y=y,
            theta=theta,
            x_d=x_d,
            y_d=y_d,
            theta_d=theta_d,
        )

        surface = self.surface_calculator.compute(
            ex=error.ex,
            ey=error.ey,
            etheta=error.etheta,
            dt=dt,
        )

        heading_to_target = math.atan2(error.ey, error.ex)
        heading_error = normalize_angle(heading_to_target - theta)

        forward_error = math.cos(theta) * error.ex + math.sin(theta) * error.ey

        if abs(forward_error) < self.position_dead_zone:
            forward_error = 0.0

        if abs(error.ey) < self.position_dead_zone:
            lateral_switch = 0.0
        else:
            lateral_switch = self._switch(surface.sy)

        if abs(error.etheta) < self.theta_dead_zone:
            heading_error = 0.0
            theta_switch = 0.0
        else:
            theta_switch = self._switch(surface.stheta)

        v = v_d + self.k_v * forward_error

        omega_raw = (
            self.k_omega * heading_error
            + self.k_omega * lateral_switch
            + 0.2 * self.k_omega * theta_switch
        )

        omega_raw = max(min(omega_raw, self.max_omega), -self.max_omega)

        omega = (
            self.omega_smoothing * self.previous_omega
            + (1.0 - self.omega_smoothing) * omega_raw
        )

        self.previous_omega = omega

        v = max(min(v, self.max_v), -self.max_v)
        omega = max(min(omega, self.max_omega), -self.max_omega)

        return v, omega, error, surface
