from level import Level
from block import Block
from levels import HARDCODED_LEVELS
import time
import os
from search import bfs_states, bfs_with_stats, convert_actions

# Color constants
RESET = "\033[0m"
FLOOR = "\033[37m"  # white
VOID = "\033[30m"  # black
BLOCK = "\033[36m"  # cyan
GOAL = "\033[32m"  # green
VISITED = "\033[33m"  # yellow


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
            elif visited and (r, c) in visited:  # first checks if visited exists
                line += VISITED + "██" + RESET
            elif tile == "0":
                line += VOID + "██" + RESET
            elif tile == "1" or tile == "S":
                line += FLOOR + "██" + RESET
        print(line)


# Clears the terminal
def clear_screen():
    os.system("clear")


# Prints BFS exploration in terminal
# Displays visited tiles as yellow, the current tile(s) as blue, the goal tile as green
def animate_bfs(level):
    explored = set()
    for current_block, actions in bfs_states(level):
        explored.update(current_block.get_occupied_tiles())
        clear_screen()
        render_grid(level, current_block, explored)
        time.sleep(0.5)
        if level.is_won(current_block):
            return actions


#
#
def animate_path(level, actions):
    block = Block(level.start_tile[0], level.start_tile[1])

    for action in actions:
        clear_screen()
        render_grid(level, block)
        time.sleep(0.8)
        block = block.move(action)

    clear_screen()
    render_grid(level, block)
    time.sleep(0.8)

    clear_screen()
    render_grid(level, block, show_block=False)


level1 = Level(HARDCODED_LEVELS[0]["grid"])
block = Block(level1.start_tile[0], level1.start_tile[1])
# render_grid(level1, block)

actions = animate_bfs(level1)
# animate_bfs(level1)

animate_path(level1, actions)
