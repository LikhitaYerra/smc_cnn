"""More realistic occupancy-map generator with walls, clutter, and subtle class cues."""

from __future__ import annotations

import numpy as np


class RealisticEnvironmentMapGenerator:
    def __init__(self, map_size: int = 64, seed: int | None = None):
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

    def _empty_grid(self) -> np.ndarray:
        grid = np.zeros((self.map_size, self.map_size), dtype=np.float32)
        grid[0, :] = 1.0
        grid[-1, :] = 1.0
        grid[:, 0] = 1.0
        grid[:, -1] = 1.0
        return grid

    def _add_random_walls(self, grid: np.ndarray, count: int = 4):
        for _ in range(count):
            w = self.rng.integers(4, 10)
            h = self.rng.integers(4, 10)
            x = self.rng.integers(2, self.map_size - w - 2)
            y = self.rng.integers(2, self.map_size - h - 2)
            grid[y : y + h, x : x + w] = 0.85

    def _add_corridor(self, grid: np.ndarray):
        center = self.map_size // 2
        grid[center - 2 : center + 2, 4 : self.map_size - 4] = 0.25

    def _generate_normal(self) -> np.ndarray:
        grid = self._empty_grid()
        self._add_random_walls(grid, count=self.rng.integers(3, 6))
        self._add_corridor(grid)
        return np.clip(grid, 0.0, 1.0)

    def _generate_noise(self) -> np.ndarray:
        grid = self._generate_normal()
        speckle = self.rng.random((self.map_size, self.map_size)) < 0.08
        grid[speckle] = np.minimum(1.0, grid[speckle] + 0.35)
        grid += self.rng.normal(0.0, 0.05, grid.shape).astype(np.float32)
        return np.clip(grid, 0.0, 1.0)

    def _generate_disturbance(self) -> np.ndarray:
        grid = self._generate_normal()
        blob_w = self.rng.integers(6, 12)
        blob_h = self.rng.integers(6, 12)
        x = self.rng.integers(8, self.map_size - blob_w - 8)
        y = self.rng.integers(8, self.map_size - blob_h - 8)
        grid[y : y + blob_h, x : x + blob_w] = 0.95
        return grid

    def _generate_slip(self) -> np.ndarray:
        grid = self._generate_normal()
        band_y = self.rng.integers(self.map_size // 4, 3 * self.map_size // 4)
        band_h = self.rng.integers(5, 10)
        grid[band_y : band_y + band_h, 4 : self.map_size - 4] = 0.55
        texture = self.rng.normal(0.0, 0.03, (band_h, self.map_size - 8))
        grid[band_y : band_y + band_h, 4 : self.map_size - 4] += texture
        return np.clip(grid, 0.0, 1.0)

    def _generate_combined(self) -> np.ndarray:
        grid = self._generate_normal()
        speckle = self.rng.random((self.map_size, self.map_size)) < 0.07
        grid[speckle] = np.minimum(1.0, grid[speckle] + 0.30)
        band_y = self.rng.integers(self.map_size // 4, 3 * self.map_size // 4)
        band_h = self.rng.integers(5, 10)
        grid[band_y : band_y + band_h, 4 : self.map_size - 4] = 0.58
        blob_w = self.rng.integers(5, 9)
        blob_h = self.rng.integers(5, 9)
        x = self.rng.integers(8, self.map_size - blob_w - 8)
        y = self.rng.integers(8, self.map_size - blob_h - 8)
        grid[y : y + blob_h, x : x + blob_w] = 0.95
        grid += self.rng.normal(0.0, 0.04, grid.shape).astype(np.float32)
        return np.clip(grid, 0.0, 1.0)
