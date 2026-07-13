"""Preview figure for the realistic CNN dataset."""

import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.data_generation.realistic_map_generator import RealisticEnvironmentMapGenerator


def main():
    generator = RealisticEnvironmentMapGenerator(map_size=64, seed=42)
    scenarios = ["normal", "noise", "disturbance", "slip", "combined"]

    fig, axes = plt.subplots(1, 5, figsize=(12, 2.5))
    for ax, scenario in zip(axes, scenarios):
        ax.imshow(generator.generate(scenario), cmap="gray", vmin=0, vmax=1)
        ax.set_title(scenario.capitalize())
        ax.axis("off")

    fig.suptitle("Realistic Occupancy Maps (walls + clutter)", fontsize=12)
    out_dir = Path("results/plots/cnn_dataset_realistic")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "realistic_dataset_preview.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
