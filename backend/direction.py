from enum import Enum

class Direction(Enum):
    VERTICAL = ((-1, 0), (1, 0))
    HORIZONTAL = ((0, -1), (0, 1))
    MAIN_DIAG = ((-1, -1), (1, 1))
    ANTI_DIAG = ((-1, 1), (1, -1))
    TRAVERSE_VERTICALLY = (1, 0)
    TRAVERSE_HORIZONTALY = (0, 1)
    TRAVERSE_MAIN_DIAG = (1, 1)
    TRAVERSE_ANTI_DIAG = (1, -1)
    DIR = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1))


DV = Direction.VERTICAL
DH = Direction.HORIZONTAL
DM = Direction.MAIN_DIAG
DA = Direction.ANTI_DIAG
dV = Direction.TRAVERSE_VERTICALLY
dH = Direction.TRAVERSE_HORIZONTALY
dM = Direction.TRAVERSE_MAIN_DIAG
dA = Direction.TRAVERSE_ANTI_DIAG
dirs = Direction.DIR
STREAK_LEN = 5
win_situation_score = 1000
lose_situation_score = 900