from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Callable, Dict, List, Any, Set
from game.types import Player, Move, GameStateSnapshot, Point
from game.game import Game
from game.exceptions import GameEngineError, InvalidMoveError, InvalidStateError

class GamePhase(Enum):
    """Represents the current phase of a player's turn"""
    WAITING_FOR_ROLL = auto()
    MOVING = auto()
    TURN_END = auto()

class GameEvent(Enum):
    """All possible game events that can be subscribed to"""
    GAME_START = auto()
    DICE_ROLLED = auto()
    MOVE_MADE = auto()
    TURN_START = auto()
    TURN_END = auto()
    GAME_OVER = auto()
    STATE_CHANGED = auto()
    AI_THINKING = auto()
    AI_MOVED = auto()
    PIECE_CAPTURED = auto()
    BEARING_OFF = auto()

@dataclass
class GameConfig:
    """Configuration settings for the game engine"""
    ai_enabled: bool = False
    ai_difficulty: str = "medium"
    validate_moves: bool = True
    auto_save: bool = False
    enforce_rules: bool = True
    max_moves_history: int = 1000

class GameEngine:
    """
    Central coordinator for the backgammon game system.
    Handles game flow, rule enforcement, and event coordination.
    """
    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        self.game = Game()
        self.current_phase = GamePhase.WAITING_FOR_ROLL
        self.subscribers: Dict[GameEvent, List[Callable[[Any], None]]] = {
            event: [] for event in GameEvent
        }
        self.move_history: List[Move] = []
        self.state_history: List[GameStateSnapshot] = []
        self._initialize_game()

    def _initialize_game(self) -> None:
        """Initialize or reset the game state"""
        self.state_history = [self.game.state.to_snapshot()]
        self.move_history.clear()
        self.current_phase = GamePhase.WAITING_FOR_ROLL
        self._emit_event(GameEvent.GAME_START)

    def subscribe(self, event: GameEvent, callback: Callable[[Any], None]) -> None:
        """Subscribe to a game event"""
        self.subscribers[event].append(callback)

    def _emit_event(self, event: GameEvent, data: Any = None) -> None:
        """Emit an event to all subscribers"""
        for callback in self.subscribers[event]:
            callback(data)

    def roll_dice(self) -> tuple[int, int]:
        """
        Roll the dice if it's allowed in the current game phase
        Returns: Tuple of two dice values
        """
        if self.current_phase != GamePhase.WAITING_FOR_ROLL:
            raise InvalidStateError("Cannot roll dice in current phase")
        
        dice = self.game.roll_dice()
        self.current_phase = GamePhase.MOVING
        self._emit_event(GameEvent.DICE_ROLLED, dice)
        
        # Check if any moves are possible
        if not self.get_valid_moves():
            self._handle_no_valid_moves()
        
        return dice

    def make_move(self, move: Move) -> bool:
        """
        Attempt to make a move
        Returns: True if move was successful
        """
        if self.current_phase != GamePhase.MOVING:
            raise InvalidStateError("Cannot make move in current phase")

        if not self._validate_move(move):
            return False

        success = self.game.make_move(move)
        if success:
            self.move_history.append(move)
            self._emit_event(GameEvent.MOVE_MADE, move)
            self._update_game_phase()
            self._save_state()
        
        return success

    def _validate_move(self, move: Move) -> bool:
        """Validate if a move is legal"""
        if not self.config.enforce_rules:
            return True
            
        valid_moves = self.get_valid_moves()
        return move in valid_moves

    def _update_game_phase(self) -> None:
        """Update the game phase based on current state"""
        if not self.game.state.dice:
            self._end_turn()
        elif not self.get_valid_moves():
            self._handle_no_valid_moves()

    def _end_turn(self) -> None:
        """Handle end of turn logic"""
        self.current_phase = GamePhase.WAITING_FOR_ROLL
        self._emit_event(GameEvent.TURN_END)
        
        if self._check_game_over():
            self._emit_event(GameEvent.GAME_OVER, self.get_winner())
        else:
            self._emit_event(GameEvent.TURN_START)

    def _handle_no_valid_moves(self) -> None:
        """Handle situation when no valid moves are available"""
        self.game.state.dice = None
        self._end_turn()

    def get_valid_moves(self) -> List[Move]:
        """Get all valid moves for current state"""
        return self.game.get_valid_moves()

    def _check_game_over(self) -> bool:
        """Check if the game is over"""
        for player in Player:
            if self.game.state.off[player] == 15:
                return True
        return False

    def get_winner(self) -> Optional[Player]:
        """Get the winner if game is over"""
        for player in Player:
            if self.game.state.off[player] == 15:
                return player
        return None

    def _save_state(self) -> None:
        """Save current state to history"""
        snapshot = self.game.state.to_snapshot()
        self.state_history.append(snapshot)
        
        # Maintain history size limit
        if len(self.state_history) > self.config.max_moves_history:
            self.state_history.pop(0)

    def undo_move(self) -> bool:
        """
        Undo the last move if possible
        Returns: True if undo was successful
        """
        if len(self.state_history) < 2:
            return False

        self.state_history.pop()  # Remove current state
        previous_state = self.state_history[-1]
        self.game.state = GameState.from_snapshot(previous_state)
        
        if self.move_history:
            self.move_history.pop()
        
        self._emit_event(GameEvent.STATE_CHANGED)
        return True

    def get_game_state(self) -> dict:
        """Get complete game state for UI/external use"""
        return {
            'board': self.game.get_state(),
            'current_player': self.game.state.current_player.value,
            'phase': self.current_phase.name,
            'dice': self.game.state.dice,
            'valid_moves': [
                {
                    'from': move.from_point,
                    'to': move.to_point,
                    'dice': move.dice_value
                }
                for move in self.get_valid_moves()
            ],
            'bar': self.game.state.bar,
            'off': self.game.state.off,
            'game_over': self._check_game_over(),
            'winner': self.get_winner().value if self.get_winner() else None
        }

    def can_bear_off(self, player: Player) -> bool:
        """Check if a player can bear off pieces"""
        return self.game.move_validator.can_bear_off()

    def get_move_history(self) -> List[Move]:
        """Get the history of moves made"""
        return self.move_history.copy()

    def save_game(self) -> str:
        """Serialize current game state to string"""
        return self.game.state.to_json()

    def load_game(self, state_json: str) -> bool:
        """Load game state from serialized string"""
        try:
            self.game.state = GameState.from_json(state_json)
            self._save_state()
            self._emit_event(GameEvent.STATE_CHANGED)
            return True
        except Exception as e:
            raise GameEngineError(f"Failed to load game state: {e}") 