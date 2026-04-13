import random
import numpy as np
from collections import deque

import torch
import torch.nn as nn
import torch.nn.functional as F


def encode_state(state, level_rows, level_cols, n_bridges):
    """
    Encodes the state tuple (x, y, orientation, b0..bn) as a float32 numpy array.
      - x normalized to [0,1]
      - y normalized to [0,1]
      - orientation one-hot (3 values)
      - bridge bits cast to float (n_bridges values)
    Total length: 5 + n_bridges
    """
    x, y, o = state[0], state[1], state[2]
    bridge_bits = state[3:]

    x_norm = x / max(level_rows - 1, 1)
    y_norm = y / max(level_cols - 1, 1)

    orientation_onehot = [0.0, 0.0, 0.0]
    orientation_onehot[o] = 1.0

    vec = [x_norm, y_norm] + orientation_onehot + [float(b) for b in bridge_bits]
    return np.array(vec, dtype=np.float32)


class DQNNetwork(nn.Module):
    def __init__(self, input_dim, n_actions=4, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_actions),
        )

    def forward(self, x):
        return self.net(x)


class ReplayBuffer:
    def __init__(self, capacity=10_000):
        self.buffer = deque(maxlen=capacity)

    def push(self, state_vec, action, reward, next_vec, done):
        self.buffer.append((state_vec, action, reward, next_vec, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32),
        )

    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    def __init__(
        self,
        input_dim,
        n_actions=4,
        hidden_dim=64,
        lr=1e-3,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.05,
        epsilon_decay=0.9996,
        buffer_capacity=50_000,
        batch_size=64,
        target_update_freq=100,
        max_grad_norm=1.0,
    ):
        self.n_actions = n_actions
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.max_grad_norm = max_grad_norm

        self.policy_net = DQNNetwork(input_dim, n_actions, hidden_dim)
        self.target_net = DQNNetwork(input_dim, n_actions, hidden_dim)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()

        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=lr)
        self.buffer = ReplayBuffer(buffer_capacity)

        self._level_rows = None
        self._level_cols = None
        self._n_bridges = None

    def _init_encoding(self, env):
        self._level_rows = env.level.rows
        self._level_cols = env.level.cols
        self._n_bridges = len(env.level.bridge_states)

    def _encode(self, state):
        return encode_state(state, self._level_rows, self._level_cols, self._n_bridges)

    def select_action(self, state_vec):
        if random.random() < self.epsilon:
            return random.randrange(self.n_actions)
        with torch.no_grad():
            tensor = torch.FloatTensor(state_vec).unsqueeze(0)
            q_vals = self.policy_net(tensor)
            return q_vals.argmax(dim=1).item()

    def train_step(self):
        if len(self.buffer) < self.batch_size:
            return None
        states, actions, rewards, next_states, dones = self.buffer.sample(self.batch_size)

        states_t = torch.FloatTensor(states)
        actions_t = torch.LongTensor(actions).unsqueeze(1)
        rewards_t = torch.FloatTensor(rewards)
        next_states_t = torch.FloatTensor(next_states)
        dones_t = torch.FloatTensor(dones)

        q_current = self.policy_net(states_t).gather(1, actions_t).squeeze(1)

        with torch.no_grad():
            # Double DQN: policy net selects action, target net evaluates it
            next_actions = self.policy_net(next_states_t).argmax(1, keepdim=True)
            q_next = self.target_net(next_states_t).gather(1, next_actions).squeeze(1)
            q_target = rewards_t + self.gamma * q_next * (1 - dones_t)

        loss = F.smooth_l1_loss(q_current, q_target)
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.max_grad_norm)
        self.optimizer.step()
        return loss.item()

    def sync_target_network(self):
        self.target_net.load_state_dict(self.policy_net.state_dict())

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def train(self, env, n_episodes=3000):
        self._init_encoding(env)
        episode_rewards = []
        episode_lengths = []
        success_per_episode = []
        epsilon_history = []

        for episode in range(n_episodes):
            state = env.reset()
            state_vec = self._encode(state)
            total_reward = 0.0
            success = False

            for step in range(env.max_steps):
                action = self.select_action(state_vec)
                next_state, reward, done = env.step(action)
                next_vec = self._encode(next_state)
                self.buffer.push(state_vec, action, reward, next_vec, done)
                self.train_step()
                state_vec = next_vec
                total_reward += reward
                if done:
                    success = reward == 1.0
                    break

            self.decay_epsilon()
            if episode % self.target_update_freq == 0:
                self.sync_target_network()

            episode_rewards.append(total_reward)
            episode_lengths.append(step + 1)
            success_per_episode.append(success)
            epsilon_history.append(self.epsilon)

        return {
            "episode_rewards": episode_rewards,
            "episode_lengths": episode_lengths,
            "success_per_episode": success_per_episode,
            "epsilon_history": epsilon_history,
        }

    def run_episode_greedy(self, env):
        if self._level_rows is None:
            self._init_encoding(env)
        saved_epsilon = self.epsilon
        self.epsilon = 0.0
        state = env.reset()
        state_vec = self._encode(state)
        actions_taken = []
        total_reward = 0.0
        success = False

        for _ in range(env.max_steps):
            action = self.select_action(state_vec)
            next_state, reward, done = env.step(action)
            actions_taken.append(action)
            total_reward += reward
            state_vec = self._encode(next_state)
            if done:
                success = reward == 1.0
                break

        self.epsilon = saved_epsilon
        return actions_taken, total_reward, success
