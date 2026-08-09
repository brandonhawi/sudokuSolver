"""Generation and solving of standard 9x9 Sudoku puzzles.

Grids are represented as a list of 9 lists of 9 ints, where 0 means empty.
Every puzzle produced by `generate_puzzle` has exactly one solution.
"""

import random

SIZE = 9
BOX = 3
EMPTY = 0

DIFFICULTIES = {
    "easy": 45,
    "medium": 36,
    "hard": 30,
}


def empty_grid():
    return [[EMPTY] * SIZE for _ in range(SIZE)]


def copy_grid(grid):
    return [row[:] for row in grid]


def is_valid(grid, row, col, value):
    """Whether `value` can be placed at (row, col) without conflicting."""
    for i in range(SIZE):
        if grid[row][i] == value and i != col:
            return False
        if grid[i][col] == value and i != row:
            return False

    box_row = (row // BOX) * BOX
    box_col = (col // BOX) * BOX
    for i in range(box_row, box_row + BOX):
        for j in range(box_col, box_col + BOX):
            if grid[i][j] == value and (i, j) != (row, col):
                return False
    return True


def find_empty(grid):
    for row in range(SIZE):
        for col in range(SIZE):
            if grid[row][col] == EMPTY:
                return row, col
    return None


def solve(grid):
    """Return a solved copy of `grid`, or None if it has no solution."""
    working = copy_grid(grid)
    if _fill(working):
        return working
    return None


def _fill(grid, shuffle=False):
    cell = find_empty(grid)
    if cell is None:
        return True

    row, col = cell
    values = list(range(1, 10))
    if shuffle:
        random.shuffle(values)

    for value in values:
        if is_valid(grid, row, col, value):
            grid[row][col] = value
            if _fill(grid, shuffle):
                return True
            grid[row][col] = EMPTY
    return False


def count_solutions(grid, limit=2):
    """Count solutions, stopping early once `limit` have been found."""
    return _count(copy_grid(grid), limit)


def _count(grid, limit):
    cell = find_empty(grid)
    if cell is None:
        return 1

    row, col = cell
    total = 0
    for value in range(1, 10):
        if is_valid(grid, row, col, value):
            grid[row][col] = value
            total += _count(grid, limit - total)
            grid[row][col] = EMPTY
            if total >= limit:
                break
    return total


def generate_solution():
    """Generate a random, fully solved grid."""
    grid = empty_grid()
    _fill(grid, shuffle=True)
    return grid


def generate_puzzle(difficulty="easy"):
    """Generate a `(puzzle, solution)` pair with a unique solution.

    `difficulty` is one of the keys of DIFFICULTIES; it sets how many clues the
    puzzle keeps. Cells are removed one at a time and a removal is only kept if
    the puzzle still has exactly one solution, so the target clue count is a
    goal rather than a guarantee.
    """
    if difficulty not in DIFFICULTIES:
        raise ValueError(
            f"unknown difficulty {difficulty!r}; expected one of {sorted(DIFFICULTIES)}"
        )

    solution = generate_solution()
    puzzle = copy_grid(solution)
    target_clues = DIFFICULTIES[difficulty]

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    clues = SIZE * SIZE
    for row, col in cells:
        if clues <= target_clues:
            break
        removed = puzzle[row][col]
        puzzle[row][col] = EMPTY
        if count_solutions(puzzle) == 1:
            clues -= 1
        else:
            puzzle[row][col] = removed

    return puzzle, solution
