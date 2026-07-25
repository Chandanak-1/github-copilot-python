import json

from app import app, CURRENT
import sudoku_logic


def test_index_route_returns_html():
    client = app.test_client()
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'<html' in response.data


def test_new_game_route_returns_puzzle_and_sets_current_solution():
    sudoku_logic.random.seed(2)
    client = app.test_client()
    response = client.get('/new?clues=30')

    assert response.status_code == 200
    payload = response.get_json()
    assert 'puzzle' in payload
    puzzle = payload['puzzle']
    assert len(puzzle) == sudoku_logic.SIZE
    assert sum(1 for row in puzzle for value in row if value != sudoku_logic.EMPTY) == 30
    assert CURRENT['solution'] is not None


def test_new_game_route_accepts_difficulty_easy():
    sudoku_logic.random.seed(7)
    client = app.test_client()
    response = client.get('/new?difficulty=easy')

    assert response.status_code == 200
    payload = response.get_json()
    puzzle = payload['puzzle']
    clue_count = sum(1 for row in puzzle for value in row if value != sudoku_logic.EMPTY)
    assert 40 <= clue_count <= 45
    assert CURRENT['solution'] is not None
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1


def test_new_game_route_accepts_difficulty_medium():
    sudoku_logic.random.seed(8)
    client = app.test_client()
    response = client.get('/new?difficulty=medium')

    assert response.status_code == 200
    payload = response.get_json()
    puzzle = payload['puzzle']
    clue_count = sum(1 for row in puzzle for value in row if value != sudoku_logic.EMPTY)
    assert 32 <= clue_count <= 39
    assert CURRENT['solution'] is not None
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1


def test_new_game_route_accepts_difficulty_hard():
    sudoku_logic.random.seed(9)
    client = app.test_client()
    response = client.get('/new?difficulty=hard')

    assert response.status_code == 200
    payload = response.get_json()
    puzzle = payload['puzzle']
    clue_count = sum(1 for row in puzzle for value in row if value != sudoku_logic.EMPTY)
    assert 28 <= clue_count <= 31
    assert CURRENT['solution'] is not None
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1
    assert payload.get('hints') == 0


def test_hint_route_returns_one_empty_cell_hint():
    sudoku_logic.random.seed(11)
    client = app.test_client()
    response = client.get('/new?clues=30')
    assert response.status_code == 200
    puzzle = CURRENT['puzzle']

    board = [row.copy() for row in puzzle]
    response = client.post('/hint', json={'board': board})
    assert response.status_code == 200

    payload = response.get_json()
    assert 'hint' in payload
    assert payload['hints'] == 1
    row = payload['hint']['row']
    col = payload['hint']['col']
    value = payload['hint']['value']

    assert puzzle[row][col] == sudoku_logic.EMPTY
    solution = CURRENT['solution']
    assert solution is not None
    assert solution[row][col] == value


def test_hint_route_does_not_overwrite_user_values():
    sudoku_logic.random.seed(12)
    client = app.test_client()
    response = client.get('/new?clues=30')
    assert response.status_code == 200
    puzzle = CURRENT['puzzle']

    board = [row.copy() for row in puzzle]
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == sudoku_logic.EMPTY:
                board[i][j] = 9 if 9 != CURRENT['solution'][i][j] else 8
                filled_row, filled_col = i, j
                break
        else:
            continue
        break

    response = client.post('/hint', json={'board': board})
    assert response.status_code == 200

    payload = response.get_json()
    hint_row = payload['hint']['row']
    hint_col = payload['hint']['col']
    assert (hint_row, hint_col) != (filled_row, filled_col)
    assert puzzle[hint_row][hint_col] == sudoku_logic.EMPTY


def test_hint_route_increments_hint_count_across_requests():
    sudoku_logic.random.seed(13)
    client = app.test_client()
    response = client.get('/new?clues=30')
    assert response.status_code == 200

    board = [row.copy() for row in CURRENT['puzzle']]
    response = client.post('/hint', json={'board': board})
    assert response.status_code == 200
    assert response.get_json()['hints'] == 1

    first_hint = response.get_json()['hint']
    board[first_hint['row']][first_hint['col']] = first_hint['value']

    response = client.post('/hint', json={'board': board})
    assert response.status_code == 200
    assert response.get_json()['hints'] == 2


def test_check_solution_route_rejects_without_active_game():
    client = app.test_client()
    CURRENT['solution'] = None
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload['error'] == 'No game in progress'


def test_check_solution_route_accepts_correct_solution():
    client = app.test_client()
    response = client.get('/new?clues=35')
    assert response.status_code == 200

    solution = CURRENT['solution']
    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['incorrect'] == []
    assert payload['complete'] is True


def test_check_solution_route_reports_incorrect_cells():
    client = app.test_client()
    response = client.get('/new?clues=35')
    assert response.status_code == 200

    puzzle = CURRENT['puzzle']
    board = [row.copy() for row in CURRENT['solution']]
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] == sudoku_logic.EMPTY:
                board[i][j] = board[i][j] % sudoku_logic.SIZE + 1
                wrong_cell = [i, j]
                break
        else:
            continue
        break

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    payload = response.get_json()
    assert wrong_cell in payload['incorrect']
    assert payload['complete'] is False


def test_check_solution_route_ignores_empty_cells():
    client = app.test_client()
    response = client.get('/new?clues=35')
    assert response.status_code == 200

    board = [row.copy() for row in CURRENT['solution']]
    board[1][1] = 0
    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['incorrect'] == []
    assert payload['complete'] is False


def test_check_solution_route_ignores_prefilled_cells_in_incorrect_list():
    client = app.test_client()
    response = client.get('/new?clues=35')
    assert response.status_code == 200

    puzzle = CURRENT['puzzle']
    solution = CURRENT['solution']
    board = [row.copy() for row in solution]
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] != sudoku_logic.EMPTY:
                board[i][j] = (board[i][j] % sudoku_logic.SIZE) + 1

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['incorrect'] == []
    assert payload['complete'] is False


def test_check_solution_route_incomplete_board_is_not_solved():
    client = app.test_client()
    response = client.get('/new?clues=35')
    assert response.status_code == 200

    solution = CURRENT['solution']
    board = [row.copy() for row in solution]
    board[0][0] = sudoku_logic.EMPTY

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['incorrect'] == []
    assert payload['complete'] is False
