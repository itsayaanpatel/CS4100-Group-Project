import heapq
import block as blk
from block import Block
import level as lvl
from level import Level, level_1_grid


# Finds a path to goal tile with BFS
def bloxorz_bfs(level):
    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)

    queue = [(start_block, [])]
    visited = {(start_block.x, start_block.y, start_block.orientation)}

    while queue:
        current_block, actions = queue.pop(0)

        if level.is_won(current_block):
            return actions

        for next_block, action in level.get_next_states(current_block):
            state = (next_block.x, next_block.y, next_block.orientation)
            if state not in visited:
                visited.add(state)
                queue.append((next_block, actions + [action]))
    return None


def heuristic(block, goal_tile):
    goal_x, goal_y = goal_tile
    return abs(block.x - goal_x) + abs(block.y - goal_y)


# Finds a path to goal tile with A*
def bloxorz_astar(level):
    start_x, start_y = level.start_tile
    start_block = Block(start_x, start_y)

    counter = 0
    heap = [(0, 0, counter, start_block, [])]
    visited = set()

    while heap:
        f, g, _, current_block, actions = heapq.heappop(heap)

        state = (current_block.x, current_block.y, current_block.orientation)
        if state in visited:
            continue
        visited.add(state)

        if level.is_won(current_block):
            return actions

        for next_block, action in level.get_next_states(current_block):
            next_state = (next_block.x, next_block.y, next_block.orientation)
            if next_state not in visited:
                new_g = g + 1
                new_f = new_g + heuristic(next_block, level.goal_tile)
                counter += 1
                heapq.heappush(heap, (new_f, new_g, counter, next_block, actions + [action]))

    return None


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


level = Level(level_1_grid)

solution_bfs = bloxorz_bfs(level)
print("BFS:", convert_actions(solution_bfs))

solution_astar = bloxorz_astar(level)
print("A*: ", convert_actions(solution_astar))
