# A list of hardcoded levels
# 1 = Floor tile, 0 = empty tile, S = Start tile, G = Goal tile
# O = Soft button (any block orientation triggers it)
# X = Hard button (only upright block triggers it)
# bridge_tiles: list of (r,c) that start as 0 and toggle when their button is pressed
HARDCODED_LEVELS = [
    {
        "name": "Level 1",
        "grid": [
            "1110000000",
            "1S11110000",
            "1111111110",
            "0111111111",
            "0000011G11",
            "0000001110",
        ],
        "buttons": {},
        "bridge_tiles": [],
    },
    {
        "name": "Level 2",
        #O: soft button that toggles bridges regardless of block orientation
        #X: hard button that only toggles bridges when block is upright
        "grid": [
            "000000111100111",
            "11110011X1001G1",
            "11O100111100111",
            "111100111100111",
            "1S1100111100111",
            "111100111100000",
        ],
        "buttons": {
            (2, 2): {"type": "soft", "toggles": [(4, 4), (4, 5)]},
            (1, 8): {"type": "hard", "toggles": [(4, 10), (4, 11)]},
        },
        "bridge_tiles": [(4, 4), (4, 5), (4, 10), (4, 11)],
    },
    {
        "name": "Level 3",
        "grid": [
            "1111000000",
            "1S11110000",
            "1111111100",
            "0011111110",
            "000011111G",
            "0000111110",
        ],
        "buttons": {},
        "bridge_tiles": [],
    },
]
