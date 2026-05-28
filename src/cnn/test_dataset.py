import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from torch.utils.data import DataLoader

from src.cnn.dataset import EnvironmentMapDataset


def main():
    train_dataset = EnvironmentMapDataset(
        metadata_path="data/generated/cnn_dataset/train_metadata.csv"
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=16,
        shuffle=True,
    )

    print(f"Dataset size: {len(train_dataset)}")

    x_batch, y_batch = next(iter(train_loader))

    print(f"x_batch shape: {x_batch.shape}")
    print(f"y_batch shape: {y_batch.shape}")
    print(f"labels: {y_batch.tolist()}")


if __name__ == "__main__":
    main()