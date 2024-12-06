import pytest
from game.utils.validators import (
    validate_board_state,
    validate_dice,
    validate_doubles_count
)
from game.types import Player, Point
from game.utils.constants import BOARD_POINTS

class TestValidators:
    def test_valid_board_state(self):
        board = [Point() for _ in range(BOARD_POINTS)]
        bar = {Player.WHITE: 0, Player.BLACK: 0}
        off = {Player.WHITE: 0, Player.BLACK: 0}
        
        # Set up a valid position
        board[0] = Point(2)
        board[5] = Point(-2)
        
        assert validate_board_state(board, bar, off)

    def test_invalid_piece_count(self):
        board = [Point() for _ in range(BOARD_POINTS)]
        bar = {Player.WHITE: 0, Player.BLACK: 0}
        off = {Player.WHITE: 0, Player.BLACK: 0}
        
        # Too many pieces
        board[0] = Point(16)
        
        assert not validate_board_state(board, bar, off)

    def test_valid_dice(self):
        assert validate_dice((1, 6))
        assert validate_dice((3, 3, 3, 3))  # Doubles
        assert validate_dice(None)

    def test_invalid_dice(self):
        assert not validate_dice((0, 7))
        assert not validate_dice((1, 2, 3, 4, 5))

    def test_valid_doubles_count(self):
        assert validate_doubles_count(None)
        assert validate_doubles_count(0)
        assert validate_doubles_count(4)

    def test_invalid_doubles_count(self):
        assert not validate_doubles_count(-1)
        assert not validate_doubles_count(5) 