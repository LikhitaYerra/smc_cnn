from dataclasses import dataclass


@dataclass
class RobotState:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0
    v: float = 0.0
    omega: float = 0.0

    def as_tuple(self):
        return self.x, self.y, self.theta, self.v, self.omega

    def copy(self):
        return RobotState(
            x=self.x,
            y=self.y,
            theta=self.theta,
            v=self.v,
            omega=self.omega,
        )