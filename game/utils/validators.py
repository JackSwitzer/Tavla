from typing import List, Dict, Optional, Tuple
from game.types import Player, Point
from game.utils.constants import (
    BOARD_POINTS, PIECES_PER_PLAYER, MIN_DICE, MAX_DICE,
    MAX_DOUBLES, MAX_POINT_PIECES
)

def validate_board_state(
    board: List[Point],
    bar: Dict[Player, int],
    off: Dict[Player, int]
) -> bool:
    """Validate complete board state including bar and off"""
    try:
        # Check piece counts
        white_count = sum(p.count for p in board if p.count > 0)
        black_count = sum(-p.count for p in board if p.count < 0)
        white_count += bar[Player.WHITE] + off[Player.WHITE]
        black_count += bar[Player.BLACK] + off[Player.BLACK]
        
        # Basic validations
        assert white_count == PIECES_PER_PLAYER
        assert black_count == PIECES_PER_PLAYER
        assert all(-MAX_POINT_PIECES <= p.count <= MAX_POINT_PIECES for p in board)
        assert all(count >= 0 for count in bar.values())
        assert all(count >= 0 for count in off.values())
        assert len(board) == BOARD_POINTS
        
        return True
    except AssertionError:
        return False

def validate_dice(dice: Optional[Tuple[int, ...]]) -> bool:
    """Validate dice values and count"""
    if dice is None:
        return True
        
    try:
        assert all(MIN_DICE <= d <= MAX_DICE for d in dice)
        assert 1 <= len(dice) <= 4
        return True
    except AssertionError:
        return False

def validate_doubles_count(count: Optional[int]) -> bool:
    """Validate remaining doubles count"""
    if count is None:
        return True
    return 0 <= count <= MAX_DOUBLES 