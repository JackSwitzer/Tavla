class BackgammonError(Exception):
    """Base exception for all game-related errors"""
    pass

class GameEngineError(BackgammonError):
    """Errors related to game engine operations"""
    pass

class InvalidMoveError(BackgammonError):
    """Raised when an invalid move is attempted"""
    pass

class InvalidStateError(BackgammonError):
    """Raised when game state is invalid"""
    pass

class RuleViolationError(BackgammonError):
    """Raised when a game rule is violated"""
    pass

class ValidationError(BackgammonError):
    """Raised when validation fails"""
    pass

class SerializationError(BackgammonError):
    """Raised when serialization/deserialization fails"""
    pass

class AIError(BackgammonError):
    """Raised for AI-related errors"""
    pass