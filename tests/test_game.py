import unittest
from game.game import Game, Player, Move, Point
from game.game_state import GameState

class TestBackgammonGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()

    def tearDown(self):
        self.game.cleanup()

    def test_initial_position(self):
        """Test initial game setup"""
        state = self.game.state
        
        # Test initial piece counts with more descriptive assertions
        self.assertEqual(state.board[0].count, 2, "Point 1 should have 2 white pieces")
        self.assertEqual(state.board[11].count, 5, "Point 12 should have 5 white pieces")
        self.assertEqual(state.board[16].count, 3, "Point 17 should have 3 white pieces")
        self.assertEqual(state.board[18].count, 5, "Point 19 should have 5 white pieces")
        
        self.assertEqual(state.board[23].count, -2, "Point 24 should have 2 black pieces")
        self.assertEqual(state.board[12].count, -5, "Point 13 should have 5 black pieces")
        self.assertEqual(state.board[7].count, -3, "Point 8 should have 3 black pieces")
        self.assertEqual(state.board[5].count, -5, "Point 6 should have 5 black pieces")
        
        # Verify total piece count
        white_count = sum(p.count for p in state.board if p.count > 0)
        black_count = sum(-p.count for p in state.board if p.count < 0)
        self.assertEqual(white_count, 15, "White should have 15 total pieces")
        self.assertEqual(black_count, 15, "Black should have 15 total pieces")
        
        # Test initial game state
        self.assertEqual(state.current_player, Player.WHITE)
        self.assertIsNone(state.dice)
        self.assertEqual(state.bar[Player.WHITE], 0)
        self.assertEqual(state.bar[Player.BLACK], 0)
        self.assertEqual(state.off[Player.WHITE], 0)
        self.assertEqual(state.off[Player.BLACK], 0)
        self.assertFalse(state.game_over)

    def test_dice_roll(self):
        """Test dice rolling functionality"""
        # Test multiple rolls to ensure randomness and valid values
        for _ in range(10):
            dice = self.game.roll_dice()
            self.assertEqual(len(dice), 2, "Dice roll should return exactly 2 values")
            self.assertTrue(all(1 <= d <= 6 for d in dice), "Dice values must be between 1 and 6")
            self.assertEqual(dice, self.game.state.dice, "Dice roll should update game state")

    def test_valid_moves_from_start(self):
        """Test valid moves from starting position"""
        self.game.state.dice = (6, 5)
        moves = self.game.get_valid_moves()
        
        # Test specific valid moves without relying on print statements
        expected_moves = {
            Move(18, 13, 5),  # Point 19 to 14 using 5
            Move(18, 12, 6),  # Point 19 to 13 using 6
            Move(16, 11, 5),  # Point 17 to 12 using 5
            Move(16, 10, 6),  # Point 17 to 11 using 6
            Move(11, 6, 5),   # Point 12 to 7 using 5
            Move(11, 5, 6),   # Point 12 to 6 using 6
            Move(0, 5, 5),    # Point 1 to 6 using 5
            Move(0, 6, 6),    # Point 1 to 7 using 6
        }
        
        # Convert lists to sets for comparison
        actual_moves = set(moves)
        self.assertEqual(
            expected_moves, 
            actual_moves, 
            f"Expected moves: {expected_moves}\nActual moves: {actual_moves}"
        )

    def test_bar_moves(self):
        """Test moves when pieces are on the bar"""
        # Put a white piece on the bar
        self.game.state.bar[Player.WHITE] = 1
        self.game.state.dice = (4, 2)
        
        moves = self.game.get_valid_moves()
        
        # Verify only bar moves are allowed
        self.assertTrue(all(move.from_point == 24 for move in moves), 
                       "All moves must be from the bar")
        
        # Verify correct entry points
        entry_points = {move.to_point for move in moves}
        expected_entries = {3, 1}  # Points 4 and 2
        self.assertEqual(entry_points, expected_entries, 
                        "Invalid entry points from bar")
        
        # Test blocked entry points
        self.game.state.board[3].count = -2  # Block point 4
        moves = self.game.get_valid_moves()
        entry_points = {move.to_point for move in moves}
        self.assertEqual(entry_points, {1}, 
                        "Should only allow unblocked entry points")

    def test_bearing_off(self):
        """Test bearing off rules"""
        # Set up a position where white can bear off
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.board[0].count = 2  # Point 1
        self.game.state.board[4].count = 2  # Point 5
        self.game.state.dice = (6, 5)
        
        # Verify initial bearing off state
        self.assertTrue(self.game.move_validator.can_bear_off(), 
                       "Should be able to bear off")
        
        # Test exact roll bearing off
        move = Move(4, -1, 5)  # Point 5 off with 5
        self.assertTrue(self.game.make_move(move), 
                       "Should allow exact bearing off move")
        self.assertEqual(self.game.state.off[Player.WHITE], 1, 
                        "One piece should be borne off")
        
        # Test bearing off with larger roll
        move = Move(0, -1, 6)  # Point 1 off with 6
        self.assertTrue(self.game.make_move(move), 
                       "Should allow bearing off with larger roll")
        self.assertEqual(self.game.state.off[Player.WHITE], 2, 
                        "Two pieces should be borne off")

    def test_invalid_bearing_off(self):
        """Test invalid bearing off attempts"""
        # Set up a position where white cannot bear off (piece too far)
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.board[0].count = 1
        self.game.state.board[8].count = 1  # Piece outside home board
        self.game.state.dice = (6, 5)
        
        self.assertFalse(self.game.can_bear_off(Player.WHITE))
        move = Move(0, -1, 6)
        self.assertFalse(self.game.make_move(move))

    def test_hitting_blot(self):
        """Test hitting opponent's blot"""
        # Set up a position with a black blot
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.board[0].count = 1    # White piece
        self.game.state.board[5].count = -1   # Black blot
        self.game.state.dice = (5, 2)
        
        # Make the hitting move
        move = Move(0, 5, 5)
        self.assertTrue(self.game.make_move(move))
        
        # Verify the hit
        self.assertEqual(self.game.state.board[5].count, 1)  # White piece
        self.assertEqual(self.game.state.bar[Player.BLACK], 1)  # Black on bar

    def test_doubles_handling(self):
        """Test handling of double dice values"""
        # Set up a position for testing doubles
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.board[0].count = 4  # Four white pieces on point 1
        self.game.state.dice = (4, 4)
        
        # Test initial moves available
        moves = self.game.get_valid_moves()
        self.assertEqual(len([m for m in moves if m.dice_value == 4]), 4,
                        "Should have exactly 4 moves available with doubles")
        
        # Execute all four moves
        for i in range(4):
            move = Move(0, 4, 4)
            self.assertTrue(self.game.make_move(move), 
                           f"Move {i+1} should be valid")
            if i < 3:
                self.assertIsNotNone(self.game.state.dice, 
                                   f"Dice should remain after move {i+1}")
        
        # Verify final position
        self.assertEqual(self.game.state.board[0].count, 0,
                        "Source point should be empty")
        self.assertEqual(self.game.state.board[4].count, 4,
                        "Target point should have all pieces")
        self.assertIsNone(self.game.state.dice,
                        "Dice should be consumed after all moves")

    def test_game_over(self):
        """Test game over detection"""
        # Set up a winning position for white
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.off[Player.WHITE] = 14
        self.game.state.board[0].count = 1  # One piece left
        self.game.state.dice = (6, 1)
        
        # Make the winning move
        move = Move(0, -1, 1)
        self.assertTrue(self.game.make_move(move))
        
        # Verify game is over
        self.assertTrue(self.game.state.game_over)
        self.assertEqual(self.game.state.off[Player.WHITE], 15)

    def test_invalid_moves(self):
        """Test various invalid move scenarios"""
        # Try to move when no dice rolled
        move = Move(0, 1, 1)
        self.assertFalse(self.game.make_move(move))
        
        # Try to move opponent's piece
        self.game.state.dice = (1, 2)
        move = Move(23, 22, 1)  # Try to move black piece as white
        self.assertFalse(self.game.make_move(move))
        
        # Try to move to occupied point
        self.game.state.board[1].count = -2  # Two black pieces
        move = Move(0, 1, 1)  # Try to move white piece onto black pieces
        self.assertFalse(self.game.make_move(move))

    def test_complex_doubles_scenario(self):
        """Test doubles with blocked moves"""
        # Set up a position where not all double moves are possible
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.board[0].count = 2    # Two white pieces
        self.game.state.board[4].count = -2   # Two black pieces blocking
        self.game.state.dice = (4, 4)
        
        moves = self.game.get_valid_moves()
        print("\nTesting complex doubles scenario")
        print("Board state:")
        for i, point in enumerate(self.game.state.board):
            if not point.is_empty:
                print(f"Point {i+1}: {point}")
            
        print("\nAvailable moves with blocked points:")
        for move in moves:
            print(f"From: {move.from_point+1}, To: {move.to_point+1}, Dice: {move.dice_value}")
        
        # Should have limited moves due to blocking
        self.assertTrue(len(moves) < 4, "Should have fewer than 4 moves available")

    def test_move_validation_with_cache(self):
        """Test that move validation caching works correctly"""
        self.game.state.dice = (6, 5)
        
        # First call should calculate moves
        moves1 = self.game.get_valid_moves()
        
        # Second call should use cache
        moves2 = self.game.get_valid_moves()
        
        self.assertEqual(moves1, moves2)
        self.assertTrue(len(moves1) > 0)
        
        # After making a move, cache should be invalidated
        first_move = moves1[0]
        self.game.make_move(first_move)
        
        moves3 = self.game.get_valid_moves()
        self.assertNotEqual(moves1, moves3)

    def test_game_serialization(self):
        """Test game state serialization for web interface"""
        self.game.state.dice = (6, 5)
        state_dict = self.game.get_state()
        
        self.assertIn('board', state_dict)
        self.assertIn('current_player', state_dict)
        self.assertIn('dice', state_dict)
        self.assertIn('valid_moves', state_dict)
        
        # Verify move format is suitable for web interface
        if state_dict['valid_moves']:
            move = state_dict['valid_moves'][0]
            self.assertIn('from', move)
            self.assertIn('to', move)
            self.assertIn('dice', move)

    def test_move_sequence(self):
        """Test a sequence of moves in a single turn"""
        self.game.state.dice = (6, 5)
        initial_moves = self.game.get_valid_moves()
        
        # Make first move
        first_move = Move(18, 13, 5)  # Point 19 to 14 using 5
        self.assertTrue(self.game.make_move(first_move))
        
        # Verify remaining moves are updated
        remaining_moves = self.game.get_valid_moves()
        self.assertNotEqual(initial_moves, remaining_moves)
        self.assertTrue(all(move.dice_value == 6 for move in remaining_moves))

    def test_forced_moves(self):
        """Test scenarios where moves are forced"""
        # Setup position where only one sequence is possible
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.board[23].count = 1  # Single white piece on point 24
        self.game.state.board[22].count = 1  # Single white piece on point 23
        self.game.state.dice = (1, 2)
        
        moves = self.game.get_valid_moves()
        expected_moves = {
            Move(23, 22, 1),  # Must move from point 24 to 23
            Move(22, 20, 2)   # Then from point 23 to 21
        }
        self.assertEqual(set(moves), expected_moves)

    def test_blocked_movement(self):
        """Test scenarios where movement is blocked"""
        # Setup position with blocked points
        self.game.state.board = [Point() for _ in range(24)]
        self.game.state.board[0].count = 1    # White piece on point 1
        self.game.state.board[1].count = -2   # Two black pieces on point 2
        self.game.state.board[2].count = -2   # Two black pieces on point 3
        self.game.state.dice = (1, 2)
        
        moves = self.game.get_valid_moves()
        self.assertEqual(len(moves), 0, "Should have no valid moves when blocked")

    def test_game_state_history(self):
        """Test game state history tracking"""
        initial_position = self.game.get_fen_position()
        
        # Make some moves
        self.game.state.dice = (6, 5)
        move = Move(18, 13, 5)
        self.game.make_move(move)
        
        # Verify history
        self.assertEqual(len(self.game.history), 2)
        self.assertEqual(self.game.history[0], initial_position)
        self.assertNotEqual(self.game.history[1], initial_position)

    def test_invalid_state_transitions(self):
        """Test invalid state transitions are prevented"""
        # Try to move without rolling dice
        move = Move(0, 1, 1)
        self.assertFalse(self.game.make_move(move))
        
        # Try to move after game is over
        self.game.state.game_over = True
        self.game.state.dice = (6, 5)
        self.assertFalse(self.game.make_move(move))

    def test_player_turn_management(self):
        """Test proper management of player turns"""
        self.assertEqual(self.game.state.current_player, Player.WHITE)
        
        # Complete a turn
        self.game.state.dice = (6, 5)
        move1 = Move(18, 13, 5)
        move2 = Move(18, 12, 6)
        
        self.game.make_move(move1)
        self.assertEqual(self.game.state.current_player, Player.WHITE)
        
        self.game.make_move(move2)
        self.assertEqual(self.game.state.current_player, Player.BLACK)

    def test_state_serialization_roundtrip(self):
        """Test complete serialization and deserialization of game state"""
        # Setup some specific state
        self.game.state.dice = (6, 5)
        self.game.state.bar[Player.WHITE] = 1
        original_state = self.game.get_state()
        
        # Serialize and deserialize
        state_json = self.game.state.to_json()
        new_state = GameState.from_json(state_json)
        
        # Verify all state is preserved
        self.assertEqual(new_state.current_player, self.game.state.current_player)
        self.assertEqual(new_state.dice, self.game.state.dice)
        self.assertEqual(new_state.bar, self.game.state.bar)
        self.assertEqual(new_state.off, self.game.state.off)
        self.assertEqual(new_state.game_over, self.game.state.game_over)
        
        # Verify board state
        for i in range(24):
            self.assertEqual(new_state.board[i].count, self.game.state.board[i].count)

if __name__ == '__main__':
    # Configure test runner
    import sys
    import unittest.runner
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBackgammonGame)
    
    # Configure verbosity from command line
    verbosity = 2 if "-v" in sys.argv else 1
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful()) 