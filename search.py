import heapq
import block as blk
from block import Block
import level as lvl
from level import Level, level_1_grid
import time


# Finds a path to goal tile with BFS
# Returns list of actions, number of states explored, and time taken
# State includes bridge configuration so button/bridge levels are handled correctly
def bfs_with_stats(level):
    start_time = time.time()

    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)
    start_bridges = frozenset()

    queue = [(start_block, start_bridges, [])]
    visited = {(start_block.x, start_block.y, start_block.orientation, start_bridges)}
    states_explored = 0

    while queue:
        current_block, bridge_states, actions = queue.pop(0)
        states_explored += 1

        if level.is_won(current_block):
            return actions, states_explored, time.time() - start_time

        for next_block, action, new_bridges in level.get_next_states_with_bridges(current_block, bridge_states):
            state = (next_block.x, next_block.y, next_block.orientation, new_bridges)
            if state not in visited:
                visited.add(state)
                queue.append((next_block, new_bridges, actions + [action]))

    return None, states_explored, time.time() - start_time


# Generator version of BFS — yields each explored block for visualization
# Also yields bridge_states so the visualizer can render active bridge tiles
def bfs_states(level):
    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)
    start_bridges = frozenset()

    queue = [(start_block, start_bridges, [])]
    visited = {(start_block.x, start_block.y, start_block.orientation, start_bridges)}

    while queue:
        current_block, bridge_states, actions = queue.pop(0)

        yield current_block, actions, bridge_states

        if level.is_won(current_block):
            return

        for next_block, action, new_bridges in level.get_next_states_with_bridges(current_block, bridge_states):
            state = (next_block.x, next_block.y, next_block.orientation, new_bridges)
            if state not in visited:
                visited.add(state)
                queue.append((next_block, new_bridges, actions + [action]))


def heuristic(block, goal_tile):
    goal_x, goal_y = goal_tile
    return abs(block.x - goal_x) + abs(block.y - goal_y)


# Finds a path to goal tile with A*
# Returns list of actions, number of states explored, and time taken
# State includes bridge configuration so button/bridge levels are handled correctly
def astar_with_stats(level):
    start_time = time.time()

    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)
    start_bridges = frozenset()

    counter = 0
    heap = [(0, 0, counter, start_block, start_bridges, [])]
    visited = set()
    states_explored = 0

    while heap:
        f, g, _, current_block, bridge_states, actions = heapq.heappop(heap)

        state = (current_block.x, current_block.y, current_block.orientation, bridge_states)
        if state in visited:
            continue
        visited.add(state)
        states_explored += 1

        if level.is_won(current_block):
            return actions, states_explored, time.time() - start_time

        for next_block, action, new_bridges in level.get_next_states_with_bridges(current_block, bridge_states):
            next_state = (next_block.x, next_block.y, next_block.orientation, new_bridges)
            if next_state not in visited:
                new_g = g + 1
                new_f = new_g + heuristic(next_block, level.goal_tile)
                counter += 1
                heapq.heappush(
                    heap, (new_f, new_g, counter, next_block, new_bridges, actions + [action])
                )

    return None, states_explored, time.time() - start_time

# Generator version of A* — yields each block for visualization
# Also yields bridge_states so the visualizer can render active bridge tiles
def astar_states(level):

    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)
    start_bridges = frozenset()

    counter = 0
    heap = [(0, 0, counter, start_block, start_bridges, [])]
    visited = set()

    while heap:
        f, g, _, current_block, bridge_states, actions = heapq.heappop(heap)

        state = (current_block.x, current_block.y, current_block.orientation, bridge_states)
        if state in visited:
            continue
        visited.add(state)

        yield current_block, actions, bridge_states

        if level.is_won(current_block):
            return

        for next_block, action, new_bridges in level.get_next_states_with_bridges(current_block, bridge_states):
            next_state = (next_block.x, next_block.y, next_block.orientation, new_bridges)
            if next_state not in visited:
                new_g = g + 1
                new_f = new_g + heuristic(next_block, level.goal_tile)
                counter += 1
                heapq.heappush(
                    heap, (new_f, new_g, counter, next_block, new_bridges, actions + [action])
                )

    return


# prints
def convert_actions(action_list):
    actions = []
    action_names = {
        blk.UP: "UP",
        blk.DOWN: "DOWN",
        blk.LEFT: "LEFT",
        blk.RIGHT: "RIGHT",
    }
    for action in action_list:
        actions.append(action_names[action])
    return actions


from levels import HARDCODED_LEVELS

data = HARDCODED_LEVELS[1]
level = Level(data["grid"], data["buttons"], data["bridge_tiles"])


# # Changed up the print format to show the number of states explored and
# #  time taken for each algorithm. This will help in comparing the efficiency of BFS and A* on the given level.
solution, states_explored, time_taken = bfs_with_stats(level)
print(
    "BFS:",
    convert_actions(solution),
    f"| states: {states_explored} | time: {time_taken:.6f}s",
)

solution, states_explored, time_taken = astar_with_stats(level)
print(
    "A*: ",
    convert_actions(solution),
    f"| states: {states_explored} | time: {time_taken:.6f}s",
)
