import copy
import random

SIZE = 9
EMPTY = 0

DIFFICULTY_LEVELS = {
    'easy': (40, 45),
    'medium': (32, 39),
    'hard': (28, 31),
}
DEFAULT_CLUES = 35
DEFAULT_DIFFICULTY = 'medium'


def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def find_empty_cell(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None, None


def find_conflicting_cells(board, row, col, value):
    if value == EMPTY:
        return []

    conflicts = []
    seen = set()

    def add_conflict(r, c):
        if (r, c) != (row, col) and (r, c) not in seen:
            seen.add((r, c))
            conflicts.append((r, c))

    for c in range(SIZE):
        if c != col and board[row][c] == value:
            add_conflict(row, c)

    for r in range(SIZE):
        if r != row and board[r][col] == value:
            add_conflict(r, col)

    start_row = row - row % 3
    start_col = col - col % 3
    for r in range(start_row, start_row + 3):
        for c in range(start_col, start_col + 3):
            if (r, c) != (row, col) and board[r][c] == value:
                add_conflict(r, c)

    return conflicts


def get_candidates(board, row, col):
    return [num for num in range(1, SIZE + 1) if is_safe(board, row, col, num)]

def count_solutions(board, max_solutions=2):
    row, col = None, None
    best_candidates = None

    # Choose an empty cell with the fewest legal candidates (MRV heuristic).
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == EMPTY:
                candidates = get_candidates(board, r, c)
                if not candidates:
                    return 0
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_candidates = candidates
                    row, col = r, c
                    if len(best_candidates) == 1:
                        break
        if best_candidates is not None and len(best_candidates) == 1:
            break

    if row is None:
        return 1

    solutions = 0
    for num in best_candidates:
        board[row][col] = num
        solutions += count_solutions(board, max_solutions)
        board[row][col] = EMPTY
        if solutions >= max_solutions:
            return solutions
    return solutions

def fill_board(board):
    row, col = find_empty_cell(board)
    if row is None:
        return True

    possible = list(range(1, SIZE + 1))
    random.shuffle(possible)
    for candidate in possible:
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            if fill_board(board):
                return True
            board[row][col] = EMPTY
    return False

def remove_cells(board, clues):
    target_removals = SIZE * SIZE - clues
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)
    removals = 0

    while removals < target_removals:
        progress = False
        for row, col in positions:
            if removals >= target_removals:
                break
            if board[row][col] == EMPTY:
                continue

            removed_value = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(board, max_solutions=2) == 1:
                removals += 1
                progress = True
            else:
                board[row][col] = removed_value

        if not progress:
            break
    return removals == target_removals

def normalize_difficulty(difficulty):
    if difficulty is None:
        return None
    if not isinstance(difficulty, str):
        raise ValueError('Difficulty must be a string')

    key = difficulty.strip().lower()
    if key not in DIFFICULTY_LEVELS:
        raise ValueError(f'Unknown difficulty level: {difficulty}')
    return key


def get_clue_count_for_difficulty(difficulty):
    difficulty_key = normalize_difficulty(difficulty)
    min_clues, max_clues = DIFFICULTY_LEVELS[difficulty_key]
    return random.randint(min_clues, max_clues)


def validate_clue_count(clues):
    if not isinstance(clues, int) or clues < 0 or clues > SIZE * SIZE:
        raise ValueError('Clues must be an integer between 0 and 81')
    return clues


def generate_puzzle(clues=None, difficulty=None):
    if clues is not None:
        clues = validate_clue_count(clues)
    elif difficulty is not None:
        clues = get_clue_count_for_difficulty(difficulty)
    else:
        clues = DEFAULT_CLUES

    while True:
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        if remove_cells(board, clues):
            return deep_copy(board), solution
