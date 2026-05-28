import numpy as np


class SensorNoise:
    def __init__(
        self,
        position_std: float = 0.01,
        theta_std: float = 0.005,
        seed: int | None = 42,
    ):
        self.position_std = position_std
        self.theta_std = theta_std
        self.rng = np.random.default_rng(seed)

    def apply(self, x: float, y: float, theta: float):
        noisy_x = x + self.rng.normal(0.0, self.position_std)
        noisy_y = y + self.rng.normal(0.0, self.position_std)
        noisy_theta = theta + self.rng.normal(0.0, self.theta_std)

        return noisy_x, noisy_y, noisy_theta