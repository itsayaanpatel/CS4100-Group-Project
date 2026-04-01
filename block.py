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

    def move(action):
        

        

        