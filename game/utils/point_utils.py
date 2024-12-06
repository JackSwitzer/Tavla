from typing import List, Optional
from game.types import Player, Point
from game.utils.constants import (
    BOARD_POINTS, WHITE_HOME_RANGE, BLACK_HOME_RANGE
)

def get_player_points(board: List[Point], player: Player) -> List[int]:
    """Get indices of points where player has pieces"""
    return [i for i, point in enumerate(board) if point.color == player]

def get_home_range(player: Player) -> range:
    """Get the home board range for a player"""
    return WHITE_HOME_RANGE if player == Player.WHITE else BLACK_HOME_RANGE

def calculate_pip_count(
    board: List[Point],
    bar: dict[Player, int],
    player: Player
) -> int:
    """Calculate pip count for a player"""
    pip_count = 0
    
    # Count board pieces
    for i, point in enumerate(board):
        if point.color == player:
            distance = 24 - i if player == Player.BLACK else i + 1
            pip_count += abs(point.count) * distance
    
    # Add bar pieces
    if bar[player] > 0:
        distance = 24 if player == Player.BLACK else 1
        pip_count += bar[player] * distance
    
    return pip_count

def can_bear_off(
    board: List[Point],
    bar: dict[Player, int],
    player: Player
) -> bool:
    """Check if player can bear off pieces"""
    if bar[player] > 0:
        return False
        
    home_range = get_home_range(player)
    
    # Check if all pieces are in home board
    for i in range(BOARD_POINTS):
        point = board[i]
        if point.color == player and i not in home_range:
            return False
    return True 