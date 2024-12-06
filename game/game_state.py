from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
from game.types import Player, Point, GameStateSnapshot
from game.utils.constants import BOARD_POINTS, INITIAL_POSITION, PIECES_PER_PLAYER
from game.exceptions import InvalidStateError

@dataclass
class GameState:
    """
    Pure data class representing the state of a backgammon game.
    Handles state validation and serialization.
    """
    board: List[Point]
    current_player: Player
    dice: Optional[Tuple[int, ...]]
    bar: Dict[Player, int]
    off: Dict[Player, int]
    game_over: bool = False
    move_count: int = 0
    remaining_doubles: Optional[int] = None

    def __post_init__(self):
        """Validate state after initialization"""
        if not self.validate_state():
            raise InvalidStateError("Invalid game state")

    @classmethod
    def create_initial_state(cls) -> 'GameState':
        """Create a new game state with initial setup"""
        board = [Point() for _ in range(BOARD_POINTS)]
        
        for point_idx, count in INITIAL_POSITION:
            board[point_idx - 1] = Point(count)
        
        return cls(
            board=board,
            current_player=Player.WHITE,
            dice=None,
            bar={Player.WHITE: 0, Player.BLACK: 0},
            off={Player.WHITE: 0, Player.BLACK: 0}
        )

    def validate_state(self) -> bool:
        """Validate the current state is legal"""
        try:
            # Check piece counts
            white_count = sum(p.count for p in self.board if p.count > 0)
            black_count = sum(-p.count for p in self.board if p.count < 0)
            white_count += self.bar[Player.WHITE] + self.off[Player.WHITE]
            black_count += self.bar[Player.BLACK] + self.off[Player.BLACK]
            
            # Basic validations
            assert white_count == PIECES_PER_PLAYER
            assert black_count == PIECES_PER_PLAYER
            assert all(-15 <= p.count <= 15 for p in self.board)
            assert all(count >= 0 for count in self.bar.values())
            assert all(count >= 0 for count in self.off.values())
            
            # Dice validation
            if self.dice:
                assert all(1 <= d <= 6 for d in self.dice)
                assert 1 <= len(self.dice) <= 4
            
            # Doubles validation
            if self.remaining_doubles is not None:
                assert 0 <= self.remaining_doubles <= 4
            
            return True
            
        except AssertionError:
            return False

    def to_snapshot(self) -> GameStateSnapshot:
        """Create immutable snapshot of current state"""
        return GameStateSnapshot(
            board_state=tuple(point.count for point in self.board),
            current_player=self.current_player,
            dice=self.dice,
            bar=self.bar.copy(),
            off=self.off.copy(),
            game_over=self.game_over,
            move_count=self.move_count,
            remaining_doubles=self.remaining_doubles
        )

    @classmethod
    def from_snapshot(cls, snapshot: GameStateSnapshot) -> 'GameState':
        """Create new state from snapshot"""
        return cls(
            board=[Point(count) for count in snapshot.board_state],
            current_player=snapshot.current_player,
            dice=snapshot.dice,
            bar=snapshot.bar.copy(),
            off=snapshot.off.copy(),
            game_over=snapshot.game_over,
            move_count=snapshot.move_count,
            remaining_doubles=snapshot.remaining_doubles
        )

    def get_player_points(self, player: Player) -> List[int]:
        """Get points where player has pieces (excluding bar/off)"""
        return [
            i for i, point in enumerate(self.board)
            if point.color == player
        ]

    def is_player_blocked(self, player: Player) -> bool:
        """Check if player has any legal moves available"""
        return (
            self.bar[player] > 0 and
            all(self.board[i].count >= 2 and 
                self.board[i].color == player.opponent
                for i in range(BOARD_POINTS))
        )