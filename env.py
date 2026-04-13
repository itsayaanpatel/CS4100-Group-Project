import block as blk
from block import Block
from level import Level


class BloxorzEnv:
    def __init__(self, level, max_steps=200):
        self.level = level
        self.block = None
        self.steps_taken = 0
        self.max_steps = max_steps

    def reset(self):
        x, y = self.level.start_tile
        self.block = Block(x, y)
        self.level.reset_bridges()
        self.steps_taken = 0
        return self._get_state()

    def step(self, action):
        self.steps_taken += 1
        new_block = self.block.move(action)

        if self.level.is_won(new_block):
            self.block = new_block
            return self._get_state(), 1.0, True       # goal reached

        if not self.level.is_valid(new_block):
            return self._get_state(), -1.0, True      # fell off

        self.block = new_block
        self.level.activate_buttons(self.block)       # toggle bridges if on a button
        done = self.steps_taken >= self.max_steps
        return self._get_state(), -0.01, done         # step penalty

    def render(self):
        occupied = set(self.block.get_occupied_tiles())
        for r, row in enumerate(self.level.grid):
            line = ""
            for c, tile in enumerate(row):
                if (r, c) in occupied:
                    line += "B "
                else:
                    line += tile + " "
            print(line)
        print()

    def _get_state(self):
        x, y, o = self.block.x, self.block.y, self.block.orientation
        bridge_bits = tuple(
            self.level.bridge_states[tile]
            for tile in sorted(self.level.bridge_states.keys())
        )
        return (x, y, o) + bridge_bits
