from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

class Player(Enum):
    WHITE = "white"
    BLACK = "black"
    
    @property
    def opponent(self) -> 'Player':
        return Player.BLACK if self == Player.WHITE else Player.WHITE

class Point:
    def __init__(self):
        self.count: int = 0  # Positive for white, negative for black
        
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

@dataclass
class GameState:
    board: List[Point]
    current_player: Player
    dice: Optional[Tuple[int, int]]
    bar: Dict[Player, int]
    off: Dict[Player, int]
    game_over: bool

class Game:
    def __init__(self):
        self.state = self.initialize_state()
        self._moves_cache = {}  # Add cache for valid moves

    def cleanup(self):
        """Clean up any resources before game is destroyed"""
        # Clear caches and references
        self._moves_cache.clear()
        self.state.board.clear()
        self.state.bar.clear()
        self.state.off.clear()
        self.state = None

    def initialize_state(self) -> GameState:
        """Reset to fresh game state"""
        # Clear any existing state
        if hasattr(self, 'state') and self.state:
            self.cleanup()
            
        # Initialize fresh board
        board = [Point() for _ in range(24)]
        
        # Set up initial position with validation
        initial_position = {
            # White pieces (positive numbers)
            0: 2,    # Point 1  (2 white pieces)
            11: 5,   # Point 12 (5 white pieces)
            16: 3,   # Point 17 (3 white pieces)
            18: 5,   # Point 19 (5 white pieces)
            
            # Black pieces (negative numbers)
            23: -2,  # Point 24 (2 black pieces)
            12: -5,  # Point 13 (5 black pieces)
            7: -3,   # Point 8  (3 black pieces)
            5: -5,   # Point 6  (5 black pieces)
        }
        
        # Verify total pieces (15 per player)
        white_total = sum(count for count in initial_position.values() if count > 0)
        black_total = abs(sum(count for count in initial_position.values() if count < 0))
        
        assert white_total == 15, f"Invalid white piece count: {white_total}"
        assert black_total == 15, f"Invalid black piece count: {black_total}"
        
        # Initialize board state
        for point_idx, count in initial_position.items():
            board[point_idx].count = count

        return GameState(
            board=board,
            current_player=Player.WHITE,
            dice=None,
            bar={Player.WHITE: 0, Player.BLACK: 0},
            off={Player.WHITE: 0, Player.BLACK: 0},
            game_over=False
        )

    def get_state(self):
        """Get current game state"""
        if not self.state:
            self.state = self.initialize_state()
        return {
            'board': [point.count for point in self.state.board],
            'current_player': self.state.current_player.value,
            'dice': self.state.dice,  # Ensure dice are included in state
            'bar': {
                'white': self.state.bar[Player.WHITE],
                'black': self.state.bar[Player.BLACK]
            },
            'off': {
                'white': self.state.off[Player.WHITE],
                'black': self.state.off[Player.BLACK]
            },
            'game_over': self.state.game_over
        }

    def is_valid_move(self, from_point: int, to_point: int, color: str) -> bool:
        player = Player(color)
        board = self.state.board
        
        # Convert points to 0-based indexing
        from_idx = from_point - 1
        to_idx = to_point - 1
        
        # Basic validation checks
        if not (0 <= from_idx < 24 and 0 <= to_idx < 24):
            return False
            
        # Check if moving piece belongs to the current player
        if player == Player.WHITE and board[from_idx].count <= 0:
            return False
        if player == Player.BLACK and board[from_idx].count >= 0:
            return False
            
        # Check if destination is blocked
        dest_point = board[to_idx]
        if dest_point.color is not None and dest_point.color != player and abs(dest_point.count) > 1:
            return False
            
        # Check if there are pieces on the bar that must be moved first
        if self.state.bar[player] > 0 and from_point != 25:  # 25 represents the bar
            return False
            
        return True

    def move_checker(self, from_point: int, to_point: int, color: str) -> bool:
        if not self.is_valid_move(from_point, to_point, color):
            return False
            
        player = Player(color)
        from_idx = from_point - 1
        to_idx = to_point - 1
        board = self.state.board
        
        # Remove piece from source
        board[from_idx].count += -1 if player == Player.WHITE else 1
        
        # If hitting an opponent's blot
        dest_point = board[to_idx]
        if dest_point.is_blot and dest_point.color == player.opponent:
            board[to_idx].count = 0
            self.state.bar[player.opponent] += 1
            
        # Add piece to destination
        board[to_idx].count += 1 if player == Player.WHITE else -1
        
        # Update current player
        self.state.current_player = player.opponent
        
        return True

    def roll_dice(self) -> Tuple[int, int]:
        """Roll two dice and store the result in the game state"""
        import random
        if self.state.dice:
            raise ValueError("Dice already rolled")
        
        self.state.dice = (random.randint(1, 6), random.randint(1, 6))
        return self.state.dice

    def can_bear_off(self, color: str) -> bool:
        """Check if the player can bear off pieces"""
        player = Player(color)
        board = self.state.board
        
        if player == Player.WHITE:
            # Check if all white pieces are in home board (last 6 points)
            return all(point.count <= 0 for point in board[:18])
        else:
            # Check if all black pieces are in home board (first 6 points)
            return all(point.count >= 0 for point in board[6:])

    def get_valid_moves(self) -> List[Dict[str, int]]:
        """Return list of valid moves based on current dice roll"""
        if not self.state.dice:
            return []
        
        current_player = self.state.current_player
        moves = []
        dice_values = list(self.state.dice)
        
        # If doubles, we have four moves with the same value
        if len(dice_values) == 2 and dice_values[0] == dice_values[1]:
            dice_values *= 2

        # Check if player has pieces on the bar
        if self.state.bar[current_player] > 0:
            # Can only move from bar
            for die in dice_values:
                entry_point = self._get_entry_point(die, current_player)
                if entry_point is not None:
                    moves.append({
                        'from': 25,  # 25 represents the bar
                        'to': entry_point,
                        'dice_value': die
                    })
            return moves

        # Regular moves
        for point_idx in range(24):
            point = self.state.board[point_idx]
            
            # Skip if point is empty or belongs to opponent
            if point.is_empty or point.color != current_player:
                continue

            for die in dice_values:
                target_idx = self._get_target_point(point_idx, die, current_player)
                
                # Skip if move is not possible
                if target_idx is None:
                    continue
                    
                # Check if move is valid
                if self._is_valid_target(target_idx, current_player):
                    moves.append({
                        'from': point_idx + 1,  # Convert to 1-based indexing
                        'to': target_idx + 1,
                        'dice_value': die
                    })

        # Add bearing off moves if possible
        if self.can_bear_off(current_player.value):
            moves.extend(self._get_bearing_off_moves(current_player, dice_values))

        return moves

    def _get_entry_point(self, die: int, player: Player) -> Optional[int]:
        """Calculate entry point from bar"""
        if player == Player.WHITE:
            target = die - 1
        else:
            target = 24 - die
        
        if self._is_valid_target(target, player):
            return target + 1  # Convert to 1-based indexing
        return None

    def _get_target_point(self, point_idx: int, die: int, player: Player) -> Optional[int]:
        """Calculate target point for a move"""
        if player == Player.WHITE:
            target = point_idx + die
            if target >= 24:  # Beyond the board
                return None if not self.can_bear_off(player.value) else target
        else:
            target = point_idx - die
            if target < 0:  # Beyond the board
                return None if not self.can_bear_off(player.value) else target
        return target

    def _is_valid_target(self, target_idx: int, player: Player) -> bool:
        """Check if target point is a valid destination"""
        if not (0 <= target_idx < 24):
            return False
        
        point = self.state.board[target_idx]
        
        # Point is empty or has only one opponent piece
        if point.is_empty or point.is_blot:
            return True
        
        # Point has multiple pieces but belongs to current player
        return point.color == player

    def _get_bearing_off_moves(self, player: Player, dice_values: List[int]) -> List[Dict[str, int]]:
        """Get valid bearing off moves"""
        moves = []
        
        if player == Player.WHITE:
            home_board = range(18, 24)
            beyond_board = 24
        else:
            home_board = range(0, 6)
            beyond_board = -1

        for point_idx in home_board:
            point = self.state.board[point_idx]
            if point.color != player:
                continue
            
            for die in dice_values:
                target = self._get_target_point(point_idx, die, player)
                
                # Exact roll to bear off
                if target == beyond_board:
                    moves.append({
                        'from': point_idx + 1,
                        'to': 0,  # 0 represents bearing off
                        'dice_value': die
                    })
                # Larger roll when no pieces are further from home
                elif (target > beyond_board and player == Player.WHITE) or \
                     (target < beyond_board and player == Player.BLACK):
                    if self._is_furthest_piece(point_idx, player):
                        moves.append({
                            'from': point_idx + 1,
                            'to': 0,
                            'dice_value': die
                        })
                    
        return moves

    def _is_furthest_piece(self, point_idx: int, player: Player) -> bool:
        """Check if the piece at point_idx is the furthest from home"""
        if player == Player.WHITE:
            search_range = range(0, point_idx)
        else:
            search_range = range(point_idx + 1, 24)
        
        return all(self.state.board[i].color != player for i in search_range)