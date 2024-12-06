from dataclasses import dataclass
from typing import List, Optional, Tuple
from game.game_state import GameState
from game.player import Player

@dataclass(frozen=True)
class Move:
    """Immutable representation of a move"""
    from_point: int  # 0-23 for board, 24 for bar, -1 for bearing off
    to_point: int    # 0-23 for board, -1 for bearing off
    dice_value: int

    def __post_init__(self):
        """Validate move values on creation"""
        if self.from_point < -1 or self.from_point > 24:
            raise ValueError(f"Invalid from_point: {self.from_point}")
        if self.to_point < -1 or self.to_point > 23:
            raise ValueError(f"Invalid to_point: {self.to_point}")
        if not 1 <= self.dice_value <= 6:
            raise ValueError(f"Invalid dice_value: {self.dice_value}")

class MoveValidator:
    def __init__(self, state: GameState):
        self.state = state
        self._cached_moves = None
        self._cached_state_hash = None
    
    def get_valid_moves(self) -> List[Move]:
        """Get all valid moves with caching"""
        current_hash = hash(str(self.state))
        if self._cached_moves and current_hash == self._cached_state_hash:
            return self._cached_moves.copy()
            
        moves = self._calculate_valid_moves()
        self._cached_moves = moves
        self._cached_state_hash = current_hash
        return moves.copy()
    
    def _calculate_valid_moves(self) -> List[Move]:
        """Calculate all valid moves without caching"""
        if not self.state.dice:
            return []
            
        moves = []
        if self.state.bar[self.state.current_player] > 0:
            return self._get_bar_moves()
            
        return self._get_regular_moves()
    
    def _get_bar_moves(self) -> List[Move]:
        """Get valid moves from the bar"""
        moves = []
        for die in self._get_available_dice():
            entry_point = self._calculate_entry_point(die)
            if entry_point is not None:
                moves.append(Move(24, entry_point, die))
        return moves
    
    def _get_regular_moves(self) -> List[Move]:
        """Get valid moves from board positions"""
        moves = []
        for point_idx in range(24):
            if self.state.board[point_idx].color != self.state.current_player:
                continue
            for die in self._get_available_dice():
                target = self._calculate_target(point_idx, die)
                if target is not None:
                    moves.append(Move(point_idx, target, die))
        return moves
    
    def _get_available_dice(self) -> List[int]:
        """Get list of available dice values, handling doubles"""
        if not self.state.dice:
            return []
            
        if len(self.state.dice) == 2 and self.state.dice[0] == self.state.dice[1]:
            return [self.state.dice[0]] * (4 if self.state.remaining_doubles is None else self.state.remaining_doubles)
        return list(self.state.dice)
    
    def _calculate_entry_point(self, die: int) -> Optional[int]:
        """Calculate valid entry point from bar"""
        player = self.state.current_player
        if player == Player.WHITE:
            target = die - 1  # Convert to 0-based indexing
        else:
            target = 24 - die
            
        if self._is_valid_target(target):
            return target
        return None
    
    def _calculate_target(self, point_idx: int, die: int) -> Optional[int]:
        """Calculate target point for a move"""
        player = self.state.current_player
        direction = player.direction
        target = point_idx + (die * direction)
        
        # Regular move within bounds
        if 0 <= target < 24:
            if self._is_valid_target(target):
                return target
            return None
        
        # Bearing off
        if not self.can_bear_off():
            return None
            
        if player == Player.WHITE and target >= 24:
            if point_idx + die == 24 or self._no_pieces_behind(point_idx):
                return -1
        elif player == Player.BLACK and target < 0:
            if point_idx - die == -1 or self._no_pieces_behind(point_idx):
                return -1
                
        return None
    
    def _is_valid_target(self, target: int) -> bool:
        """Check if target point is valid for landing"""
        if not (0 <= target < 24):
            return False
            
        target_point = self.state.board[target]
        if target_point.is_empty:
            return True
            
        if target_point.color == self.state.current_player:
            return True
            
        return target_point.is_blot
    
    def _no_pieces_behind(self, point_idx: int) -> bool:
        """Check if there are no pieces behind the given point"""
        player = self.state.current_player
        if player == Player.WHITE:
            range_to_check = range(0, point_idx)
        else:
            range_to_check = range(point_idx + 1, 24)
            
        return all(
            self.state.board[i].color != player 
            for i in range_to_check
        )
    
    def can_bear_off(self) -> bool:
        """Check if current player can bear off"""
        player = self.state.current_player
        
        if self.state.bar[player] > 0:
            return False
            
        home_start = 18 if player == Player.BLACK else 0
        home_end = 24 if player == Player.BLACK else 6
        
        for i in range(24):
            point = self.state.board[i]
            if point.color == player:
                if player == Player.WHITE and i >= 6:
                    return False
                if player == Player.BLACK and i < 18:
                    return False
                    
        return True

class MoveExecutor:
    """Handles the execution of moves and state updates"""
    def __init__(self, state: GameState):
        self.state = state
    
    def execute_move(self, move: Move) -> bool:
        """Execute a move and update game state"""
        validator = MoveValidator(self.state)
        if move not in validator.get_valid_moves():
            return False
            
        self._update_board(move)
        self._update_dice_state(move)
        self._check_turn_end()
        return True
    
    def _update_board(self, move: Move) -> None:
        """Update board state for the move"""
        player = self.state.current_player
        
        # Remove piece from source
        if move.from_point == 24:
            self.state.bar[player] -= 1
        else:
            self.state.board[move.from_point].count += -1 if player == Player.WHITE else 1
        
        # Add piece to destination
        if move.to_point == -1:
            self.state.off[player] += 1
            if self.state.off[player] == 15:
                self.state.game_over = True
        else:
            target_point = self.state.board[move.to_point]
            if target_point.is_blot and target_point.color == player.opponent:
                target_point.count = 0
                self.state.bar[player.opponent] += 1
            target_point.count += 1 if player == Player.WHITE else -1
    
    def _update_dice_state(self, move: Move) -> None:
        """Update dice state after move"""
        if self.state.dice[0] == self.state.dice[1]:  # Doubles
            if self.state.remaining_doubles is None:
                self.state.remaining_doubles = 3
            else:
                self.state.remaining_doubles -= 1
                
            if self.state.remaining_doubles > 0:
                self.state.dice = (self.state.dice[0],) * self.state.remaining_doubles
            else:
                self.state.dice = None
                self.state.remaining_doubles = None
        else:
            dice_list = list(self.state.dice)
            dice_list.remove(move.dice_value)
            self.state.dice = tuple(dice_list) if dice_list else None
    
    def _check_turn_end(self) -> None:
        """Check if turn should end and update player"""
        validator = MoveValidator(self.state)
        if not self.state.dice or not validator.get_valid_moves():
            self.state.current_player = self.state.current_player.opponent
            self.state.dice = None
            self.state.remaining_doubles = None