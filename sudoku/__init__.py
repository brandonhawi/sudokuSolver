"""Core Sudoku game logic: puzzle generation and playable game state."""

from sudoku.game import Game, MoveError, normalize_difficulty, render_grid
from sudoku.generator import DIFFICULTIES, generate_puzzle, solve

__all__ = [
    "Game",
    "MoveError",
    "normalize_difficulty",
    "render_grid",
    "DIFFICULTIES",
    "generate_puzzle",
    "solve",
]
