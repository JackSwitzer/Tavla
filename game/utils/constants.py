from typing import Final, Tuple

# Board constants
BOARD_POINTS: Final[int] = 24
PIECES_PER_PLAYER: Final[int] = 15
BAR_POINT: Final[int] = 24
OFF_POINT: Final[int] = -1

# Dice constants
MIN_DICE: Final[int] = 1
MAX_DICE: Final[int] = 6
DICE_COUNT: Final[int] = 2
MAX_DOUBLES: Final[int] = 4

# Initial setup - (point_number, count) where negative count means black pieces
INITIAL_POSITION: Final[Tuple[Tuple[int, int], ...]] = (
    (1, 2),    # Point 1: 2 white pieces
    (12, 5),   # Point 12: 5 white pieces
    (17, 3),   # Point 17: 3 white pieces
    (19, 5),   # Point 19: 5 white pieces
    (6, -5),   # Point 6: 5 black pieces
    (8, -3),   # Point 8: 3 black pieces
    (13, -5),  # Point 13: 5 black pieces
    (24, -2),  # Point 24: 2 black pieces
)

# Game rules
MAX_POINT_PIECES: Final[int] = 15
BEARING_OFF_THRESHOLD: Final[int] = 6

# Home board ranges
WHITE_HOME_RANGE: Final[range] = range(0, 6)
BLACK_HOME_RANGE: Final[range] = range(18, 24)