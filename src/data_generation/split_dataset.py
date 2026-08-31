import os
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def split_dataset(
    metadata_path: str = "data/generated/cnn_dataset/metadata.csv",
    output_dir: str = "data/generated/cnn_dataset",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    random_state: int = 42,
):
    if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
        raise ValueError("train_ratio + val_ratio + test_ratio must equal 1.0")

    metadata = pd.read_csv(metadata_path)

    train_df, temp_df = train_test_split(
        metadata,
        train_size=train_ratio,
        stratify=metadata["label"],
        random_state=random_state,
        shuffle=True,
    )

    relative_test_ratio = test_ratio / (val_ratio + test_ratio)

    val_df, test_df = train_test_split(
        temp_df,
        test_size=relative_test_ratio,
        stratify=temp_df["label"],
        random_state=random_state,
        shuffle=True,
    )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    train_path = output_path / "train_metadata.csv"
    val_path = output_path / "val_metadata.csv"
    test_path = output_path / "test_metadata.csv"

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print("Dataset split completed.")
    print(f"Train samples: {len(train_df)}")
    print(f"Validation samples: {len(val_df)}")
    print(f"Test samples: {len(test_df)}")
    print()
    print("Class distribution:")
    print("Train:")
    print(train_df["scenario"].value_counts().sort_index())
    print()
    print("Validation:")
    print(val_df["scenario"].value_counts().sort_index())
    print()
    print("Test:")
    print(test_df["scenario"].value_counts().sort_index())
    print()
    print(f"Saved: {train_path}")
    print(f"Saved: {val_path}")
    print(f"Saved: {test_path}")


def main():
    split_dataset()


if __name__ == "__main__":
    main()