from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Dict

class Player(Enum):
    WHITE = "white"
    BLACK = "black"
    
    @property
    def opponent(self) -> 'Player':
        return Player.BLACK if self == Player.WHITE else Player.WHITE

@dataclass(frozen=True)
class Point:
    count: int = 0
    
    @property
    def color(self) -> Optional[Player]:
        if self.count > 0:
            return Player.WHITE
        elif self.count < 0:
            return Player.BLACK
        return None
    
    @property
    def is_empty(self) -> bool:
        return self.count == 0
        
    @property
    def is_blot(self) -> bool:
        return abs(self.count) == 1

@dataclass(frozen=True)
class Move:
    from_point: int
    to_point: int
    dice_value: int
    
    def __post_init__(self):
        if not (-1 <= self.from_point <= 24):
            raise ValueError(f"Invalid from_point: {self.from_point}")
        if not (-1 <= self.to_point <= 24):
            raise ValueError(f"Invalid to_point: {self.to_point}")
        if not (1 <= self.dice_value <= 6):
            raise ValueError(f"Invalid dice_value: {self.dice_value}")

@dataclass(frozen=True)
class GameStateSnapshot:
    board_state: Tuple[int, ...]
    current_player: Player
    dice: Optional[Tuple[int, ...]]
    bar: Dict[Player, int]
    off: Dict[Player, int]
    game_over: bool
    move_count: int
    remaining_doubles: Optional[int]