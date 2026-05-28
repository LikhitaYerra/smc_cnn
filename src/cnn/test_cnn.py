import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, ConfusionMatrixDisplay
from torch.utils.data import DataLoader

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.cnn.cnn_model import EnvironmentCNN
from src.cnn.dataset import EnvironmentMapDataset
from src.data_generation.labels import LABEL_TO_SCENARIO


def get_device():
    if torch.backends.mps.is_available():
        return torch.device("mps")

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def load_model(model_path: str, device):
    checkpoint = torch.load(model_path, map_location=device)

    model = EnvironmentCNN(num_classes=checkpoint.get("num_classes", 5))
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    return model, checkpoint


def evaluate_model(model, dataloader, device):
    y_true = []
    y_pred = []

    with torch.no_grad():
        for x_batch, y_batch in dataloader:
            x_batch = x_batch.to(device)

            outputs = model(x_batch)
            predictions = outputs.argmax(dim=1).cpu().numpy().tolist()

            y_pred.extend(predictions)
            y_true.extend(y_batch.numpy().tolist())

    return y_true, y_pred


def main():
    test_metadata = "data/generated/cnn_dataset/test_metadata.csv"
    model_path = "models/cnn_environment_classifier.pt"

    output_dir = Path("results/cnn")
    plot_dir = Path("results/plots/cnn")
    output_dir.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)

    device = get_device()
    print(f"Using device: {device}")

    test_dataset = EnvironmentMapDataset(test_metadata)
    test_loader = DataLoader(
        test_dataset,
        batch_size=32,
        shuffle=False,
        num_workers=0,
    )

    model, checkpoint = load_model(model_path, device)

    print(f"Loaded model from: {model_path}")
    print(f"Best validation accuracy: {checkpoint.get('best_val_accuracy')}")
    print(f"Saved at epoch: {checkpoint.get('epoch')}")

    y_true, y_pred = evaluate_model(model, test_loader, device)

    labels = sorted(LABEL_TO_SCENARIO.keys())
    class_names = [LABEL_TO_SCENARIO[label] for label in labels]

    accuracy = accuracy_score(y_true, y_pred)

    report_dict = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    report_text = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=class_names,
        zero_division=0,
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels,
    )

    metrics_path = output_dir / "test_classification_report.csv"
    pd.DataFrame(report_dict).transpose().to_csv(metrics_path)

    text_report_path = output_dir / "test_classification_report.txt"
    with open(text_report_path, "w") as f:
        f.write(report_text)

    cm_path = output_dir / "test_confusion_matrix.csv"
    pd.DataFrame(cm, index=class_names, columns=class_names).to_csv(cm_path)

    plt.figure(figsize=(7, 7))
    display = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=class_names,
    )
    display.plot(values_format="d", cmap="Blues")
    plt.title(f"CNN Test Confusion Matrix - Accuracy: {accuracy:.4f}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    confusion_plot_path = plot_dir / "cnn_test_confusion_matrix.png"
    plt.savefig(confusion_plot_path, dpi=300, bbox_inches="tight")
    plt.show()

    print()
    print(f"Test accuracy: {accuracy:.4f}")
    print()
    print(report_text)
    print(f"Saved report CSV to: {metrics_path}")
    print(f"Saved report TXT to: {text_report_path}")
    print(f"Saved confusion matrix CSV to: {cm_path}")
    print(f"Saved confusion matrix plot to: {confusion_plot_path}")


if __name__ == "__main__":
    main()