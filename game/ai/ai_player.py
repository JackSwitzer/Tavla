from typing import Optional
from game.game_state import GameState
from game.move import Move, MoveValidator

class AIPlayer:
    def get_best_move(self, state: GameState) -> Optional[Move]:
        """
        Get the best move for the current position
        This is a placeholder - we'll implement actual AI logic later
        """
        # For now, just return the first valid move
        validator = MoveValidator(state)
        valid_moves = validator.get_valid_moves()
        return valid_moves[0] if valid_moves else None 