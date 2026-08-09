"""Playable Sudoku game state.

Coordinates here are 0-indexed. The layers that talk to a player (the HTTP API
and the MCP server) present 1-indexed rows and columns, which are easier to
read off a rendered board.
"""

from sudoku.generator import (
    DIFFICULTIES,
    EMPTY,
    SIZE,
    copy_grid,
    generate_puzzle,
    is_valid,
)


class MoveError(Exception):
    """Raised when a requested move is not allowed by the rules."""


class Game:
    def __init__(self, difficulty="easy"):
        self.difficulty = difficulty
        self.puzzle, self.solution = generate_puzzle(difficulty)
        self.grid = copy_grid(self.puzzle)
        self.moves = 0
        self.rejected_moves = 0
        self._history = []

    @property
    def solved(self):
        return self.grid == self.solution

    @property
    def empty_cells(self):
        return sum(row.count(EMPTY) for row in self.grid)

    def is_given(self, row, col):
        return self.puzzle[row][col] != EMPTY

    def place(self, row, col, value):
        """Write `value` into an empty or player-filled cell.

        Raises MoveError if the cell is a given, or if the value already
        appears in the same row, column, or 3x3 box.
        """
        self._check_bounds(row, col)
        if not 1 <= value <= 9:
            raise MoveError(f"value must be between 1 and 9, got {value}")
        if self.is_given(row, col):
            raise MoveError(
                f"R{row + 1}C{col + 1} is a given clue ({self.puzzle[row][col]}) "
                "and cannot be changed"
            )
        if not is_valid(self.grid, row, col, value):
            self.rejected_moves += 1
            raise MoveError(
                f"{value} cannot go in R{row + 1}C{col + 1}: it already appears "
                "in that row, column, or box"
            )

        self._history.append((row, col, self.grid[row][col]))
        self.grid[row][col] = value
        self.moves += 1

    def clear(self, row, col):
        """Empty a cell the player filled in earlier."""
        self._check_bounds(row, col)
        if self.is_given(row, col):
            raise MoveError(
                f"R{row + 1}C{col + 1} is a given clue and cannot be cleared"
            )
        if self.grid[row][col] == EMPTY:
            raise MoveError(f"R{row + 1}C{col + 1} is already empty")

        self._history.append((row, col, self.grid[row][col]))
        self.grid[row][col] = EMPTY
        self.moves += 1

    def undo(self):
        """Revert the most recent move. Returns the reverted (row, col)."""
        if not self._history:
            raise MoveError("there are no moves to undo")
        row, col, previous = self._history.pop()
        self.grid[row][col] = previous
        self.moves += 1
        return row, col

    def serialize(self):
        return {
            "difficulty": self.difficulty,
            "grid": copy_grid(self.grid),
            "givens": [[cell != EMPTY for cell in row] for row in self.puzzle],
            "solved": self.solved,
            "moves": self.moves,
            "rejected_moves": self.rejected_moves,
            "empty_cells": self.empty_cells,
        }

    def render(self):
        """An ASCII board, labelled so a player can name cells as RxCy."""
        return render_grid(self.grid)

    def status_line(self):
        if self.solved:
            return f"Solved in {self.moves} moves."
        return (
            f"{self.empty_cells} empty cells remaining "
            f"({self.moves} moves, {self.rejected_moves} rejected)."
        )

    @staticmethod
    def _check_bounds(row, col):
        if not (0 <= row < SIZE and 0 <= col < SIZE):
            raise MoveError(
                f"row and column must be between 1 and {SIZE}, "
                f"got R{row + 1}C{col + 1}"
            )


SEPARATOR = "   +-------+-------+-------+"
COLUMN_HEADER = "     1 2 3   4 5 6   7 8 9   (columns C1-C9)"


def render_grid(grid):
    """An ASCII board, labelled so a player can name cells as RxCy.

    Lives outside Game so the MCP server can render a grid it fetched over
    HTTP with exactly the same layout the game itself uses.
    """
    lines = [COLUMN_HEADER, SEPARATOR]
    for row in range(SIZE):
        cells = [
            str(value) if value != EMPTY else "." for value in grid[row]
        ]
        groups = [" ".join(cells[i:i + 3]) for i in range(0, SIZE, 3)]
        lines.append(f"R{row + 1} | {groups[0]} | {groups[1]} | {groups[2]} |")
        if row in (2, 5):
            lines.append(SEPARATOR)
    lines.append(SEPARATOR)
    return "\n".join(lines)


def normalize_difficulty(value):
    difficulty = (value or "easy").lower()
    if difficulty not in DIFFICULTIES:
        raise MoveError(
            f"unknown difficulty {value!r}; expected one of {sorted(DIFFICULTIES)}"
        )
    return difficulty
