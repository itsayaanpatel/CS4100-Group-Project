import block as blk

# 0 = Empty tile
# 1 = Floor tile
# S = Start tile
# G = Goal tile
# O = Soft button (activates when any part of block touches it)
# X = Hard button (activates only when block is upright on it)
# Bridge tiles are tracked separately in bridge_states and start inactive (treated as 0)

level_1_grid = [
    "1110000000",
    "1S11110000",
    "1111111110",
    "0111111111",
    "0000011G11",
    "0000001110",
]

VALID_TILES = {"1", "S", "G", "O", "X"}


# Finds the coord of a desired tile
def find_tile(tile, grid):
    for r, row in enumerate(grid):
        for c, col in enumerate(row):
            if col == tile:
                return (r, c)
    return None


class Level:
    # creates a level
    # buttons: {(r,c): {'type': 'soft'/'hard', 'toggles': [(r,c), ...]}}
    # bridge_tiles: [(r,c), ...] tiles that start inactive and can be toggled on/off
    def __init__(self, grid, buttons=None, bridge_tiles=None):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start_tile = find_tile("S", grid)
        self.goal_tile = find_tile("G", grid)
        self.buttons = buttons or {}
        self._initial_bridge_tiles = set(bridge_tiles or [])
        self.bridge_states = {tile: False for tile in self._initial_bridge_tiles}

        if self.start_tile is None:
            raise ValueError("Level has no start tile 'S'")
        if self.goal_tile is None:
            raise ValueError("Level has no goal tile 'G'")

    # resets all bridge tiles to inactive — called at the start of each episode
    def reset_bridges(self):
        self.bridge_states = {tile: False for tile in self._initial_bridge_tiles}

    # checks if the tiles a block occupies are all valid
    def is_valid(self, block):
        occupied_tiles = block.get_occupied_tiles()

        for r, c in occupied_tiles:
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                return False
            tile = self.grid[r][c]
            if tile not in VALID_TILES:
                # allow it only if it's an active bridge tile
                if not self.bridge_states.get((r, c), False):
                    return False
        return True

    # checks if a button is triggered by the block and toggles its bridge tiles
    def activate_buttons(self, block):
        for pos in set(block.get_occupied_tiles()):
            if pos in self.buttons:
                btn = self.buttons[pos]
                triggered = (
                    btn["type"] == "soft"
                    or (btn["type"] == "hard" and block.orientation == blk.UPRIGHT)
                )
                if triggered:
                    for tile in btn["toggles"]:
                        self.bridge_states[tile] = not self.bridge_states.get(tile, False)

    # checks if a block wins the game — must be upright on the goal tile
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

    # --- stateless helpers for search algorithms ---
    # Search cannot mutate self.bridge_states mid-exploration (would corrupt other
    # branches of the search tree), so these methods take bridge_states as a
    # frozenset of currently-active bridge tile positions and return new values
    # without touching self.bridge_states.

    # same logic as is_valid but uses a passed frozenset instead of self.bridge_states
    def is_valid_with_bridges(self, block, bridge_states):
        for r, c in block.get_occupied_tiles():
            if r < 0 or r >= self.rows or c < 0 or c >= self.cols:
                return False
            tile = self.grid[r][c]
            if tile not in VALID_TILES:
                if (r, c) not in bridge_states:
                    return False
        return True

    # returns a new frozenset of active bridge tiles after the block lands
    def compute_next_bridges(self, block, bridge_states):
        active = set(bridge_states)
        for pos in set(block.get_occupied_tiles()):
            if pos in self.buttons:
                btn = self.buttons[pos]
                triggered = (
                    btn["type"] == "soft"
                    or (btn["type"] == "hard" and block.orientation == blk.UPRIGHT)
                )
                if triggered:
                    for tile in btn["toggles"]:
                        if tile in active:
                            active.remove(tile)
                        else:
                            active.add(tile)
        return frozenset(active)

    # returns (new_block, action, new_bridge_states) for every valid move
    def get_next_states_with_bridges(self, block, bridge_states):
        next_states = []
        for action in [blk.UP, blk.DOWN, blk.LEFT, blk.RIGHT]:
            new_block = block.move(action)
            if self.is_valid_with_bridges(new_block, bridge_states):
                new_bridges = self.compute_next_bridges(new_block, bridge_states)
                next_states.append((new_block, action, new_bridges))
        return next_states
