import numpy as np
from search import bfs_with_stats, astar_with_stats, convert_actions


def run_rl_evaluation(agent, env, n_eval=100):
    successes = []
    steps_on_success = []

    for _ in range(n_eval):
        actions, _, success = agent.run_episode_greedy(env)
        successes.append(success)
        if success:
            steps_on_success.append(len(actions))

    success_rate = sum(successes) / n_eval
    mean_steps = float(np.mean(steps_on_success)) if steps_on_success else float("nan")
    std_steps = float(np.std(steps_on_success)) if steps_on_success else float("nan")

    return {
        "success_rate": success_rate,
        "mean_steps": mean_steps,
        "std_steps": std_steps,
        "n_successes": sum(successes),
        "n_eval": n_eval,
    }


def run_search_baseline(level):
    bfs_sol, bfs_states, bfs_time = bfs_with_stats(level)
    astar_sol, astar_states, astar_time = astar_with_stats(level)
    return {
        "bfs_steps": len(bfs_sol) if bfs_sol else None,
        "bfs_states_explored": bfs_states,
        "bfs_time": bfs_time,
        "astar_steps": len(astar_sol) if astar_sol else None,
        "astar_states_explored": astar_states,
        "astar_time": astar_time,
        "optimal_steps": len(bfs_sol) if bfs_sol else None,
    }


def compute_convergence_episode(success_per_episode, window=100, threshold=0.9):
    for i in range(window, len(success_per_episode) + 1):
        window_slice = success_per_episode[i - window:i]
        if sum(window_slice) / window >= threshold:
            return i - window
    return None


def print_comparison_table(level_name, rl_name, rl_results, search_results, convergence_ep):
    print(f"\n{'='*55}")
    print(f"  {level_name} — {rl_name}")
    print(f"{'='*55}")
    print(f"  {'Metric':<30} {'Value':>20}")
    print(f"  {'-'*50}")
    print(f"  {'Success rate':<30} {rl_results['success_rate']*100:>19.1f}%")
    print(f"  {'Mean steps (successes)':<30} {rl_results['mean_steps']:>20.1f}")
    print(f"  {'Std steps':<30} {rl_results['std_steps']:>20.1f}")
    print(f"  {'Episodes to 90% success':<30} {str(convergence_ep) if convergence_ep else 'not reached':>20}")
    print(f"  {'-'*50}")
    print(f"  {'BFS optimal steps':<30} {search_results['bfs_steps']:>20}")
    print(f"  {'A* optimal steps':<30} {search_results['astar_steps']:>20}")
    print(f"  {'BFS states explored':<30} {search_results['bfs_states_explored']:>20}")
    print(f"  {'A* states explored':<30} {search_results['astar_states_explored']:>20}")
    print(f"{'='*55}\n")


def plot_training_curves(stats, agent_name, save_path=None):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed — skipping plot")
        return

    rewards = stats["episode_rewards"]
    successes = stats["success_per_episode"]
    episodes = range(len(rewards))

    window = 100
    rolling_success = [
        sum(successes[max(0, i - window):i + 1]) / min(i + 1, window)
        for i in range(len(successes))
    ]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    fig.suptitle(f"{agent_name} Training Curves")

    ax1.plot(episodes, rewards, alpha=0.3, color="steelblue", linewidth=0.8)
    ax1.plot(
        episodes,
        np.convolve(rewards, np.ones(window) / window, mode="same"),
        color="steelblue", linewidth=2, label=f"{window}-ep moving avg"
    )
    ax1.set_ylabel("Episode Reward")
    ax1.legend()

    ax2.plot(episodes, rolling_success, color="green", linewidth=2)
    ax2.axhline(0.9, color="red", linestyle="--", linewidth=1, label="90% threshold")
    ax2.set_ylabel("Rolling Success Rate")
    ax2.set_xlabel("Episode")
    ax2.set_ylim(0, 1.05)
    ax2.legend()

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
        print(f"Saved plot to {save_path}")
    else:
        plt.show()
    plt.close()
