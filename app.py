"""Flask server holding the one live Sudoku game.

The browser UI and the MCP server are both clients of this API, so a move made
by a language model shows up in the browser and vice versa.
"""

import threading

from flask import Flask, jsonify, render_template, request

from sudoku.game import Game, MoveError, normalize_difficulty

app = Flask(__name__)

_lock = threading.Lock()
_game = None


def current_game():
    global _game
    if _game is None:
        _game = Game("easy")
    return _game


@app.errorhandler(MoveError)
def handle_move_error(error):
    return jsonify({"error": str(error)}), 400


@app.route("/")
def index():
    return render_template("index.html")


@app.get("/api/game")
def get_game():
    with _lock:
        return jsonify(current_game().serialize())


@app.post("/api/game")
def new_game():
    global _game
    payload = request.get_json(silent=True) or {}
    difficulty = normalize_difficulty(payload.get("difficulty"))
    with _lock:
        _game = Game(difficulty)
        return jsonify(_game.serialize())


@app.post("/api/move")
def move():
    payload = request.get_json(silent=True) or {}
    row, col = _coordinates(payload)
    value = payload.get("value")
    if not isinstance(value, int):
        raise MoveError("value must be an integer between 1 and 9")
    with _lock:
        game = current_game()
        game.place(row, col, value)
        return jsonify(game.serialize())


@app.post("/api/clear")
def clear():
    row, col = _coordinates(request.get_json(silent=True) or {})
    with _lock:
        game = current_game()
        game.clear(row, col)
        return jsonify(game.serialize())


@app.post("/api/undo")
def undo():
    with _lock:
        game = current_game()
        game.undo()
        return jsonify(game.serialize())


def _coordinates(payload):
    """Pull 0-indexed row/col out of a request payload."""
    row = payload.get("row")
    col = payload.get("col")
    if not isinstance(row, int) or not isinstance(col, int):
        raise MoveError("row and column must be integers")
    return row, col


if __name__ == "__main__":
    app.run(debug=True, port=5001)
