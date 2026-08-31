#!/usr/bin/env python3
"""Bootstrap CNN and RL models for presentation (fast, ~5-10 min)."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))


def bootstrap_cnn(samples_per_class: int = 150, epochs: int = 15):
    from src.data_generation.generate_dataset import generate_dataset
    from src.data_generation.split_dataset import split_dataset

    print("\n=== Step 1: Generate CNN dataset ===")
    generate_dataset(samples_per_class=samples_per_class, output_dir="data/generated/cnn_dataset")

    print("\n=== Step 2: Split dataset ===")
    split_dataset()

    print("\n=== Step 3: Train CNN ===")
    import json
    from pathlib import Path

    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader

    from src.cnn.cnn_model import EnvironmentCNN
    from src.cnn.dataset import EnvironmentMapDataset
    from src.cnn.train_cnn import evaluate, get_device, train_one_epoch

    device = get_device()
    print(f"Device: {device}")

    train_loader = DataLoader(
        EnvironmentMapDataset("data/generated/cnn_dataset/train_metadata.csv"),
        batch_size=32, shuffle=True, num_workers=0,
    )
    val_loader = DataLoader(
        EnvironmentMapDataset("data/generated/cnn_dataset/val_metadata.csv"),
        batch_size=32, shuffle=False, num_workers=0,
    )

    model = EnvironmentCNN(num_classes=5).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    os.makedirs("models", exist_ok=True)
    best_acc = 0.0
    best_path = "models/cnn_environment_classifier.pt"

    for epoch in range(1, epochs + 1):
        tl, ta = train_one_epoch(model, train_loader, criterion, optimizer, device)
        vl, va = evaluate(model, val_loader, criterion, device)
        print(f"  Epoch {epoch:02d}/{epochs}  train_acc={ta:.3f}  val_acc={va:.3f}")
        if va > best_acc:
            best_acc = va
            torch.save({"model_state_dict": model.state_dict(), "num_classes": 5, "best_val_accuracy": va, "epoch": epoch}, best_path)

    print(f"CNN saved to {best_path}  (val_acc={best_acc:.3f})")
    return best_acc


def bootstrap_rl(iterations: int = 25):
    print("\n=== Step 4: Train RL agent ===")
    from src.rl.train_rl import train
    train(n_iterations=iterations, rollout_steps=1024, save_path="models/rl_smc_agent.pt")
    print("RL agent saved to models/rl_smc_agent.pt")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnn-samples", type=int, default=150)
    parser.add_argument("--cnn-epochs", type=int, default=15)
    parser.add_argument("--rl-iters", type=int, default=25)
    parser.add_argument("--skip-rl", action="store_true")
    parser.add_argument("--skip-cnn", action="store_true")
    args = parser.parse_args()

    print("=" * 50)
    print("  Bootstrapping AI models for presentation")
    print("=" * 50)

    if not args.skip_cnn:
        bootstrap_cnn(samples_per_class=args.cnn_samples, epochs=args.cnn_epochs)
    if not args.skip_rl:
        bootstrap_rl(iterations=args.rl_iters)

    print("\n" + "=" * 50)
    print("  All models ready!")
    print("  Restart server: python run_digital_twin.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
