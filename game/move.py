from typing import List, Optional, Protocol, Set, Tuple
from game.types import Move, Player, Point
from game.utils.constants import BOARD_POINTS, BAR_POINT, OFF_POINT, BEARING_OFF_THRESHOLD
from game.exceptions import InvalidMoveError

class GameStateProtocol(Protocol):
    """Protocol defining required GameState interface for move validation"""
    board: List[Point]
    current_player: Player
    dice: Optional[Tuple[int, ...]]
    bar: dict[Player, int]
    off: dict[Player, int]
    remaining_doubles: Optional[int]

class MoveValidator:
    """Validates moves according to backgammon rules"""
    
    def __init__(self, state: GameStateProtocol):
        self.state = state
        self._cached_moves: Optional[List[Move]] = None
        self._cached_state_hash: Optional[int] = None

    def get_valid_moves(self) -> List[Move]:
        """
        Get all valid moves for current state with caching
        Returns:
            List[Move]: List of valid moves
        """
        current_hash = self._calculate_state_hash()
        if self._cached_moves is not None and current_hash == self._cached_state_hash:
            return self._cached_moves.copy()

        moves = self._calculate_valid_moves()
        self._cached_moves = moves
        self._cached_state_hash = current_hash
        return moves.copy()

    def _calculate_state_hash(self) -> int:
        """Calculate hash of current state for cache invalidation"""
        state_tuple = (
            tuple(point.count for point in self.state.board),
            self.state.current_player,
            self.state.dice,
            tuple(sorted(self.state.bar.items())),
            tuple(sorted(self.state.off.items())),
            self.state.remaining_doubles
        )
        return hash(state_tuple)

    def _calculate_valid_moves(self) -> List[Move]:
        """Calculate all valid moves for current state"""
        if not self.state.dice:
            return []

        moves: List[Move] = []
        
        # Must move from bar first
        if self.state.bar[self.state.current_player] > 0:
            return self._get_bar_moves()

        # Regular moves or bearing off
        if self.can_bear_off():
            moves.extend(self._get_bearing_off_moves())
        
        moves.extend(self._get_regular_moves())
        return moves

    def _get_bar_moves(self) -> List[Move]:
        """Get valid moves from the bar"""
        moves = []
        for die in self._get_available_dice():
            entry_point = self._calculate_entry_point(die)
            if entry_point is not None:
                moves.append(Move(BAR_POINT, entry_point, die))
        return moves

    def _get_regular_moves(self) -> List[Move]:
        """Get valid moves from board positions"""
        moves = []
        for point_idx in range(BOARD_POINTS):
            point = self.state.board[point_idx]
            if point.color != self.state.current_player:
                continue
                
            for die in self._get_available_dice():
                target = self._calculate_target_point(point_idx, die)
                if target is not None:
                    moves.append(Move(point_idx, target, die))
        return moves

    def _get_bearing_off_moves(self) -> List[Move]:
        """Get valid bearing off moves"""
        moves = []
        player = self.state.current_player
        home_range = range(0, 6) if player == Player.WHITE else range(18, 24)
        
        for point_idx in home_range:
            point = self.state.board[point_idx]
            if point.color != player:
                continue
                
            for die in self._get_available_dice():
                if self._is_valid_bearing_off_move(point_idx, die):
                    moves.append(Move(point_idx, OFF_POINT, die))
        return moves

    def _get_available_dice(self) -> Set[int]:
        """Get set of available dice values"""
        if not self.state.dice:
            return set()
            
        if len(self.state.dice) == 2 and self.state.dice[0] == self.state.dice[1]:
            return {self.state.dice[0]}
        return set(self.state.dice)

    def _calculate_entry_point(self, die: int) -> Optional[int]:
        """Calculate valid entry point from bar"""
        player = self.state.current_player
        target = die - 1 if player == Player.WHITE else BOARD_POINTS - die
        
        if self._is_valid_landing(target):
            return target
        return None

    def _calculate_target_point(self, from_point: int, die: int) -> Optional[int]:
        """Calculate target point for a regular move"""
        player = self.state.current_player
        direction = 1 if player == Player.WHITE else -1
        target = from_point + (die * direction)
        
        if 0 <= target < BOARD_POINTS and self._is_valid_landing(target):
            return target
        return None

    def _is_valid_landing(self, point_idx: int) -> bool:
        """Check if a point is a valid landing spot"""
        if not (0 <= point_idx < BOARD_POINTS):
            return False
            
        target_point = self.state.board[point_idx]
        if target_point.color == self.state.current_player:
            return True
            
        return target_point.is_empty or target_point.is_blot

    def _is_valid_bearing_off_move(self, point_idx: int, die: int) -> bool:
        """Check if bearing off move is valid"""
        player = self.state.current_player
        if player == Player.WHITE:
            exact_roll = die == point_idx + 1
            higher_roll = die > point_idx + 1
        else:
            exact_roll = die == (24 - point_idx)
            higher_roll = die > (24 - point_idx)
            
        if exact_roll:
            return True
            
        if higher_roll and self._no_pieces_behind(point_idx):
            return True
            
        return False

    def _no_pieces_behind(self, point_idx: int) -> bool:
        """Check if there are no pieces behind given point"""
        player = self.state.current_player
        if player == Player.WHITE:
            check_range = range(0, point_idx)
        else:
            check_range = range(point_idx + 1, BOARD_POINTS)
            
        return all(
            self.state.board[i].color != player 
            for i in check_range
        )

    def can_bear_off(self) -> bool:
        """Check if current player can bear off"""
        player = self.state.current_player
        
        if self.state.bar[player] > 0:
            return False
            
        home_start = 18 if player == Player.BLACK else 0
        home_end = 24 if player == Player.BLACK else 6
        
        # Check if all pieces are in home board or off
        for i in range(BOARD_POINTS):
            point = self.state.board[i]
            if point.color == player:
                if home_start <= i < home_end:
                    continue
                return False
        return True

class MoveExecutor:
    """Executes moves and updates game state"""
    
    def __init__(self, state: GameStateProtocol):
        self.state = state

    def execute_move(self, move: Move) -> bool:
        """
        Execute a move and update game state
        Args:
            move: Move to execute
        Returns:
            bool: True if move was successful
        """
        if not self._is_valid_move(move):
            return False

        self._update_board(move)
        self._update_dice_state(move.dice_value)
        return True

    def _is_valid_move(self, move: Move) -> bool:
        """Validate move before execution"""
        validator = MoveValidator(self.state)
        return move in validator.get_valid_moves()

    def _update_board(self, move: Move) -> None:
        """Update board state for move"""
        player = self.state.current_player
        
        # Remove piece from source
        if move.from_point == BAR_POINT:
            self.state.bar[player] -= 1
        else:
            self.state.board[move.from_point].count += -1 if player == Player.WHITE else 1
        
        # Add piece to destination
        if move.to_point == OFF_POINT:
            self.state.off[player] += 1
            if self.state.off[player] == 15:
                self.state.game_over = True
        else:
            target = self.state.board[move.to_point]
            if target.is_blot and target.color == player.opponent:
                # Capture opponent's blot
                self.state.bar[player.opponent] += 1
                target.count = 0
            
            target.count += 1 if player == Player.WHITE else -1

    def _update_dice_state(self, used_value: int) -> None:
        """Update dice state after move"""
        if not self.state.dice:
            return
            
        if len(self.state.dice) == 2 and self.state.dice[0] == self.state.dice[1]:
            if self.state.remaining_doubles is None:
                self.state.remaining_doubles = 3
            else:
                self.state.remaining_doubles -= 1
                
            if self.state.remaining_doubles == 0:
                self.state.dice = None
                self.state.remaining_doubles = None
        else:
            dice_list = list(self.state.dice)
            dice_list.remove(used_value)
            self.state.dice = tuple(dice_list) if dice_list else None