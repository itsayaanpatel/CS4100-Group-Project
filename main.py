from visualizer import clear_screen, animate_bfs, animate_astar, animate_path
from levels import HARDCODED_LEVELS
from search import bfs_with_stats, bfs_states, astar_with_stats, astar_states
from level import Level

# Prints a welcome screen
def welcome_screen():
    clear_screen()
    print("================================")
    print("         BLOXORZ SOLVER         ")
    print("================================")
    print()
    input("Press enter to start...")

# Prints a level selection screen and selects a level from user choice
def select_level():
    clear_screen()
    print("================================")
    print("         SELECT A LEVEL         ")
    print("================================")
    print()
    for i, level in enumerate(HARDCODED_LEVELS):
        print(f"{level['name']}")
    print()
    choice = input("Enter level number: ")
    return HARDCODED_LEVELS[int(choice) - 1]

# Displays stats
def show_stats(bfs_states_count, bfs_time, astar_states_count, astar_time, actions):
    clear_screen()
    print("================================")
    print("           RESULTS              ")
    print("================================")
    print()
    print(f"  Path length:     {len(actions)} steps")
    print()
    print(f"  BFS")
    print(f"    States explored: {bfs_states_count}")
    print(f"    Time:            {bfs_time:.6f}s")
    print()
    print(f"  A*")
    print(f"    States explored: {astar_states_count}")
    print(f"    Time:            {astar_time:.6f}s")
    print()

# Runs Bloxorz solver
def run():
    welcome_screen()

    while True:
        data = select_level()
        level = Level(data["grid"], data.get("buttons", {}), data.get("bridge_tiles", []))

        # get stats instantly
        bfs_actions, bfs_states_count, bfs_time = bfs_with_stats(level)
        astar_actions, astar_states_count, astar_time = astar_with_stats(level)

        # animate BFS
        animate_bfs(level)
        animate_path(level, bfs_actions)

        # animate A*
        animate_astar(level)
        animate_path(level, astar_actions)

        # show stats
        show_stats(bfs_states_count, bfs_time, astar_states_count, astar_time, bfs_actions)

        again = input("Play again? (y/n): ")
        if again.lower() != "y":
            break

    clear_screen()
    print("Thanks for playing")

run()

