from typing import List, Optional, Tuple, Dict
import random
from game.types import Player, Point, Move, GameStateSnapshot
from game.game_state import GameState
from game.move import MoveValidator, MoveExecutor
from game.utils.constants import MIN_DICE, MAX_DICE, DICE_COUNT
from game.exceptions import InvalidStateError, GameEngineError

class Game:
    """
    Core game logic implementation.
    Handles game state management and move execution.
    """
    def __init__(self):
        """Initialize a new game with starting position"""
        self.state = GameState.create_initial_state()
        self.move_validator = MoveValidator(self.state)
        self.move_executor = MoveExecutor(self.state)
        self._validate_initial_state()

    def _validate_initial_state(self) -> None:
        """Ensure initial game state is valid"""
        if not self.state.validate_state():
            raise InvalidStateError("Invalid initial game state")

    def make_move(self, move: Move) -> bool:
        """
        Execute a move and update game state
        Args:
            move: The move to execute
        Returns:
            bool: True if move was successful
        """
        if self.state.game_over:
            return False

        if not self._is_valid_move(move):
            return False

        return self.move_executor.execute_move(move)

    def _is_valid_move(self, move: Move) -> bool:
        """
        Validate a move against current game state
        Args:
            move: The move to validate
        Returns:
            bool: True if move is valid
        """
        return move in self.get_valid_moves()

    def get_valid_moves(self) -> List[Move]:
        """
        Get all valid moves for current player
        Returns:
            List[Move]: List of valid moves
        """
        if self.state.game_over:
            return []
        return self.move_validator.get_valid_moves()

    def roll_dice(self) -> Tuple[int, int]:
        """
        Roll dice and update game state
        Returns:
            Tuple[int, int]: The rolled dice values
        Raises:
            InvalidStateError: If dice cannot be rolled now
        """
        if self.state.dice is not None:
            raise InvalidStateError("Dice have already been rolled")
        
        if self.state.game_over:
            raise InvalidStateError("Game is over")

        dice = self._generate_dice_roll()
        self.state.dice = dice
        
        # Handle doubles
        if dice[0] == dice[1]:
            self.state.remaining_doubles = 4

        return dice

    def _generate_dice_roll(self) -> Tuple[int, int]:
        """Generate a random dice roll"""
        return (
            random.randint(MIN_DICE, MAX_DICE),
            random.randint(MIN_DICE, MAX_DICE)
        )

    def get_state(self) -> Dict:
        """
        Get complete game state for external use
        Returns:
            Dict: Current game state
        """
        valid_moves = self.get_valid_moves()
        return {
            'board': [str(point) for point in self.state.board],
            'current_player': self.state.current_player.value,
            'dice': self.state.dice,
            'bar': self.state.bar,
            'off': self.state.off,
            'game_over': self.state.game_over,
            'valid_moves': [
                {
                    'from': move.from_point,
                    'to': move.to_point,
                    'dice': move.dice_value
                }
                for move in valid_moves
            ],
            'can_roll': self.can_roll_dice(),
            'remaining_doubles': self.state.remaining_doubles
        }

    def can_roll_dice(self) -> bool:
        """Check if dice can be rolled"""
        return (
            not self.state.game_over and
            self.state.dice is None
        )

    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.state.game_over

    def get_winner(self) -> Optional[Player]:
        """Get the winner if game is over"""
        if not self.state.game_over:
            return None
        
        for player in Player:
            if self.state.off[player] == 15:
                return player
        return None

    def can_bear_off(self, player: Player) -> bool:
        """Check if player can bear off pieces"""
        return self.move_validator.can_bear_off()

    def get_pip_count(self, player: Player) -> int:
        """
        Calculate pip count for a player
        Args:
            player: Player to calculate for
        Returns:
            int: Total pip count
        """
        pip_count = 0
        multiplier = 1 if player == Player.WHITE else -1
        
        # Count board pieces
        for i, point in enumerate(self.state.board):
            if point.color == player:
                distance = 24 - i if player == Player.BLACK else i + 1
                pip_count += abs(point.count) * distance
        
        # Add bar pieces
        if self.state.bar[player] > 0:
            distance = 24 if player == Player.BLACK else 1
            pip_count += self.state.bar[player] * distance
        
        return pip_count

    def reset(self) -> None:
        """Reset the game to initial state"""
        self.state = GameState.create_initial_state()
        self.move_validator = MoveValidator(self.state)
        self.move_executor = MoveExecutor(self.state)
        self._validate_initial_state()