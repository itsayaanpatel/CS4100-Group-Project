import random
from collections import defaultdict


class QLearningAgent:
    def __init__(
        self,
        n_actions=4,
        alpha=0.1,
        gamma=0.99,
        epsilon_start=1.0,
        epsilon_end=0.05,
        epsilon_decay=0.995,
    ):
        self.Q = defaultdict(lambda: [0.0] * n_actions)
        self.n_actions = n_actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

    def select_action(self, state):
        if random.random() < self.epsilon:
            return random.randrange(self.n_actions)
        q_vals = self.Q[state]
        return q_vals.index(max(q_vals))

    def update(self, state, action, reward, next_state, done):
        q_current = self.Q[state][action]
        q_next = 0.0 if done else max(self.Q[next_state])
        self.Q[state][action] = q_current + self.alpha * (
            reward + self.gamma * q_next - q_current
        )

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

    def train(self, env, n_episodes=5000):
        episode_rewards = []
        episode_lengths = []
        success_per_episode = []
        epsilon_history = []

        for episode in range(n_episodes):
            state = env.reset()
            total_reward = 0.0
            success = False

            for step in range(env.max_steps):
                action = self.select_action(state)
                next_state, reward, done = env.step(action)
                self.update(state, action, reward, next_state, done)
                state = next_state
                total_reward += reward

                if done:
                    success = reward == 1.0
                    break

            self.decay_epsilon()
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
        saved_epsilon = self.epsilon
        self.epsilon = 0.0
        state = env.reset()
        actions_taken = []
        total_reward = 0.0
        success = False

        for _ in range(env.max_steps):
            action = self.select_action(state)
            next_state, reward, done = env.step(action)
            actions_taken.append(action)
            total_reward += reward
            state = next_state
            if done:
                success = reward == 1.0
                break

        self.epsilon = saved_epsilon
        return actions_taken, total_reward, success
