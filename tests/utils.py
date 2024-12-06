from typing import List, Tuple, Optional, Dict
from game.types import Player, Point, Move, GameStateSnapshot
from game.game import Game
from game.game_state import GameState
from game.utils.constants import BOARD_POINTS

def create_board_position(positions: List[Tuple[int, int]]) -> List[Point]:
    """
    Create a board from position tuples
    Args:
        positions: List of (point_index, count) tuples
    Returns:
        List[Point]: Complete board state
    """
    board = [Point() for _ in range(BOARD_POINTS)]
    for point_idx, count in positions:
        board[point_idx] = Point(count)
    return board

def assert_valid_move_sequence(game: Game, moves: List[Move]) -> None:
    """
    Assert that a sequence of moves is valid
    Args:
        game: Game instance
        moves: List of moves to execute
    Raises:
        AssertionError: If any move is invalid
    """
    initial_state = game.state.to_snapshot()
    
    for move in moves:
        assert game.make_move(move), f"Move {move} should be valid"
    
    # Verify final position
    final_state = game.state.to_snapshot()
    assert final_state != initial_state, "Game state should have changed"

def create_game_snapshot(
    board: Optional[List[Point]] = None,
    current_player: Player = Player.WHITE,
    dice: Optional[Tuple[int, ...]] = None,
    bar: Optional[Dict[Player, int]] = None,
    off: Optional[Dict[Player, int]] = None,
    **kwargs
) -> GameStateSnapshot:
    """
    Create a game snapshot with custom board
    Args:
        board: Optional custom board state
        current_player: Current player
        dice: Optional dice values
        bar: Optional bar state
        off: Optional off state
        **kwargs: Additional GameStateSnapshot fields
    Returns:
        GameStateSnapshot: Custom game state
    """
    if board is None:
        board = [Point() for _ in range(BOARD_POINTS)]
    if bar is None:
        bar = {Player.WHITE: 0, Player.BLACK: 0}
    if off is None:
        off = {Player.WHITE: 0, Player.BLACK: 0}
        
    return GameStateSnapshot(
        board_state=tuple(point.count for point in board),
        current_player=current_player,
        dice=dice,
        bar=bar,
        off=off,
        game_over=kwargs.get('game_over', False),
        move_count=kwargs.get('move_count', 0),
        remaining_doubles=kwargs.get('remaining_doubles', None)
    ) 