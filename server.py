from flask import Flask, render_template, jsonify, request, session
from flask_cors import CORS
import secrets
from game import GameState

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app)

games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/new_game', methods=['POST'])
def new_game():
    data = request.json
    n = data.get('n', 5)
    if n < 4 or n > 10:
        n = 5
    
    game_id = secrets.token_hex(8)
    try:
        games[game_id] = GameState(n)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify({
        'game_id': game_id,
        'n': n,
        'grid': get_grid_state(game_id)
    })

@app.route('/api/grid/<game_id>', methods=['GET'])
def get_grid(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    return jsonify(get_grid_state(game_id))

@app.route('/api/mark_cow/<game_id>', methods=['POST'])
def mark_cow(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    if row is None or col is None:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    game = games[game_id]
    success = game.mark_cow(row, col)
    
    if not success:
        return jsonify({'error': 'Cannot mark this cell'}), 400
    
    return jsonify({
        'success': True,
        'grid': get_grid_state(game_id),
        'game_over': game.is_game_over(),
        'won': game.is_won(),
        'errors': game.get_errors(),
        'remaining_cows': game.get_remaining_cows()
    })

@app.route('/api/mark_not_cow/<game_id>', methods=['POST'])
def mark_not_cow(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.json
    row = data.get('row')
    col = data.get('col')
    
    if row is None or col is None:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    game = games[game_id]
    success = game.mark_not_cow(row, col)
    
    if not success:
        return jsonify({'error': 'Cannot mark this cell'}), 400
    
    return jsonify({
        'success': True,
        'grid': get_grid_state(game_id),
        'game_over': game.is_game_over(),
        'won': game.is_won()
    })

@app.route('/api/reveal/<game_id>', methods=['POST'])
def reveal(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    game.reveal_answer()
    
    return jsonify({
        'success': True,
        'grid': get_grid_state(game_id),
        'game_over': True,
        'won': False
    })

def get_grid_state(game_id: str):
    game = games[game_id]
    grid = []
    for r in range(game.n):
        row = []
        for c in range(game.n):
            row.append({
                'row': r,
                'col': c,
                'color': game.get_color(r, c),
                'mark': game.get_mark(r, c)
            })
        grid.append(row)
    return grid

if __name__ == '__main__':
    print("Starting Find The Cows game server...")
    print("Open your browser and go to http://localhost:5000")
    app.run(debug=True, host='localhost', port=5000)
