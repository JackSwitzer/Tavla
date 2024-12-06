from flask import Flask, jsonify, request, render_template
from ai import BackgammonAI
from game.game import Game, Player
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class GameManager:
    def __init__(self):
        self.games = {}
    
    def create_game(self):
        game_id = str(uuid.uuid4())
        game = Game()
        self.games[game_id] = game
        return game_id, game

    def get_game(self, game_id):
        return self.games.get(game_id)

game_manager = GameManager()
ai_player = BackgammonAI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game/new', methods=['POST'])
def new_game():
    game_id, game = game_manager.create_game()
    return jsonify({'game_id': game_id, 'state': game.get_state()})

@app.route('/api/game/<game_id>/roll', methods=['POST'])
def roll_dice(game_id):
    try:
        game = game_manager.get_game(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        
        # Clear existing dice before rolling new ones
        game.state.dice = None
        
        dice = game.roll_dice()
        state = game.get_state()
        return jsonify({'state': state, 'dice': dice})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/<game_id>/valid-moves', methods=['GET'])
def get_valid_moves(game_id):
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    dice_values = game.state.dice
    if not dice_values:
        return jsonify({'error': 'Must roll dice first'}), 400
    
    # TODO: Implement get_valid_moves logic in Game class
    valid_moves = game.get_valid_moves()
    return jsonify({'valid_moves': valid_moves})

@app.route('/api/game/<game_id>/move', methods=['POST'])
def make_move(game_id):
    try:
        game = game_manager.get_game(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        data = request.json
        if not all(k in data for k in ['from', 'to', 'color']):
            return jsonify({'error': 'Missing required move parameters'}), 400

        from_point = data['from']
        to_point = data['to']
        color = data['color']

        if game.state.current_player.value != color:
            return jsonify({'error': 'Not your turn'}), 400

        if not game.state.dice:
            return jsonify({'error': 'Must roll dice first'}), 400

        if game.is_valid_move(from_point, to_point, color):
            game.move_checker(from_point, to_point, color)
            return jsonify({'state': game.get_state()})
        else:
            return jsonify({'error': 'Invalid move'}), 400
    except Exception as e:
        return jsonify({'error': f'Move failed: {str(e)}'}), 500

@app.route('/api/game/<game_id>/ai-move', methods=['POST'])
def ai_move(game_id):
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404

    move = ai_player.choose_best_move(game)
    if move:
        from_point, to_point = move
        game.move_checker(from_point, to_point, 'black')
        return jsonify({'state': game.get_state()})
    else:
        return jsonify({'error': 'No valid moves'}), 400

@app.route('/api/game/<game_id>/state', methods=['GET'])
def get_game_state(game_id):
    game = game_manager.get_game(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    try:
        state = game.get_state()
        return jsonify({'state': state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/<game_id>/refresh', methods=['POST'])
def refresh_game(game_id):
    try:
        # Clean up old game
        if game_id in game_manager.games:
            game_manager.games[game_id].cleanup()
            del game_manager.games[game_id]
        
        # Create new game with fresh state
        new_game_id, game = game_manager.create_game()
        return jsonify({
            'game_id': new_game_id,
            'state': game.get_state()
        })
    except Exception as e:
        return jsonify({'error': f'Failed to refresh game: {str(e)}'}), 500

@app.errorhandler(Exception)
def handle_error(error):
    response = {
        'error': str(error),
        'status': 500
    }
    return jsonify(response), 500

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port=5000)
