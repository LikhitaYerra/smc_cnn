"""Train a PPO policy for discrete SMC parameter-preset selection."""

from __future__ import annotations

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

from src.rl.smc_parameter_env import SMCParameterSelectionEnv


def main(total_timesteps: int = 80_000):
    env = make_vec_env(
        lambda: SMCParameterSelectionEnv(randomize_scenario=True, seed=42),
        n_envs=1,
    )

    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=256,
        gamma=0.99,
        verbose=1,
        seed=42,
    )

    model.learn(total_timesteps=total_timesteps)

    os.makedirs("models", exist_ok=True)
    zip_path = "models/rl_smc_parameter_policy.zip"
    state_path = "models/rl_smc_parameter_policy_state.pt"
    model.save(zip_path)
    import torch

    torch.save(model.policy.state_dict(), state_path)
    print(f"Saved RL policy to: {zip_path}")
    print(f"Saved RL policy state dict to: {state_path}")


if __name__ == "__main__":
    main()
