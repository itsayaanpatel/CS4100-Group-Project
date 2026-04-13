from levels import HARDCODED_LEVELS
from level import Level
from env import BloxorzEnv
from q_learning import QLearningAgent
from dqn import DQNAgent
from evaluate import (
    run_rl_evaluation,
    run_search_baseline,
    compute_convergence_episode,
    print_comparison_table,
    plot_training_curves,
)
from visualizer import animate_path

# Hyperparameters per level index
Q_PARAMS = {
    0: dict(alpha=0.1,  epsilon_decay=0.995, n_episodes=5_000,  max_steps=200),
    1: dict(alpha=0.2,  epsilon_decay=0.998, n_episodes=15_000, max_steps=300),
    2: dict(alpha=0.1,  epsilon_decay=0.995, n_episodes=5_000,  max_steps=200),
}

DQN_PARAMS = {
    0: dict(lr=1e-3,  epsilon_decay=0.9996, n_episodes=10_000, max_steps=200),
    1: dict(lr=5e-4,  epsilon_decay=0.9998, n_episodes=20_000, max_steps=300),
    2: dict(lr=1e-3,  epsilon_decay=0.9996, n_episodes=10_000, max_steps=200),
}


def train_and_evaluate(level_idx, run_dqn=True, save_plots=False):
    data = HARDCODED_LEVELS[level_idx]
    level_name = data["name"]
    print(f"\n{'#'*55}")
    print(f"  {level_name}")
    print(f"{'#'*55}")

    qp = Q_PARAMS[level_idx]
    dp = DQN_PARAMS[level_idx]
    n_bridges = len(data["bridge_tiles"])

    # Search baseline
    level = Level(data["grid"], data["buttons"], data["bridge_tiles"])
    search_results = run_search_baseline(level)
    print(f"  BFS: {search_results['bfs_steps']} steps | "
          f"A*: {search_results['astar_steps']} steps  (optimal)")

    # --- Q-Learning ---
    print(f"\n  Training Q-Learning ({qp['n_episodes']} episodes)...")
    level = Level(data["grid"], data["buttons"], data["bridge_tiles"])
    env = BloxorzEnv(level, max_steps=qp["max_steps"])
    q_agent = QLearningAgent(
        alpha=qp["alpha"],
        epsilon_decay=qp["epsilon_decay"],
    )
    q_stats = q_agent.train(env, n_episodes=qp["n_episodes"])
    q_results = run_rl_evaluation(q_agent, env)
    q_conv = compute_convergence_episode(q_stats["success_per_episode"])
    print_comparison_table(level_name, "Q-Learning", q_results, search_results, q_conv)
    plot_training_curves(
        q_stats, f"Q-Learning — {level_name}",
        save_path=f"q_learning_{level_name.replace(' ', '_')}.png" if save_plots else None,
    )
    actions, _, success = q_agent.run_episode_greedy(env)
    if success:
        print(f"  Replaying Q-Learning solution ({len(actions)} steps)...")
        animate_path(level, actions)

    if not run_dqn:
        return

    # --- DQN ---
    print(f"  Training DQN ({dp['n_episodes']} episodes)...")
    level = Level(data["grid"], data["buttons"], data["bridge_tiles"])
    env = BloxorzEnv(level, max_steps=dp["max_steps"])
    dqn_agent = DQNAgent(
        input_dim=5 + n_bridges,
        lr=dp["lr"],
        epsilon_decay=dp["epsilon_decay"],
    )
    dqn_stats = dqn_agent.train(env, n_episodes=dp["n_episodes"])
    dqn_results = run_rl_evaluation(dqn_agent, env)
    dqn_conv = compute_convergence_episode(dqn_stats["success_per_episode"])
    print_comparison_table(level_name, "DQN", dqn_results, search_results, dqn_conv)
    plot_training_curves(
        dqn_stats, f"DQN — {level_name}",
        save_path=f"dqn_{level_name.replace(' ', '_')}.png" if save_plots else None,
    )
    actions, _, success = dqn_agent.run_episode_greedy(env)
    if success:
        print(f"  Replaying DQN solution ({len(actions)} steps)...")
        animate_path(level, actions)


if __name__ == "__main__":
    train_and_evaluate(level_idx=0, run_dqn=True)   # Level 1
    train_and_evaluate(level_idx=1, run_dqn=True)   # Level 2
    train_and_evaluate(level_idx=2, run_dqn=True)   # Level 3
