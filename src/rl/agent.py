"""PPO policy network for SMC parameter adaptation."""

from __future__ import annotations

import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal

from src.rl.parameter_mapper import PARAM_KEYS, action_to_parameters


OBS_DIM = 10
ACTION_DIM = len(PARAM_KEYS)


class PolicyNetwork(nn.Module):
    """Actor-critic network for continuous SMC parameter control."""

    def __init__(self, obs_dim: int = OBS_DIM, action_dim: int = ACTION_DIM, hidden: int = 128):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(obs_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, hidden),
            nn.Tanh(),
        )
        self.mu_head = nn.Linear(hidden, action_dim)
        self.log_std = nn.Parameter(torch.zeros(action_dim))
        self.value_head = nn.Linear(hidden, 1)

    def forward(self, obs: torch.Tensor):
        features = self.shared(obs)
        mu = torch.tanh(self.mu_head(features))
        std = torch.exp(self.log_std).expand_as(mu)
        value = self.value_head(features)
        return mu, std, value.squeeze(-1)

    def get_action(self, obs: np.ndarray, deterministic: bool = False):
        obs_t = torch.FloatTensor(obs).unsqueeze(0)
        with torch.no_grad():
            mu, std, value = self.forward(obs_t)
            if deterministic:
                action = mu
            else:
                dist = Normal(mu, std)
                action = dist.sample()
            action = torch.clamp(action, -1.0, 1.0)
        return action.squeeze(0).numpy(), float(value.item())

    def evaluate_actions(self, obs: torch.Tensor, actions: torch.Tensor):
        mu, std, values = self.forward(obs)
        dist = Normal(mu, std)
        log_probs = dist.log_prob(actions).sum(dim=-1)
        entropy = dist.entropy().sum(dim=-1)
        return log_probs, entropy, values


class PPOAgent:
    """Proximal Policy Optimization agent for SMC parameter tuning."""

    def __init__(
        self,
        lr: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_eps: float = 0.2,
        entropy_coef: float = 0.01,
        value_coef: float = 0.5,
        max_grad_norm: float = 0.5,
    ):
        self.policy = PolicyNetwork()
        self.optimizer = torch.optim.Adam(self.policy.parameters(), lr=lr)
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_eps = clip_eps
        self.entropy_coef = entropy_coef
        self.value_coef = value_coef
        self.max_grad_norm = max_grad_norm

    def select_action(self, obs: np.ndarray, deterministic: bool = False):
        action, value = self.policy.get_action(obs, deterministic=deterministic)
        params = action_to_parameters(action)
        return action, params, value

    def update(self, rollout: dict, n_epochs: int = 4, batch_size: int = 64):
        obs = torch.FloatTensor(np.array(rollout["observations"]))
        actions = torch.FloatTensor(np.array(rollout["actions"]))
        old_log_probs = torch.FloatTensor(np.array(rollout["log_probs"]))
        returns = torch.FloatTensor(np.array(rollout["returns"]))
        advantages = torch.FloatTensor(np.array(rollout["advantages"]))
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        n_samples = obs.shape[0]
        indices = np.arange(n_samples)

        for _ in range(n_epochs):
            np.random.shuffle(indices)
            for start in range(0, n_samples, batch_size):
                end = start + batch_size
                batch_idx = indices[start:end]

                batch_obs = obs[batch_idx]
                batch_actions = actions[batch_idx]
                batch_old_log_probs = old_log_probs[batch_idx]
                batch_returns = returns[batch_idx]
                batch_advantages = advantages[batch_idx]

                log_probs, entropy, values = self.policy.evaluate_actions(
                    batch_obs, batch_actions
                )

                ratio = torch.exp(log_probs - batch_old_log_probs)
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.clip_eps, 1 + self.clip_eps) * batch_advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                value_loss = F.mse_loss(values, batch_returns)
                entropy_loss = -entropy.mean()

                loss = policy_loss + self.value_coef * value_loss + self.entropy_coef * entropy_loss

                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
                self.optimizer.step()

    def compute_gae(self, rewards, values, dones):
        advantages = []
        gae = 0.0
        next_value = 0.0

        for t in reversed(range(len(rewards))):
            mask = 1.0 - dones[t]
            delta = rewards[t] + self.gamma * next_value * mask - values[t]
            gae = delta + self.gamma * self.gae_lambda * mask * gae
            advantages.insert(0, gae)
            next_value = values[t]

        returns = [adv + val for adv, val in zip(advantages, values)]
        return advantages, returns

    def save(self, path: str):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        torch.save(
            {
                "policy_state_dict": self.policy.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
            },
            path,
        )

    def load(self, path: str):
        if not os.path.exists(path):
            return False
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        self.policy.load_state_dict(checkpoint["policy_state_dict"])
        if "optimizer_state_dict" in checkpoint:
            self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        return True
