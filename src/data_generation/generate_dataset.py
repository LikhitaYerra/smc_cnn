import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.data_generation.environment_generator import EnvironmentMapGenerator
from src.data_generation.labels import SCENARIO_LABELS


def save_map_image(env_map: np.ndarray, save_path: Path):
    plt.figure(figsize=(3, 3))
    plt.imshow(env_map, cmap="gray", vmin=0.0, vmax=1.0)
    plt.axis("off")
    plt.savefig(save_path, dpi=100, bbox_inches="tight", pad_inches=0)
    plt.close()


def generate_dataset(
    samples_per_class: int = 300,
    map_size: int = 64,
    output_dir: str = "data/generated/cnn_dataset",
):
    output_path = Path(output_dir)
    images_path = output_path / "images"
    arrays_path = output_path / "arrays"

    images_path.mkdir(parents=True, exist_ok=True)
    arrays_path.mkdir(parents=True, exist_ok=True)

    generator = EnvironmentMapGenerator(map_size=map_size, seed=42)

    rows = []

    for scenario_name, label in SCENARIO_LABELS.items():
        scenario_image_dir = images_path / scenario_name
        scenario_array_dir = arrays_path / scenario_name

        scenario_image_dir.mkdir(parents=True, exist_ok=True)
        scenario_array_dir.mkdir(parents=True, exist_ok=True)

        for i in range(samples_per_class):
            env_map = generator.generate(scenario_name)

            file_stem = f"{scenario_name}_{i:04d}"

            image_path = scenario_image_dir / f"{file_stem}.png"
            array_path = scenario_array_dir / f"{file_stem}.npy"

            save_map_image(env_map, image_path)
            np.save(array_path, env_map)

            rows.append(
                {
                    "scenario": scenario_name,
                    "label": label,
                    "image_path": str(image_path),
                    "array_path": str(array_path),
                }
            )

    metadata = pd.DataFrame(rows)

    metadata_path = output_path / "metadata.csv"
    metadata.to_csv(metadata_path, index=False)

    print(f"Dataset generated successfully.")
    print(f"Total samples: {len(metadata)}")
    print(f"Metadata saved to: {metadata_path}")

    return metadata


def main():
    generate_dataset(
        samples_per_class=300,
        map_size=64,
        output_dir="data/generated/cnn_dataset",
    )


if __name__ == "__main__":
    main()