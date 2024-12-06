class BackgammonError(Exception):
    """Base exception for backgammon game errors"""
    pass

class InvalidMoveError(BackgammonError):
    """Raised when an invalid move is attempted"""
    pass

class IllegalStateError(BackgammonError):
    """Raised when game state is invalid"""
    pass

class GameOverError(BackgammonError):
    """Raised when attempting actions on a finished game"""
    pass