from typing import Optional, Tuple
from game.types import Player, Point, Move
from game.utils.constants import BOARD_POINTS, BAR_POINT, OFF_POINT

def calculate_target_point(
    from_point: int,
    die: int,
    player: Player
) -> Optional[int]:
    """Calculate target point for a move"""
    direction = 1 if player == Player.WHITE else -1
    target = from_point + (die * direction)
    
    if 0 <= target < BOARD_POINTS:
        return target
    return None

def is_valid_landing(point: Point, player: Player) -> bool:
    """Check if a point is a valid landing spot"""
    if point.color == player:
        return True
    return point.is_empty or point.is_blot

def calculate_entry_point(die: int, player: Player) -> int:
    """Calculate entry point from bar"""
    return die - 1 if player == Player.WHITE else BOARD_POINTS - die

def is_valid_bearing_off_move(
    point_idx: int,
    die: int,
    player: Player,
    has_pieces_behind: bool
) -> bool:
    """Check if bearing off move is valid"""
    if player == Player.WHITE:
        exact_roll = die == point_idx + 1
        higher_roll = die > point_idx + 1
    else:
        exact_roll = die == (24 - point_idx)
        higher_roll = die > (24 - point_idx)
        
    return exact_roll or (higher_roll and not has_pieces_behind) 