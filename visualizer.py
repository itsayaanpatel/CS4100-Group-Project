from level import Level
from block import Block
from levels import HARDCODED_LEVELS
import time
import os
from search import bfs_states, astar_states, bfs_with_stats, convert_actions

# Color constants
RESET = "\033[0m"
FLOOR = "\033[37m"   # white
VOID = "\033[30m"    # black
BLOCK = "\033[36m"   # cyan
GOAL = "\033[32m"    # green
VISITED = "\033[33m" # yellow
BUTTON = "\033[35m"  # magenta — soft (O) and hard (X) buttons
BRIDGE = "\033[34m"  # blue — active bridge tiles


# Prints a game state to the terminal
def render_grid(level, block, visited=None, show_block=True):
    occupied = set(block.get_occupied_tiles())
    if not show_block:
        occupied = set()

    for r, row in enumerate(level.grid):
        line = ""
        for c, tile in enumerate(row):
            if (r, c) in occupied:
                line += BLOCK + "██" + RESET
            elif tile == "G":
                line += GOAL + "██" + RESET
            elif tile in ("O", "X"):
                line += BUTTON + "██" + RESET
            elif level.bridge_states.get((r, c), False):
                line += BRIDGE + "██" + RESET
            elif visited and (r, c) in visited:
                line += VISITED + "██" + RESET
            elif tile == "0":
                line += VOID + "██" + RESET
            elif tile in ("1", "S"):
                line += FLOOR + "██" + RESET
        print(line)


# Clears the terminal
def clear_screen():
    os.system("clear")


# Animates BFS exploration — yellow=visited, cyan=current block, green=goal, blue=active bridge
def animate_bfs(level):
    explored = set()
    states_count = 0
    for current_block, actions, bridge_states in bfs_states(level):
        explored.update(current_block.get_occupied_tiles())
        states_count += 1
        # sync level.bridge_states so render_grid shows active bridges correctly
        level.bridge_states = {tile: (tile in bridge_states) for tile in level._initial_bridge_tiles}
        clear_screen()
        print(f"BFS EXPLORING | States visited: ", states_count)
        render_grid(level, current_block, explored)
        time.sleep(0.3)
        if level.is_won(current_block):
            return actions


# Replays a solution path step by step
def animate_path(level, actions):
    level.reset_bridges()
    block = Block(level.start_tile[0], level.start_tile[1])
    steps = 0

    for action in actions:
        clear_screen()
        print(f"OPTIMAL PATH | Step " + str(steps) + " / " + str(len(actions)))
        render_grid(level, block)
        time.sleep(0.8)
        block = block.move(action)
        steps += 1
        level.activate_buttons(block)  # update bridges as block moves

    clear_screen()
    print(f"OPTIMAL PATH | Step " + str(steps) + " / " + str(len(actions)))
    render_grid(level, block)
    time.sleep(0.8)

    clear_screen()
    print(f"OPTIMAL PATH | Step " + str(steps) + " / " + str(len(actions)))
    render_grid(level, block, show_block=False)

# Animates A* exploration — yellow=visited, cyan=current block, green=goal, blue=active bridge
def animate_astar(level):
    explored = set()
    states_count = 0
    for current_block, actions, bridge_states in astar_states(level):
        explored.update(current_block.get_occupied_tiles())
        states_count += 1
        level.bridge_states = {tile: (tile in bridge_states) for tile in level._initial_bridge_tiles}
        clear_screen()
        print(f"A* EXPLORING | States visited: {states_count}")
        render_grid(level, current_block, explored)
        time.sleep(0.3)
        if level.is_won(current_block):
            return actions

data = HARDCODED_LEVELS[1]  # change index to switch levels (0=L1, 1=L2, 2=L3)
level = Level(data["grid"], data.get("buttons", {}), data.get("bridge_tiles", []))
block = Block(level.start_tile[0], level.start_tile[1])

# actions = animate_bfs(level)
actions = animate_astar(level)
animate_path(level, actions)
