import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def main():
    metadata_path = "data/generated/cnn_dataset/metadata.csv"
    metadata = pd.read_csv(metadata_path)

    scenarios = metadata["scenario"].unique()

    plt.figure(figsize=(12, 3))

    for index, scenario in enumerate(scenarios):
        row = metadata[metadata["scenario"] == scenario].iloc[0]
        env_map = np.load(row["array_path"])

        plt.subplot(1, len(scenarios), index + 1)
        plt.imshow(env_map, cmap="gray", vmin=0.0, vmax=1.0)
        plt.title(scenario)
        plt.axis("off")

    os.makedirs("results/plots/cnn_dataset", exist_ok=True)
    save_path = "results/plots/cnn_dataset/dataset_preview.png"
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved dataset preview to: {save_path}")


if __name__ == "__main__":
    main()