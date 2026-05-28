from pathlib import Path
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r") as file:
        return yaml.safe_load(file)
