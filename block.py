# Possible orientations
UPRIGHT = 0
HORIZONTAL = 1
VERTICAL = 2

# Possible Actions
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


## Block is given a starting x and y position and orientation
## The tiles it occupies are updated based on action
## This is essentially everything that is tracked in the block class

## The level/environment class keeps track of what happens when a block is
## on a certain tile. Ex. wins, dies


class Block:
    # Creates an upright block at a starting x and y position
    def __init__(self, x, y, orientation=UPRIGHT):
        self.x = x
        self.y = y
        self.orientation = orientation

    # updates block's anchor position (top-left most tile) based on action taken
    # and current orientation
    def move(self, action):
        x, y, o = self.x, self.y, self.orientation

        if o == UPRIGHT:
            if action == UP:
                return Block(x - 2, y, VERTICAL)
            elif action == DOWN:
                return Block(x + 1, y, VERTICAL)
            elif action == LEFT:
                return Block(x, y - 2, HORIZONTAL)
            elif action == RIGHT:
                return Block(x, y + 1, HORIZONTAL)
        elif o == VERTICAL:
            if action == UP:
                return Block(x - 1, y, UPRIGHT)
            elif action == DOWN:
                return Block(x + 2, y, UPRIGHT)
            elif action == LEFT:
                return Block(x, y - 1, VERTICAL)
            elif action == RIGHT:
                return Block(x, y + 1, VERTICAL)
        elif o == HORIZONTAL:
            if action == UP:
                return Block(x - 1, y, HORIZONTAL)
            elif action == DOWN:
                return Block(x + 1, y, HORIZONTAL)
            elif action == LEFT:
                return Block(x, y - 1, UPRIGHT)
            elif action == RIGHT:
                return Block(x, y + 2, UPRIGHT)

    # returns a list of all tiles occupied by a block based on its
    # anchor position (top-left most tile) and orientation
    def get_occupied_tiles(self):
        x, y, o = self.x, self.y, self.orientation
        occupied_tiles = []
        occupied_tiles.append((x, y))
        if o == UPRIGHT:
            return occupied_tiles
        elif o == VERTICAL:
            occupied_tiles.append((x + 1, y))
        elif o == HORIZONTAL:
            occupied_tiles.append((x, y + 1))
        return occupied_tiles
