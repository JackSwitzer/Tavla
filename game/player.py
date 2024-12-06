from enum import Enum
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

class Player(Enum):
    WHITE = "white"
    BLACK = "black"
    
    @property
    def opponent(self) -> 'Player':
        """Get the opposing player"""
        return Player.BLACK if self == Player.WHITE else Player.WHITE
    
    @property
    def direction(self) -> int:
        """Movement direction: positive for white, negative for black"""
        return 1 if self == Player.WHITE else -1
    
    @property
    def home_board_range(self) -> Tuple[int, int]:
        """Get the range of points in player's home board"""
        return (0, 6) if self == Player.WHITE else (18, 24)
    
    @property
    def entry_point_calculator(self) -> callable:
        """Get function to calculate entry point from bar"""
        return (lambda die: die - 1) if self == Player.WHITE else (lambda die: 24 - die)

@dataclass
class PlayerState:
    """Track player-specific state"""
    bar_count: int = 0
    off_count: int = 0
    
    def can_bear_off(self, board: list, player: Player) -> bool:
        """Check if player can bear off pieces"""
        if self.bar_count > 0:
            return False
            
        home_start, home_end = player.home_board_range
        
        # All pieces must be in home board or already borne off
        pieces_accounted = self.off_count
        for i in range(24):
            point = board[i]
            if point.color == player:
                if home_start <= i < home_end:
                    pieces_accounted += abs(point.count)
                else:
                    return False
                    
        return pieces_accounted == 15

class PlayerManager:
    """Manages player states and transitions"""
    def __init__(self):
        self.states: Dict[Player, PlayerState] = {
            Player.WHITE: PlayerState(),
            Player.BLACK: PlayerState()
        }
        self.current_player: Player = Player.WHITE
    
    def switch_player(self) -> None:
        """Switch to the other player"""
        self.current_player = self.current_player.opponent
    
    def get_player_state(self, player: Optional[Player] = None) -> PlayerState:
        """Get state for specified player or current player"""
        return self.states[player or self.current_player]
    
    def add_to_bar(self, player: Player) -> None:
        """Add a piece to player's bar"""
        self.states[player].bar_count += 1
    
    def remove_from_bar(self, player: Player) -> None:
        """Remove a piece from player's bar"""
        if self.states[player].bar_count > 0:
            self.states[player].bar_count -= 1
    
    def add_to_off(self, player: Player) -> None:
        """Add a piece to player's off (borne off pieces)"""
        self.states[player].off_count += 1
    
    def has_won(self, player: Player) -> bool:
        """Check if player has won"""
        return self.states[player].off_count == 15
