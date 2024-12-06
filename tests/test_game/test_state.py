import pytest
from game.types import Player, Point, GameStateSnapshot
from game.game_state import GameState
from game.exceptions import InvalidStateError
from game.utils.constants import BOARD_POINTS, PIECES_PER_PLAYER

class TestGameState:
    def test_initial_state(self):
        state = GameState.create_initial_state()
        assert len(state.board) == BOARD_POINTS
        assert state.current_player == Player.WHITE
        assert state.dice is None
        assert state.bar == {Player.WHITE: 0, Player.BLACK: 0}
        assert state.off == {Player.WHITE: 0, Player.BLACK: 0}
        assert not state.game_over

    def test_validate_state(self):
        state = GameState.create_initial_state()
        assert state.validate_state()

    def test_invalid_piece_count(self):
        state = GameState.create_initial_state()
        state.board[0].count = 16  # Too many pieces
        with pytest.raises(InvalidStateError):
            state.validate_state()

    def test_snapshot_roundtrip(self):
        original = GameState.create_initial_state()
        snapshot = original.to_snapshot()
        restored = GameState.from_snapshot(snapshot)
        
        assert original.board == restored.board
        assert original.current_player == restored.current_player
        assert original.dice == restored.dice
        assert original.bar == restored.bar
        assert original.off == restored.off
        assert original.game_over == restored.game_over

    def test_json_roundtrip(self):
        original = GameState.create_initial_state()
        json_str = original.to_json()
        restored = GameState.from_json(json_str)
        
        assert original.board == restored.board
        assert original.current_player == restored.current_player
        assert original.dice == restored.dice
        assert original.bar == restored.bar
        assert original.off == restored.off 