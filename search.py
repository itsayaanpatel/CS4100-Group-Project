import heapq
import block as blk
from block import Block
import level as lvl
from level import Level, level_1_grid
import time


# Attempts to find optimal path for a level
# Returns list of actions, number of states explored, and time taken
def bfs_with_stats(level):
    start_time = time.time()

    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)

    queue = [(start_block, [])]
    visited = {(start_block.x, start_block.y, start_block.orientation)}
    states_explored = 0

    while queue:
        current_block, actions = queue.pop(0)
        states_explored += 1

        if level.is_won(current_block):
            return actions, states_explored, time.time() - start_time

        # adds all neighbor states of the current state into the queue
        # when a neighbor state is added, it goes into the visited list so it can't be added again
        for next_block, action in level.get_next_states(current_block):
            state = (next_block.x, next_block.y, next_block.orientation)
            if state not in visited:
                visited.add(state)
                queue.append((next_block, actions + [action]))
    return None, states_explored, time.time() - start_time


def heuristic(block, goal_tile):
    goal_x, goal_y = goal_tile
    return abs(block.x - goal_x) + abs(block.y - goal_y)


# Finds a path to goal tile with A*
# Returns list of actions, number of states explored, and time taken
def astar_with_stats(level):
    start_time = time.time()

    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)

    counter = 0
    heap = [(0, 0, counter, start_block, [])]
    visited = set()
    states_explored = 0

    while heap:
        f, g, _, current_block, actions = heapq.heappop(heap)

        state = (current_block.x, current_block.y, current_block.orientation)
        if state in visited:
            continue
        visited.add(state)
        states_explored += 1

        if level.is_won(current_block):
            return actions, states_explored, time.time() - start_time

        for next_block, action in level.get_next_states(current_block):
            next_state = (next_block.x, next_block.y, next_block.orientation)
            if next_state not in visited:
                new_g = g + 1
                new_f = new_g + heuristic(next_block, level.goal_tile)
                counter += 1
                heapq.heappush(heap, (new_f, new_g, counter, next_block, actions + [action]))

    return None, states_explored, time.time() - start_time


# returns a list of actions as words instead of integers
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


level = Level(level_1_grid)

solution, states_explored, time_taken = bfs_with_stats(level)
print("BFS:", convert_actions(solution), f"| states: {states_explored} | time: {time_taken:.6f}s")

solution, states_explored, time_taken = astar_with_stats(level)
print("A*: ", convert_actions(solution), f"| states: {states_explored} | time: {time_taken:.6f}s")
