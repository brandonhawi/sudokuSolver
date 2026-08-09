"""MCP server exposing the Sudoku game's controls to a language model.

It is a thin client over the Flask game server, so every move a model makes is
visible live in the browser at http://127.0.0.1:5001.

Rows and columns are 1-indexed here (R1C1 is the top-left cell) because that is
how the rendered board labels them. Tool results are plain text: small models
follow a drawn board far better than they follow JSON.

Run with: uv run python mcp_server.py
"""

import logging
import os

import httpx
from mcp.server import MCPServer

from sudoku.game import render_grid

GAME_URL = os.environ.get("SUDOKU_GAME_URL", "http://127.0.0.1:5001")

logging.getLogger("httpx").setLevel(logging.WARNING)

mcp = MCPServer(
    "sudoku",
    instructions=(
        "Controls for a live Sudoku game. Call show_board to see the current "
        "puzzle, then place_number to fill in cells. Rows and columns are "
        "numbered 1-9, so R1C1 is the top-left cell."
    ),
)


def _request(method, path, **kwargs):
    """Call the game server, returning either its state or an error string."""
    try:
        response = httpx.request(method, f"{GAME_URL}{path}", timeout=30, **kwargs)
    except httpx.HTTPError:
        return None, (
            f"Could not reach the Sudoku game at {GAME_URL}. "
            "Start it with `uv run flask run` and try again."
        )

    try:
        body = response.json()
    except ValueError:
        return None, f"The game server returned an unreadable response ({response.status_code})."

    if response.status_code >= 400:
        return None, f"Move rejected: {body.get('error', 'unknown error')}"
    return body, None


def _describe(state, prefix=None):
    """Render a board plus a one-line summary of where the game stands."""
    if state["solved"]:
        summary = f"Solved! {state['moves']} moves, {state['rejected_moves']} rejected."
    else:
        summary = (
            f"{state['empty_cells']} empty cells remain "
            f"({state['difficulty']} puzzle, {state['moves']} moves, "
            f"{state['rejected_moves']} rejected)."
        )
    parts = [prefix] if prefix else []
    parts.extend([render_grid(state["grid"]), summary])
    return "\n\n".join(parts)


def _act(method, path, prefix=None, **kwargs):
    state, error = _request(method, path, **kwargs)
    if error:
        return error
    return _describe(state, prefix)


@mcp.tool()
def show_board() -> str:
    """Show the current Sudoku board. Empty cells are shown as a dot."""
    return _act("GET", "/api/game")


@mcp.tool()
def new_game(difficulty: str = "easy") -> str:
    """Start a new puzzle, discarding the current one.

    difficulty: "easy", "medium", or "hard".
    """
    return _act("POST", "/api/game", json={"difficulty": difficulty})


@mcp.tool()
def place_number(row: int, col: int, value: int) -> str:
    """Write a number into one cell of the board.

    row: 1-9, counting from the top. col: 1-9, counting from the left.
    value: the digit 1-9 to write.

    The move is rejected if the cell holds a starting clue, or if the digit
    already appears in that row, column, or 3x3 box.
    """
    return _act(
        "POST",
        "/api/move",
        prefix=f"Placed {value} at R{row}C{col}.",
        json={"row": row - 1, "col": col - 1, "value": value},
    )


@mcp.tool()
def clear_cell(row: int, col: int) -> str:
    """Erase a number you placed earlier. Starting clues cannot be erased."""
    return _act(
        "POST",
        "/api/clear",
        prefix=f"Cleared R{row}C{col}.",
        json={"row": row - 1, "col": col - 1},
    )


@mcp.tool()
def undo() -> str:
    """Undo the most recent move."""
    return _act("POST", "/api/undo", prefix="Undid the last move.")


if __name__ == "__main__":
    mcp.run()
