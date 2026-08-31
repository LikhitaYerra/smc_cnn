import numpy as np


class EnvironmentMapGenerator:
    def __init__(
        self,
        map_size: int = 64,
        seed: int | None = None,
    ):
        self.map_size = map_size
        self.rng = np.random.default_rng(seed)

    def generate(self, scenario: str) -> np.ndarray:
        if scenario == "normal":
            return self._generate_normal()

        if scenario == "noise":
            return self._generate_noise()

        if scenario == "disturbance":
            return self._generate_disturbance()

        if scenario == "slip":
            return self._generate_slip()

        if scenario == "combined":
            return self._generate_combined()

        raise ValueError(f"Unknown scenario: {scenario}")

    def _base_map(self) -> np.ndarray:
        env_map = np.zeros((self.map_size, self.map_size), dtype=np.float32)

        center = self.map_size // 2
        env_map[center - 1:center + 1, :] = 0.3

        return env_map

    def _generate_normal(self) -> np.ndarray:
        env_map = self._base_map()
        return env_map

    def _generate_noise(self) -> np.ndarray:
        env_map = self._base_map()

        noise = self.rng.normal(
            loc=0.0,
            scale=0.15,
            size=(self.map_size, self.map_size),
        ).astype(np.float32)

        env_map = env_map + noise
        env_map = np.clip(env_map, 0.0, 1.0)

        return env_map

    def _generate_disturbance(self) -> np.ndarray:
        env_map = self._base_map()

        marker_size = self.rng.integers(5, 10)
        x = self.rng.integers(10, self.map_size - 10)
        y = self.rng.integers(10, self.map_size - 10)

        env_map[
            y:y + marker_size,
            x:x + marker_size,
        ] = 0.8

        return env_map

    def _generate_slip(self) -> np.ndarray:
        env_map = self._base_map()

        band_y = self.rng.integers(
            self.map_size // 3,
            2 * self.map_size // 3,
        )

        band_height = self.rng.integers(6, 12)

        env_map[
            band_y:band_y + band_height,
            :
        ] = 0.6

        return env_map

    def _generate_combined(self) -> np.ndarray:
        env_map = self._base_map()

        noise = self.rng.normal(
            loc=0.0,
            scale=0.15,
            size=(self.map_size, self.map_size),
        ).astype(np.float32)

        env_map = env_map + noise

        band_y = self.rng.integers(
            self.map_size // 3,
            2 * self.map_size // 3,
        )
        band_height = self.rng.integers(6, 12)

        env_map[
            band_y:band_y + band_height,
            :
        ] = 0.6

        marker_size = self.rng.integers(5, 10)
        x = self.rng.integers(10, self.map_size - 10)
        y = self.rng.integers(10, self.map_size - 10)

        env_map[
            y:y + marker_size,
            x:x + marker_size,
        ] = 0.9

        env_map = np.clip(env_map, 0.0, 1.0)

        return env_map