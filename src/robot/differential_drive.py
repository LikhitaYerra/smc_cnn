import math
from src.robot.robot_state import RobotState


class DifferentialDriveRobot:
    def __init__(
        self,
        wheel_base: float = 0.3,
        wheel_radius: float = 0.05,
        initial_state: RobotState | None = None,
    ):
        self.wheel_base = wheel_base
        self.wheel_radius = wheel_radius
        self.state = initial_state if initial_state is not None else RobotState()

    def reset(self, state: RobotState | None = None):
        self.state = state if state is not None else RobotState()

    def set_velocity(self, v: float, omega: float):
        self.state.v = v
        self.state.omega = omega

    def update(self, dt: float):
        x = self.state.x
        y = self.state.y
        theta = self.state.theta
        v = self.state.v
        omega = self.state.omega

        x_new = x + v * math.cos(theta) * dt
        y_new = y + v * math.sin(theta) * dt
        theta_new = theta + omega * dt

        theta_new = self._normalize_angle(theta_new)

        self.state.x = x_new
        self.state.y = y_new
        self.state.theta = theta_new

        return self.state.copy()

    def wheel_speeds_to_velocity(self, left_wheel_speed: float, right_wheel_speed: float):
        v = self.wheel_radius * (right_wheel_speed + left_wheel_speed) / 2.0
        omega = self.wheel_radius * (right_wheel_speed - left_wheel_speed) / self.wheel_base
        return v, omega

    def velocity_to_wheel_speeds(self, v: float, omega: float):
        right_wheel_speed = (v + (omega * self.wheel_base / 2.0)) / self.wheel_radius
        left_wheel_speed = (v - (omega * self.wheel_base / 2.0)) / self.wheel_radius
        return left_wheel_speed, right_wheel_speed

    @staticmethod
    def _normalize_angle(angle: float):
        return math.atan2(math.sin(angle), math.cos(angle))