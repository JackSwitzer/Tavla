from enum import Enum
from typing import Callable, Dict, List, Any, Tuple, Optional
from game.game_state import GameState
from game.move import Move
from game.game import Game
from game.ai.ai_player import AIPlayer  # We'll create this later
from game.game_state import GameStateSnapshot
from game.player import Player

class GameEvent(Enum):
    DICE_ROLLED = "dice_rolled"
    MOVE_MADE = "move_made"
    GAME_OVER = "game_over"
    STATE_CHANGED = "state_changed"

class EventManager:
    def __init__(self):
        self._subscribers: Dict[GameEvent, List[Callable]] = {
            event: [] for event in GameEvent
        }
    
    def subscribe(self, event: GameEvent, callback: Callable[[Any], None]) -> None:
        self._subscribers[event].append(callback)
    
    def emit(self, event: GameEvent, data: Any = None) -> None:
        for callback in self._subscribers[event]:
            callback(data)

class GameManager:
    def __init__(self, ai_opponent: bool = False):
        self.game = Game()
        self.event_manager = EventManager()
        self.state_manager = GameStateManager()
        self.ai_player: Optional[AIPlayer] = AIPlayer() if ai_opponent else None
        
        # Store initial state
        self.state_manager.push_state(self.game.state)
        
    def handle_turn(self) -> None:
        """Handle turn logic, including AI moves if necessary"""
        if self.game.state.game_over:
            return
            
        current_player = self.game.state.current_player
        if self.ai_player and current_player == Player.BLACK:
            self._handle_ai_turn()
        
    def _handle_ai_turn(self) -> None:
        """Execute AI player's turn"""
        if not self.game.state.dice:
            self.roll_dice()
            
        # Give AI multiple attempts to find valid moves
        attempts = 0
        max_attempts = 3
        
        while self.game.state.dice and attempts < max_attempts:
            move = self.ai_player.get_best_move(self.game.state)
            if not move:
                break
            if not self.make_move(move):
                attempts += 1
                continue
            attempts = 0  # Reset attempts after successful move
    
    def make_move(self, move: Move) -> bool:
        """Execute a move and update game state"""
        if self.game.state.game_over:
            return False
            
        success = self.game.make_move(move)
        if success:
            self.state_manager.push_state(self.game.state)
            self.event_manager.emit(GameEvent.MOVE_MADE, self.game.get_state())
            if self.game.state.game_over:
                self.event_manager.emit(GameEvent.GAME_OVER, self.game.get_state())
        return success
    
    def roll_dice(self) -> Tuple[int, int]:
        """Roll dice and notify subscribers"""
        if self.game.state.game_over or self.game.state.dice:
            raise ValueError("Cannot roll dice now")
            
        dice = self.game.roll_dice()
        self.state_manager.push_state(self.game.state)
        self.event_manager.emit(GameEvent.DICE_ROLLED, dice)
        return dice
    
    def undo_move(self) -> bool:
        """Undo the last move"""
        if not self.state_manager.can_undo():
            return False
        
        snapshot = self.state_manager.undo()
        self.game.load_from_snapshot(snapshot)
        self.event_manager.emit(GameEvent.STATE_CHANGED, self.game.get_state())
        return True
    
    def redo_move(self) -> bool:
        """Redo a previously undone move"""
        if not self.state_manager.can_redo():
            return False
        
        snapshot = self.state_manager.redo()
        self.game.load_from_snapshot(snapshot)
        self.event_manager.emit(GameEvent.STATE_CHANGED, self.game.get_state())
        return True
    
    def get_state(self) -> dict:
        """Get current game state"""
        return self.game.get_state()
    
    def get_state_for_client(self) -> dict:
        """Get game state formatted for web client"""
        return self.game.state.to_json()
    
    def handle_client_move(self, move_data: dict) -> bool:
        """Handle move request from web client"""
        try:
            move = Move(
                from_point=move_data['from'],
                to_point=move_data['to'],
                dice_value=move_data['dice']
            )
            success = self.make_move(move)
            if success:
                self.handle_turn()  # Handle AI response if necessary
            return success
        except (KeyError, ValueError):
            return False
    
    def subscribe_to_updates(self, callback: Callable[[dict], None]) -> None:
        """Subscribe to game state updates"""
        def state_changed(data):
            callback(self.get_state_for_client())
        
        self.event_manager.subscribe(GameEvent.STATE_CHANGED, state_changed)
        self.event_manager.subscribe(GameEvent.MOVE_MADE, state_changed)
        self.event_manager.subscribe(GameEvent.DICE_ROLLED, state_changed)
        self.event_manager.subscribe(GameEvent.GAME_OVER, state_changed)

class GameStateManager:
    def __init__(self):
        self.history: List[GameStateSnapshot] = []
        self.current_index: int = -1
        
    def push_state(self, state: GameState) -> None:
        """Create and store a snapshot of the current state"""
        snapshot = GameStateSnapshot(
            board_state=tuple(point.count for point in state.board),
            current_player=state.current_player,
            dice=state.dice,
            bar=state.bar.copy(),
            off=state.off.copy(),
            game_over=state.game_over,
            move_count=state.move_count,
            remaining_doubles=state.remaining_doubles
        )
        
        # Remove any future states if we're in a branched history
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
            
        self.history.append(snapshot)
        self.current_index = len(self.history) - 1
    
    def can_undo(self) -> bool:
        """Check if undo is possible"""
        return self.current_index > 0
    
    def can_redo(self) -> bool:
        """Check if redo is possible"""
        return self.current_index < len(self.history) - 1
    
    def undo(self) -> Optional[GameStateSnapshot]:
        """Move back one state in history"""
        if not self.can_undo():
            return None
            
        self.current_index -= 1
        return self.history[self.current_index]
    
    def redo(self) -> Optional[GameStateSnapshot]:
        """Move forward one state in history"""
        if not self.can_redo():
            return None
            
        self.current_index += 1
        return self.history[self.current_index]
    
    def get_current_snapshot(self) -> Optional[GameStateSnapshot]:
        """Get the current state snapshot"""
        if self.current_index < 0:
            return None
        return self.history[self.current_index]
    
    def clear_history(self) -> None:
        """Clear all history"""
        self.history.clear()
        self.current_index = -1
    
    def get_move_history(self) -> List[Tuple[int, int, int]]:
        """Get list of moves made (from_point, to_point, dice_value)"""
        moves = []
        for i in range(1, len(self.history)):
            prev = self.history[i-1]
            curr = self.history[i]
            # Find what changed between states
            for j in range(24):
                if prev.board_state[j] != curr.board_state[j]:
                    # This point changed - find the corresponding move
                    if prev.board_state[j] > curr.board_state[j]:
                        from_point = j
                    else:
                        to_point = j
            # Infer dice value from the move
            dice_value = abs(to_point - from_point)
            moves.append((from_point, to_point, dice_value))
        return moves