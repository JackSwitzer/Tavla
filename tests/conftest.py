import pytest
from game.types import Player, Point, Move, GameStateSnapshot
from game.game_state import GameState
from game.game import Game
from game.utils.constants import BOARD_POINTS

@pytest.fixture
def empty_game_state():
    """Empty board state"""
    return GameState(
        board=[Point() for _ in range(BOARD_POINTS)],
        current_player=Player.WHITE,
        dice=None,
        bar={Player.WHITE: 0, Player.BLACK: 0},
        off={Player.WHITE: 0, Player.BLACK: 0}
    )

@pytest.fixture
def mid_game_state():
    """Realistic mid-game position"""
    board = [Point() for _ in range(BOARD_POINTS)]
    # White pieces
    board[0] = Point(2)   # Point 1
    board[7] = Point(3)   # Point 8
    board[12] = Point(5)  # Point 13
    board[16] = Point(3)  # Point 17
    # Black pieces
    board[5] = Point(-2)  # Point 6
    board[11] = Point(-5) # Point 12
    board[18] = Point(-3) # Point 19
    board[23] = Point(-2) # Point 24
    
    return GameState(
        board=board,
        current_player=Player.WHITE,
        dice=None,
        bar={Player.WHITE: 0, Player.BLACK: 0},
        off={Player.WHITE: 0, Player.BLACK: 0}
    )

@pytest.fixture
def bearing_off_state():
    """Position where White can bear off"""
    board = [Point() for _ in range(BOARD_POINTS)]
    # White pieces all in home board
    board[0] = Point(3)  # Point 1
    board[2] = Point(4)  # Point 3
    board[4] = Point(5)  # Point 5
    board[5] = Point(3)  # Point 6
    # Black pieces far away
    board[18] = Point(-8) # Point 19
    board[20] = Point(-7) # Point 21
    
    return GameState(
        board=board,
        current_player=Player.WHITE,
        dice=None,
        bar={Player.WHITE: 0, Player.BLACK: 0},
        off={Player.WHITE: 0, Player.BLACK: 0}
    )

@pytest.fixture
def game():
    """Fresh game instance"""
    return Game()

@pytest.fixture
def game_with_dice():
    """Game with predetermined dice roll"""
    game = Game()
    game.state.dice = (6, 3)
    return game 