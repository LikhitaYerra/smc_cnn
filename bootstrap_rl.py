#!/usr/bin/env python3
"""Bootstrap RL model for presentation demos."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.rl.rl_adapter import ensure_rl_model, RLParameterAdapter


def main():
    print("Bootstrapping RL model for presentation...")
    path = RLParameterAdapter.DEFAULT_MODEL_PATH

    if os.path.exists(path):
        adapter = RLParameterAdapter()
        print(f"✓ Model already exists at {path} (trained={adapter.is_trained})")
        return

    success = ensure_rl_model(path)
    if success:
        print(f"✓ Model saved to {path}")
    else:
        print("✗ Bootstrap failed — RL mode will use heuristic policy")


if __name__ == "__main__":
    main()
