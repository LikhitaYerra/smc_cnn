"""Train PPO agent for adaptive SMC parameter tuning."""

from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import torch
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.rl.agent import PPOAgent
from src.rl.env import SMCParameterEnv


def collect_rollout(env, agent, max_steps: int):
    obs, _ = env.reset()
    observations, actions, rewards, values, log_probs, dones = [], [], [], [], [], []

    for _ in range(max_steps):
        obs_t = torch.FloatTensor(obs).unsqueeze(0)
        with torch.no_grad():
            mu, std, value = agent.policy.forward(obs_t)
            dist = torch.distributions.Normal(mu, std)
            action_t = dist.sample()
            action_t = torch.clamp(action_t, -1.0, 1.0)
            log_prob = dist.log_prob(action_t).sum(dim=-1)

        action = action_t.squeeze(0).numpy()
        next_obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated

        observations.append(obs)
        actions.append(action)
        rewards.append(reward)
        values.append(float(value.item()))
        log_probs.append(float(log_prob.item()))
        dones.append(float(done))

        obs = next_obs
        if done:
            obs, _ = env.reset()

    advantages, returns = agent.compute_gae(rewards, values, dones)
    return {
        "observations": observations,
        "actions": actions,
        "rewards": rewards,
        "values": values,
        "log_probs": log_probs,
        "dones": dones,
        "advantages": advantages,
        "returns": returns,
        "mean_reward": float(np.mean(rewards)),
    }


def train(
    n_iterations: int = 100,
    rollout_steps: int = 2048,
    save_path: str = "models/rl_smc_agent.pt",
    log_dir: str = "results/rl_training",
):
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    env = SMCParameterEnv(episode_steps=500, param_update_interval=50)
    agent = PPOAgent()

    best_reward = -float("inf")
    history = []

    print("Training RL agent for SMC parameter adaptation...")
    print(f"  Iterations: {n_iterations}")
    print(f"  Rollout steps: {rollout_steps}")
    print(f"  Save path: {save_path}")

    for iteration in tqdm(range(n_iterations), desc="RL Training"):
        rollout = collect_rollout(env, agent, rollout_steps)
        agent.update(rollout)

        mean_reward = rollout["mean_reward"]
        history.append(mean_reward)

        if mean_reward > best_reward:
            best_reward = mean_reward
            agent.save(save_path)

        if (iteration + 1) % 10 == 0:
            print(f"  Iter {iteration + 1}: mean_reward={mean_reward:.4f}, best={best_reward:.4f}")

    agent.save(save_path)
    np.save(f"{log_dir}/reward_history.npy", np.array(history))
    print(f"\nTraining complete. Model saved to {save_path}")
    print(f"Best mean reward: {best_reward:.4f}")
    return agent


def main():
    parser = argparse.ArgumentParser(description="Train RL agent for SMC adaptation")
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--rollout-steps", type=int, default=2048)
    parser.add_argument("--save-path", type=str, default="models/rl_smc_agent.pt")
    parser.add_argument("--quick", action="store_true", help="Quick training (20 iterations)")
    args = parser.parse_args()

    iterations = 20 if args.quick else args.iterations
    train(n_iterations=iterations, rollout_steps=args.rollout_steps, save_path=args.save_path)


if __name__ == "__main__":
    main()
