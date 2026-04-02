import block as blk

# 0 = Empty tile
# 1 = Floor tile
# S = Start tile
# G = Goal tile
level_1_grid = [
    "1110000000",
    "1S11110000",
    "1111111110",
    "0111111111",
    "0000011G11",
    "0000001110",
]


# Finds the coord of a desired tile
def find_tile(tile, grid):
    for r, row in enumerate(grid):
        for c, col in enumerate(row):
            if col == tile:
                return (r, c)
    return None


class Level:
    # creates a level
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start_tile = find_tile("S", grid)
        self.goal_tile = find_tile("G", grid)

        if self.start_tile is None:
            raise ValueError("Level has no start tile 'S'")
        if self.goal_tile is None:
            raise ValueError("Level has no goal tile 'G'")

    # checks if the tiles that a block is occupying are valid or not based on the level grid
    def is_valid(self, block):
        occupied_tiles = block.get_occupied_tiles()

        for r, c in occupied_tiles:
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                return False
            if self.grid[r][c] == "0":
                return False
        return True

    # checks if a block wins the game if it is upright on the goal tile
    def is_won(self, block):
        x, y, o = block.x, block.y, block.orientation
        goal_x, goal_y = self.goal_tile

        return x == goal_x and y == goal_y and o == blk.UPRIGHT

    # gets all next states that are valid for a given block
    def get_next_states(self, block):
        next_states = []
        for action in [blk.UP, blk.DOWN, blk.LEFT, blk.RIGHT]:
            new_block = block.move(action)
            if self.is_valid(new_block):
                next_states.append((new_block, action))
        return next_states
