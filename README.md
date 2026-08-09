# Sudoku

A playable Sudoku game whose controls are exposed to a language model over MCP,
so you can watch a model play in the browser and work on teaching it to win.

The Flask server owns the single live game. The browser page and the MCP server
are both clients of the same HTTP API, so a move a model makes through MCP
appears in the browser within a few hundred milliseconds, and a move you make in
the browser is what the model sees on its next look at the board.

```
browser  ──┐
           ├──►  Flask (app.py)  ──►  game state (sudoku/)
MCP client ┘         ▲
                     │
              mcp_server.py
```

## Setup

This repository uses [uv](https://docs.astral.sh/uv/). After cloning:

```bash
uv sync
```

Use `uv add <package>` for new packages (`uv add --dev <package>` for dev tools).

## Running the game

```bash
uv run flask run
```

Then open <http://127.0.0.1:5001>. Click a cell and type 1-9 to place a number,
backspace to clear it. The port is 5001 rather than the Flask default of 5000
because macOS AirPlay Receiver occupies 5000 and answers 403 to everything.

## Connecting a model over MCP

Start the game server first — the MCP server is a client of it and will say so
if it cannot connect. Then register the MCP server:

```bash
claude mcp add sudoku -- uv --directory /Users/brandonhawi/Projects/sudokuSolver run python mcp_server.py
```

Or, for a client that takes JSON config:

```json
{
  "mcpServers": {
    "sudoku": {
      "command": "uv",
      "args": [
        "--directory", "/Users/brandonhawi/Projects/sudokuSolver",
        "run", "python", "mcp_server.py"
      ]
    }
  }
}
```

Set `SUDOKU_GAME_URL` if the game is not on `http://127.0.0.1:5001`.

### Tools the model gets

| Tool | What it does |
| --- | --- |
| `show_board` | Draws the current board. Empty cells are dots. |
| `new_game(difficulty)` | Starts a fresh `easy`, `medium`, or `hard` puzzle. |
| `place_number(row, col, value)` | Writes a digit into a cell. |
| `clear_cell(row, col)` | Erases a digit the model placed earlier. |
| `undo()` | Reverts the last move. |

Rows and columns are 1-indexed, so `R1C1` is the top-left cell — matching the
labels on the rendered board. Every tool returns a redrawn board plus a summary
line, because small models track a drawn grid far better than they track JSON.

The tool set is deliberately bare: there is nothing that narrows a cell down for
the model, so working out which digits are possible is the model's job and the
board is an honest measure of its play.

Illegal moves are refused rather than recorded. Placing a digit that already
appears in the row, column, or box comes back as a rejection explaining why, and
the board is left untouched — the model gets corrective feedback instead of a
quietly broken board, and the running `rejected` count is a cheap signal of how
well it is reasoning. A wrong-but-legal digit is still accepted, though, so a
model can reason its way into a dead end and has to `undo` or `clear_cell` to
get out.

## Layout

| Path | Contents |
| --- | --- |
| `sudoku/generator.py` | Puzzle generation and solving. |
| `sudoku/game.py` | Game state, move rules, board rendering. |
| `app.py` | Flask server: the game's HTTP API and the page. |
| `static/`, `templates/` | The browser UI — plain JS and CSS, no build step. |
| `mcp_server.py` | MCP server exposing the controls to a model. |

Every generated puzzle is checked to have exactly one solution: cells are
removed from a solved grid one at a time, and a removal is kept only if the
puzzle still solves uniquely. That matters here because an ambiguous puzzle
would make "did the model beat it?" unanswerable. Difficulty is the number of
clues left — 45 easy, 36 medium, 30 hard.
