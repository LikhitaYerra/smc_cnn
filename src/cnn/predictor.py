import os
import sys

import numpy as np
import torch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.cnn.cnn_model import EnvironmentCNN
from src.data_generation.labels import LABEL_TO_SCENARIO


class CNNEnvironmentPredictor:
    def __init__(
        self,
        model_path: str = "models/cnn_environment_classifier.pt",
        device: str | None = None,
    ):
        self.device = self._get_device(device)
        self.model = self._load_model(model_path)
        self.model.eval()

    def _get_device(self, device: str | None):
        if device is not None:
            return torch.device(device)

        if torch.backends.mps.is_available():
            return torch.device("mps")

        if torch.cuda.is_available():
            return torch.device("cuda")

        return torch.device("cpu")

    def _load_model(self, model_path: str):
        checkpoint = torch.load(model_path, map_location=self.device)

        model = EnvironmentCNN(
            num_classes=checkpoint.get("num_classes", 5)
        )

        model.load_state_dict(checkpoint["model_state_dict"])
        model.to(self.device)

        return model

    def predict(self, env_map: np.ndarray):
        env_map = env_map.astype(np.float32)

        if env_map.ndim == 2:
            env_map = np.expand_dims(env_map, axis=0)

        if env_map.ndim == 3:
            env_map = np.expand_dims(env_map, axis=0)

        x = torch.tensor(env_map, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            outputs = self.model(x)
            probabilities = torch.softmax(outputs, dim=1)
            predicted_label = int(probabilities.argmax(dim=1).item())
            confidence = float(probabilities.max().item())

        scenario = LABEL_TO_SCENARIO[predicted_label]

        return {
            "label": predicted_label,
            "scenario": scenario,
            "confidence": confidence,
            "probabilities": probabilities.cpu().numpy().flatten().tolist(),
        }