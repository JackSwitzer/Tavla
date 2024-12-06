from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict
import random
from game.player import Player
from game.game_state import Point, Move, GameStateSnapshot, GameState
from game.game_manager import GameStateManager
from game.move import MoveValidator
from game.move import MoveExecutor

class Game:
    def __init__(self):
        """Initialize a new game"""
        self._moves_cache = {}
        self.history = []
        self.state = GameState.create_initial_state()
        self.state_manager = GameStateManager()
        self.move_validator = MoveValidator(self.state)
        self.move_executor = MoveExecutor(self.state)
        
        # Store initial position
        self.state_manager.push_state(self.state)
        self.history.append(self.get_fen_position())

    def make_move(self, move: Move) -> bool:
        """Execute a move and update game state"""
        if self.state.game_over:
            return False
            
        success = self.move_executor.execute_move(move)
        if success:
            self.state_manager.push_state(self.state)
            self._moves_cache.clear()  # Invalidate cache
            self.history.append(self.get_fen_position())
            
        return success

    def get_valid_moves(self) -> List[Move]:
        """Get all valid moves for current player with caching"""
        cache_key = self.get_fen_position()
        if cache_key in self._moves_cache:
            return self._moves_cache[cache_key]
            
        moves = self.move_validator.get_valid_moves()
        self._moves_cache[cache_key] = moves
        return moves

    def _calculate_target(self, point_idx: int, die: int, player: Player) -> Optional[int]:
        """Calculate target point for a move, considering direction and bearing off"""
        direction = player.direction
        target = point_idx + (die * direction)
        
        # Validate target is within board bounds
        if 0 <= target < 24:
            return target
        
        # Handle bearing off
        if self.can_bear_off(player):
            if player == Player.WHITE and target >= 24:
                if point_idx + die == 24 or all(
                    self.state.board[i].color != player 
                    for i in range(point_idx + 1, 24)):
                    return -1
            elif player == Player.BLACK and target < 0:
                if point_idx - die == -1 or all(
                    self.state.board[i].color != player 
                    for i in range(0, point_idx)):
                    return -1
        return None

    def _is_valid_target(self, target_idx: int, player: Player) -> bool:
        """Check if target point is a valid destination"""
        if target_idx == -1:  # Bearing off
            return self.can_bear_off(player)
            
        point = self.state.board[target_idx]
        return (point.is_empty or 
                point.color == player or 
                point.is_blot)

    def _check_game_over(self) -> None:
        """Check if the game is over"""
        for player in Player:
            if self.state.off[player] == 15:
                self.state.game_over = True
                break

    def get_fen_position(self) -> str:
        """Convert current position to FEN format"""
        # Convert board to FEN notation
        pieces = []
        empty_count = 0
        
        for point in self.state.board:
            if point.is_empty:
                empty_count += 1
            else:
                if empty_count > 0:
                    pieces.append(str(empty_count))
                    empty_count = 0
                count = abs(point.count)
                color = 'W' if point.count > 0 else 'B'
                pieces.append(f"{count}{color}")
        
        if empty_count > 0:
            pieces.append(str(empty_count))
        
        # Active color
        active = 'W' if self.state.current_player == Player.WHITE else 'B'
        
        # Bar pieces in hex
        bar_white = hex(self.state.bar[Player.WHITE])[2:].upper()
        bar_black = hex(self.state.bar[Player.BLACK])[2:].upper()
        
        # Move number
        move_number = self.state.move_count
        
        # Dice values
        dice = ''.join(str(d) if d else '0' for d in (self.state.dice or (0, 0)))
        
        return f"{'-'.join(pieces)} {active} {bar_white}{bar_black} {move_number} {dice}"

    def load_fen_position(self, fen: str) -> None:
        """Load position from FEN string"""
        try:
            pieces, active, bar, move_number, dice = fen.split()
            
            # Reset board
            self.state.board = [Point() for _ in range(24)]
            
            # Load pieces
            current_point = 0
            for piece in pieces.split('-'):
                if piece.isdigit():
                    current_point += int(piece)
                else:
                    count = int(piece[:-1])
                    color = 1 if piece[-1] == 'W' else -1
                    self.state.board[current_point].count = count * color
                    current_point += 1
            
            # Set active player
            self.state.current_player = Player.WHITE if active == 'W' else Player.BLACK
            
            # Set bar pieces
            self.state.bar[Player.WHITE] = int(bar[0], 16)
            self.state.bar[Player.BLACK] = int(bar[1], 16)
            
            # Set move number
            self.state.move_count = int(move_number)
            
            # Set dice
            if dice != '00':
                self.state.dice = (int(dice[0]), int(dice[1]))
            else:
                self.state.dice = None
                
        except Exception as e:
            raise ValueError(f"Invalid FEN format: {e}")

    def get_score(self) -> Dict[Player, int]:
        """Calculate current score for each player"""
        scores = {Player.WHITE: 0, Player.BLACK: 0}
        
        for player in Player:
            # Points for bearing off
            scores[player] += self.state.off[player] * 2
            
            # Points for home board position
            home_start = 0 if player == Player.WHITE else 18
            home_end = 6 if player == Player.WHITE else 24
            
            for i in range(home_start, home_end):
                point = self.state.board[i]
                if point.color == player:
                    scores[player] += abs(point.count)
                    
            # Penalty for pieces on bar
            scores[player] -= self.state.bar[player] * 3
            
        return scores

    def _get_entry_point(self, die: int, player: Player) -> Optional[int]:
        """Calculate entry point when moving from bar"""
        if player == Player.WHITE:
            target = die - 1  # Convert from 1-based to 0-based indexing
        else:
            target = 24 - die
            
        if self._is_valid_target(target, player):
            return target
        return None

    def can_bear_off(self, player: Player) -> bool:
        """Check if player can bear off pieces"""
        # Must have no pieces on bar
        if self.state.bar[player] > 0:
            return False
            
        # All remaining pieces must be in home board
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

    def _is_valid_move(self, move: Move) -> bool:
        """Validate a proposed move"""
        player = self.state.current_player
        
        # Verify dice value is available
        if not self.state.dice or move.dice_value not in self.state.dice:
            return False
        
        # Must move from bar first
        if self.state.bar[player] > 0:
            return move.from_point == 24
        
        # Verify source point
        if not (0 <= move.from_point < 24):
            return False
        source_point = self.state.board[move.from_point]
        if source_point.color != player:
            return False
        
        # Verify target point
        if move.to_point == -1:  # Bearing off
            if not self.can_bear_off(player):
                return False
        else:
            if not (0 <= move.to_point < 24):
                return False
            target_point = self.state.board[move.to_point]
            if not target_point.is_empty and target_point.color != player and not target_point.is_blot:
                return False
        
        # Verify move direction
        direction = player.direction
        if move.to_point != -1 and (move.to_point - move.from_point) * direction <= 0:
            return False
        
        return True

    def roll_dice(self) -> Tuple[int, int]:
        """Roll two dice and update game state"""
        dice = (random.randint(1, 6), random.randint(1, 6))
        self.state.dice = dice
        return dice

    def get_state(self) -> dict:
        """Get complete game state for frontend"""
        return {
            'board': [str(point) for point in self.state.board],
            'current_player': self.state.current_player.value,
            'dice': self.state.dice,
            'bar': {
                'white': self.state.bar[Player.WHITE],
                'black': self.state.bar[Player.BLACK]
            },
            'off': {
                'white': self.state.off[Player.WHITE],
                'black': self.state.off[Player.BLACK]
            },
            'game_over': self.state.game_over,
            'move_count': self.state.move_count,
            'valid_moves': [
                {
                    'from': move.from_point,
                    'to': move.to_point,
                    'dice': move.dice_value
                }
                for move in self.get_valid_moves()
            ]
        }

    def undo_move(self) -> bool:
        """Undo the last move"""
        if len(self.history) < 2:  # Need at least 2 positions to undo
            return False
            
        # Remove current position
        self.history.pop()
        # Load previous position
        previous_position = self.history[-1]
        self.load_fen_position(previous_position)
        return True

    def load_from_snapshot(self, snapshot: GameStateSnapshot) -> None:
        """Load game state from a snapshot"""
        self.state = GameState(
            board=[Point() for _ in range(24)],
            current_player=snapshot.current_player,
            dice=snapshot.dice,
            bar=snapshot.bar.copy(),
            off=snapshot.off.copy(),
            game_over=snapshot.game_over,
            move_count=snapshot.move_count,
            remaining_doubles=snapshot.remaining_doubles
        )
        
        # Restore board state
        for i, count in enumerate(snapshot.board_state):
            self.state.board[i].count = count