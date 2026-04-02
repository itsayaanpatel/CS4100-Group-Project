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
solution = bloxorz_bfs(level)
print(convert_actions(solution))
