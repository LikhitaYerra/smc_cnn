"""Train and evaluate CNN on the realistic occupancy-map dataset."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, classification_report
from torch.utils.data import DataLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.cnn.cnn_model import EnvironmentCNN
from src.cnn.dataset import EnvironmentMapDataset
from src.data_generation.labels import LABEL_TO_SCENARIO
from src.data_generation.split_dataset import split_dataset


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def main():
    dataset_dir = "data/generated/cnn_dataset_realistic"
    metadata_path = f"{dataset_dir}/metadata.csv"

    if not Path(metadata_path).exists():
        raise FileNotFoundError("Run generate_realistic_dataset.py first.")

    split_dataset(metadata_path=metadata_path, output_dir=dataset_dir)

    device = get_device()
    train_loader = DataLoader(
        EnvironmentMapDataset(f"{dataset_dir}/train_metadata.csv"),
        batch_size=32,
        shuffle=True,
    )
    val_loader = DataLoader(
        EnvironmentMapDataset(f"{dataset_dir}/val_metadata.csv"),
        batch_size=32,
        shuffle=False,
    )
    test_loader = DataLoader(
        EnvironmentMapDataset(f"{dataset_dir}/test_metadata.csv"),
        batch_size=32,
        shuffle=False,
    )

    model = EnvironmentCNN(num_classes=5).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    history = {"train_loss": [], "train_accuracy": [], "val_loss": [], "val_accuracy": []}
    best_val_acc = 0.0

    for epoch in range(20):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        for x_batch, y_batch in train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            outputs = model(x_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * y_batch.size(0)
            train_correct += (outputs.argmax(1) == y_batch).sum().item()
            train_total += y_batch.size(0)

        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for x_batch, y_batch in val_loader:
                x_batch, y_batch = x_batch.to(device), y_batch.to(device)
                outputs = model(x_batch)
                loss = criterion(outputs, y_batch)
                val_loss += loss.item() * y_batch.size(0)
                val_correct += (outputs.argmax(1) == y_batch).sum().item()
                val_total += y_batch.size(0)

        train_acc = train_correct / train_total
        val_acc = val_correct / val_total
        history["train_loss"].append(train_loss / train_total)
        history["train_accuracy"].append(train_acc)
        history["val_loss"].append(val_loss / val_total)
        history["val_accuracy"].append(val_acc)
        print(f"Epoch {epoch + 1}: train_acc={train_acc:.4f}, val_acc={val_acc:.4f}")

        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "num_classes": 5,
                    "best_val_accuracy": best_val_acc,
                    "epoch": epoch + 1,
                },
                "models/cnn_realistic_environment_classifier.pt",
            )

    model.eval()
    y_true, y_pred = [], []
    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            outputs = model(x_batch.to(device))
            preds = outputs.argmax(dim=1).cpu().numpy().tolist()
            y_pred.extend(preds)
            y_true.extend(y_batch.numpy().tolist())

    labels = sorted(LABEL_TO_SCENARIO.keys())
    class_names = [LABEL_TO_SCENARIO[label] for label in labels]
    report = classification_report(y_true, y_pred, target_names=class_names, digits=4)
    acc = accuracy_score(y_true, y_pred)

    out_dir = Path("results/cnn_realistic")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "test_classification_report.txt", "w") as f:
        f.write(report)
    with open(out_dir / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

    summary = pd.DataFrame(
        [{"dataset": "realistic", "test_accuracy": acc, "best_val_accuracy": best_val_acc}]
    )
    summary.to_csv(out_dir / "summary.csv", index=False)
    print(f"Realistic CNN test accuracy: {acc:.4f}")
    print(report)


if __name__ == "__main__":
    main()
