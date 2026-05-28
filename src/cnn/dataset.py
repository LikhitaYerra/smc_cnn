import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset


class EnvironmentMapDataset(Dataset):
    def __init__(self, metadata_path: str):
        self.metadata = pd.read_csv(metadata_path)

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, index: int):
        row = self.metadata.iloc[index]

        array_path = row["array_path"]
        label = int(row["label"])

        env_map = np.load(array_path).astype(np.float32)

        # Shape before: (64, 64)
        # Shape after:  (1, 64, 64)
        env_map = np.expand_dims(env_map, axis=0)

        x = torch.tensor(env_map, dtype=torch.float32)
        y = torch.tensor(label, dtype=torch.long)

        return x, y