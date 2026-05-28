import os
import sys

import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.cnn.cnn_model import EnvironmentCNN


def main():
    model = EnvironmentCNN(num_classes=5)

    dummy_input = torch.randn(16, 1, 64, 64)

    output = model(dummy_input)

    print(model)
    print()
    print(f"Input shape: {dummy_input.shape}")
    print(f"Output shape: {output.shape}")
    print(f"Predicted class shape: {output.argmax(dim=1).shape}")
    print(f"Example predicted classes: {output.argmax(dim=1).tolist()}")


if __name__ == "__main__":
    main()