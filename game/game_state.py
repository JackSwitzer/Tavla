from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from game.player import Player
from game.move import MoveValidator

@dataclass
class Point:
    count: int = 0  # Positive for white, negative for black
        
    @property
    def is_empty(self) -> bool:
        return self.count == 0
        
    @property
    def color(self) -> Optional[Player]:
        if self.count > 0:
            return Player.WHITE
        elif self.count < 0:
            return Player.BLACK
        return None
        
    @property
    def is_blot(self) -> bool:
        return abs(self.count) == 1
    
    def __str__(self) -> str:
        if self.is_empty:
            return "0"
        return f"{abs(self.count)}{'W' if self.count > 0 else 'B'}"
    
    @classmethod
    def from_str(cls, s: str) -> 'Point':
        if s == "0":
            return cls()
        count = int(s[:-1])
        color = s[-1]
        return cls(count if color == 'W' else -count)

@dataclass
class GameState:
    board: List[Point]
    current_player: Player
    dice: Optional[Tuple[int, ...]]
    bar: Dict[Player, int]
    off: Dict[Player, int]
    game_over: bool = False
    move_count: int = 0
    remaining_doubles: Optional[int] = None
    
    def __post_init__(self):
        """Validate state on creation"""
        if len(self.board) != 24:
            raise ValueError("Board must have exactly 24 points")
        
        # Validate piece counts
        white_count = sum(p.count for p in self.board if p.count > 0)
        black_count = sum(-p.count for p in self.board if p.count < 0)
        white_total = white_count + self.bar[Player.WHITE] + self.off[Player.WHITE]
        black_total = black_count + self.bar[Player.BLACK] + self.off[Player.BLACK]
        
        if white_total > 15 or black_total > 15:
            raise ValueError("Invalid piece count")
    
    @classmethod
    def create_initial_state(cls) -> 'GameState':
        """Factory method for creating initial game state"""
        board = [Point() for _ in range(24)]
        
        # Standard backgammon starting position
        initial_position = {
            0: 2,    # Point 1  (2 white pieces)
            11: 5,   # Point 12 (5 white pieces)
            16: 3,   # Point 17 (3 white pieces)
            18: 5,   # Point 19 (5 white pieces)
            
            23: -2,  # Point 24 (2 black pieces)
            12: -5,  # Point 13 (5 black pieces)
            7: -3,   # Point 8  (3 black pieces)
            5: -5,   # Point 6  (5 black pieces)
        }
        
        for point_idx, count in initial_position.items():
            board[point_idx].count = count
            
        return cls(
            board=board,
            current_player=Player.WHITE,
            dice=None,
            bar={Player.WHITE: 0, Player.BLACK: 0},
            off={Player.WHITE: 0, Player.BLACK: 0}
        )
    
    def to_json(self) -> dict:
        """Convert state to JSON-serializable format for web client"""
        validator = MoveValidator(self)
        return {
            'board': [str(point) for point in self.board],
            'currentPlayer': self.current_player.value,
            'dice': list(self.dice) if self.dice else None,
            'bar': {
                'white': self.bar[Player.WHITE],
                'black': self.bar[Player.BLACK]
            },
            'off': {
                'white': self.off[Player.WHITE],
                'black': self.off[Player.BLACK]
            },
            'gameOver': self.game_over,
            'moveCount': self.move_count,
            'validMoves': [
                {
                    'from': move.from_point,
                    'to': move.to_point,
                    'dice': move.dice_value
                }
                for move in validator.get_valid_moves()
            ]
        }
    
    @classmethod
    def from_json(cls, data: dict) -> 'GameState':
        """Create GameState from JSON data"""
        try:
            state = cls(
                board=[Point.from_str(p) for p in data['board']],
                current_player=Player(data['currentPlayer']),
                dice=tuple(data['dice']) if data['dice'] else None,
                bar={
                    Player.WHITE: data['bar']['white'],
                    Player.BLACK: data['bar']['black']
                },
                off={
                    Player.WHITE: data['off']['white'],
                    Player.BLACK: data['off']['black']
                },
                game_over=data['gameOver'],
                move_count=data['moveCount']
            )
            state.__post_init__()  # Validate the loaded state
            return state
        except (KeyError, ValueError) as e:
            raise ValueError(f"Invalid game state data: {e}")