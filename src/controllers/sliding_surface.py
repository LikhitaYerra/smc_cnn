from dataclasses import dataclass


@dataclass
class SlidingSurface:
    sx: float
    sy: float
    stheta: float


class SlidingSurfaceCalculator:
    def __init__(self, lambda_x: float = 2.0, lambda_y: float = 2.0, lambda_theta: float = 2.0):
        self.lambda_x = lambda_x
        self.lambda_y = lambda_y
        self.lambda_theta = lambda_theta

        self.previous_ex = 0.0
        self.previous_ey = 0.0
        self.previous_etheta = 0.0
        self.first_call = True

    def compute(
        self,
        ex: float,
        ey: float,
        etheta: float,
        dt: float,
    ) -> SlidingSurface:
        if self.first_call:
            ex_dot = 0.0
            ey_dot = 0.0
            etheta_dot = 0.0
            self.first_call = False
        else:
            ex_dot = (ex - self.previous_ex) / dt
            ey_dot = (ey - self.previous_ey) / dt
            etheta_dot = (etheta - self.previous_etheta) / dt

        sx = ex_dot + self.lambda_x * ex
        sy = ey_dot + self.lambda_y * ey
        stheta = etheta_dot + self.lambda_theta * etheta

        self.previous_ex = ex
        self.previous_ey = ey
        self.previous_etheta = etheta

        return SlidingSurface(
            sx=sx,
            sy=sy,
            stheta=stheta,
        )

    def reset(self):
        self.previous_ex = 0.0
        self.previous_ey = 0.0
        self.previous_etheta = 0.0
        self.first_call = True