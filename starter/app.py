from flask import Flask, render_template, jsonify, request, abort
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle, solution, and hint count
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints': 0,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    clues_arg = request.args.get('clues')

    try:
        clues = int(clues_arg) if clues_arg is not None else None
    except ValueError:
        return jsonify({'error': 'Invalid clues value'}), 400

    try:
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues, difficulty=difficulty)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints'] = 0
    return jsonify({'puzzle': puzzle, 'hints': 0})

@app.route('/hint', methods=['POST'])
def hint_cell():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400
    if board is None:
        return jsonify({'error': 'Board is required'}), 400

    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == sudoku_logic.EMPTY and puzzle[i][j] == sudoku_logic.EMPTY:
                value = solution[i][j]
                CURRENT['hints'] += 1
                return jsonify({
                    'hint': {'row': i, 'col': j, 'value': value},
                    'hints': CURRENT['hints'],
                })

    return jsonify({'error': 'No empty cells available for hint'}), 400

@app.route('/validate-entry', methods=['POST'])
def validate_entry():
    data = request.json or {}
    board = data.get('board')
    row = data.get('row')
    col = data.get('col')
    value = data.get('value')

    if board is None or row is None or col is None or value is None:
        return jsonify({'error': 'Board, row, col, and value are required'}), 400

    try:
        row_index = int(row)
        col_index = int(col)
        value_int = int(value)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid row, col, or value'}), 400

    conflicts = sudoku_logic.find_conflicting_cells(board, row_index, col_index, value_int)
    return jsonify({'conflicts': conflicts})


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    incorrect = []
    complete = True
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if value == sudoku_logic.EMPTY:
                complete = False
                continue
            if value != solution[i][j]:
                if puzzle[i][j] == sudoku_logic.EMPTY:
                    incorrect.append([i, j])
                complete = False
    return jsonify({'incorrect': incorrect, 'complete': complete})

if __name__ == '__main__':
    app.run(debug=True)