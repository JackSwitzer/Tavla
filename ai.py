import random
from copy import deepcopy

class BackgammonAI:
    def __init__(self, depth=3, simulations=50):
        self.depth = depth
        self.simulations = simulations

    def evaluate_position(self, board, bar, home):
        """
        Basic position evaluation:
        1. Material count
        2. Position advancement
        3. Home board strength
        4. Blots (exposed pieces)
        """
        score = 0
        
        # Material and position score
        for i, count in enumerate(board):
            if count < 0:  # AI pieces (black)
                # More valuable if advanced (closer to home)
                score -= count * (i + 1) / 2
                # Penalty for blots
                if count == -1:
                    score += 2
            elif count > 0:  # Opponent pieces (white)
                score += count * ((24 - i) + 1) / 2
                if count == 1:
                    score -= 2

        # Bar piece penalty
        score += bar["white"] * 5
        score -= bar["black"] * 5

        # Home piece bonus
        score += home["white"] * 3
        score -= home["black"] * 3

        return score

    def simulate_move(self, game, move_sequence):
        """Simulate a sequence of moves and return resulting position score"""
        # Create a deep copy of the game state
        sim_game = deepcopy(game)
        
        for move in move_sequence:
            from_point, to_point = move
            sim_game.move_checker(from_point, to_point, "black")
            
        return self.evaluate_position(sim_game.board, sim_game.bar, sim_game.home)

    def get_possible_moves(self, game):
        """Get all possible moves for current dice values"""
        moves = []
        dice_values = game.moves_remaining.copy()
        
        # For each starting point
        for from_point in range(24):
            # For each dice value
            for dice in dice_values:
                to_point = from_point - dice  # Moving towards 0 for black
                if game.is_valid_move(from_point, to_point, "black"):
                    moves.append((from_point, to_point))
        
        return moves

    def get_move_sequences(self, game, depth=None):
        """Generate possible move sequences up to specified depth"""
        if depth is None:
            depth = self.depth

        base_moves = self.get_possible_moves(game)
        if depth == 1 or not base_moves:
            return [[move] for move in base_moves]

        sequences = []
        for move in base_moves:
            # Simulate making this move
            sim_game = deepcopy(game)
            sim_game.move_checker(move[0], move[1], "black")
            
            # Recursively get subsequent moves
            subsequent_sequences = self.get_move_sequences(sim_game, depth - 1)
            
            # Add this move to the front of each subsequent sequence
            for seq in subsequent_sequences:
                sequences.append([move] + seq)

        return sequences

    def choose_best_move(self, game):
        """Use Monte Carlo simulation to choose the best move sequence"""
        move_sequences = self.get_move_sequences(game)
        if not move_sequences:
            return None

        best_score = float('inf')  # We want to minimize score (black is negative)
        best_sequence = None

        for sequence in move_sequences:
            total_score = 0
            
            # Run multiple simulations for this sequence
            for _ in range(self.simulations):
                score = self.simulate_move(game, sequence)
                total_score += score
            
            avg_score = total_score / self.simulations
            
            if avg_score < best_score:
                best_score = avg_score
                best_sequence = sequence

        return best_sequence[0] if best_sequence else None 