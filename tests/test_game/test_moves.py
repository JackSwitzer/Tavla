import pytest
from game.types import Move, Player
from game.game import Game
from game.exceptions import InvalidMoveError
from tests.utils import create_board_position, assert_valid_move_sequence

class TestMoves:
    def test_basic_move(self, game):
        game.state.dice = (6, 1)
        move = Move(0, 6, 6)  # Move from point 1 to point 7
        assert game.make_move(move)
        assert game.state.board[0].count == 1  # One piece moved
        assert game.state.board[6].count == 1  # Landed here

    def test_invalid_move(self, game):
        game.state.dice = (3, 2)
        invalid_move = Move(5, 9, 4)  # 4 isn't available
        assert not game.make_move(invalid_move)

    def test_bar_move(self, game):
        game.state.bar[Player.WHITE] = 1
        game.state.dice = (6, 4)
        move = Move(24, 5, 6)  # From bar to point 6
        assert game.make_move(move)
        assert game.state.bar[Player.WHITE] == 0

    def test_bearing_off(self, bearing_off_state):
        bearing_off_state.dice = (6, 3)
        move = Move(5, -1, 6)  # Bear off from point 6
        assert game.make_move(move)
        assert game.state.off[Player.WHITE] == 1

    def test_capture(self, game):
        # Setup position with potential capture
        game.state.board[5] = Point(-1)  # Black blot
        game.state.dice = (6, 3)
        move = Move(0, 5, 6)  # White captures black
        
        assert game.make_move(move)
        assert game.state.board[5].count == 1  # White piece
        assert game.state.bar[Player.BLACK] == 1  # Black on bar

    def test_doubles(self, game):
        game.state.dice = (4, 4)
        moves = [
            Move(0, 4, 4),
            Move(4, 8, 4),
            Move(8, 12, 4),
            Move(12, 16, 4)
        ]
        assert_valid_move_sequence(game, moves) 