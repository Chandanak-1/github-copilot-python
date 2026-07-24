import sudoku_logic


def count_clues(board):
    return sum(1 for row in board for value in row if value != sudoku_logic.EMPTY)


def is_valid_sudoku(board):
    size = sudoku_logic.SIZE
    for row in board:
        if sorted(row) != list(range(1, size + 1)):
            return False
    for col in range(size):
        column = [board[row][col] for row in range(size)]
        if sorted(column) != list(range(1, size + 1)):
            return False
    for box_row in range(0, size, 3):
        for box_col in range(0, size, 3):
            box = []
            for r in range(3):
                for c in range(3):
                    box.append(board[box_row + r][box_col + c])
            if sorted(box) != list(range(1, size + 1)):
                return False
    return True


def test_create_empty_board_shape_and_values():
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(value == sudoku_logic.EMPTY for row in board for value in row)


def test_is_safe_detects_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 3
    board[1][0] = 6

    assert not sudoku_logic.is_safe(board, 0, 2, 5)
    assert not sudoku_logic.is_safe(board, 2, 0, 6)
    assert not sudoku_logic.is_safe(board, 1, 1, 5)
    assert sudoku_logic.is_safe(board, 2, 2, 4)


def test_generate_puzzle_produces_valid_solution_and_clue_count():
    sudoku_logic.random.seed(0)
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert count_clues(puzzle) == 35
    assert all(0 <= value <= sudoku_logic.SIZE for row in puzzle for value in row)
    assert is_valid_sudoku(solution)
    assert any(puzzle[row][col] == sudoku_logic.EMPTY for row in range(sudoku_logic.SIZE) for col in range(sudoku_logic.SIZE))


def test_generate_puzzle_solution_matches_puzzle_non_empty_cells():
    sudoku_logic.random.seed(1)
    puzzle, solution = sudoku_logic.generate_puzzle(clues=40)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if puzzle[row][col] != sudoku_logic.EMPTY:
                assert puzzle[row][col] == solution[row][col]


def test_generated_puzzle_has_unique_solution():
    sudoku_logic.random.seed(2)
    puzzle, solution = sudoku_logic.generate_puzzle(clues=36)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1
    assert is_valid_sudoku(solution)
    assert count_clues(puzzle) == 36


def test_generated_puzzle_non_empty_cells_do_not_conflict():
    sudoku_logic.random.seed(3)
    puzzle, solution = sudoku_logic.generate_puzzle(clues=38)

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            value = puzzle[row][col]
            if value != sudoku_logic.EMPTY:
                # Temporarily remove the cell and verify the same value is safe there.
                puzzle[row][col] = sudoku_logic.EMPTY
                assert sudoku_logic.is_safe(puzzle, row, col, value)
                puzzle[row][col] = value


def test_generate_puzzle_with_easy_difficulty():
    sudoku_logic.random.seed(4)
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty='easy')

    clue_count = count_clues(puzzle)
    assert 40 <= clue_count <= 45
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1
    assert is_valid_sudoku(solution)


def test_generate_puzzle_with_medium_difficulty():
    sudoku_logic.random.seed(5)
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty='medium')

    clue_count = count_clues(puzzle)
    assert 32 <= clue_count <= 39
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1
    assert is_valid_sudoku(solution)


def test_generate_puzzle_with_hard_difficulty():
    sudoku_logic.random.seed(6)
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty='hard')

    clue_count = count_clues(puzzle)
    assert 28 <= clue_count <= 31
    assert sudoku_logic.count_solutions(puzzle, max_solutions=2) == 1
    assert is_valid_sudoku(solution)
