"""Runs a local model against the Sudoku game over MCP.

Point it at an Ollama host and it plays one game, printing each move as it
goes so you can follow along next to the browser.

    uv run --group agent python -m solver_agent.player --difficulty easy
"""

import argparse
import asyncio
import os
import mlflow
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_ollama import ChatOllama

from solver_agent.client import BoardState, sudoku_client

mlflow.langchain.autolog()

mlflow.set_tracking_uri("http://gaming-pc:5000")
mlflow.set_experiment("sudoku-solver")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://gaming-pc:11434")
MODEL = os.environ.get("SUDOKU_MODEL", "qwen3:8b")

NUM_CTX = 4096
TEMPERATURE = 0.0
MAX_STEPS = 300

SYSTEM_PROMPT = """You are playing a game of Sudoku by calling tools.

The board is 9x9. Rows are numbered 1-9 from the top and columns 1-9 from the \
left, so R1C1 is the top-left cell. A dot is an empty cell. Every row, every \
column, and every 3x3 box must end up holding each digit 1-9 exactly once.

Work one cell at a time:
1. Pick an empty cell.
2. Rule out every digit that already appears in its row, its column, or its \
3x3 box.
3. If exactly one digit survives, place it with place_number.
4. If more than one survives, leave the cell alone and pick a different one.

Only place a digit you are sure of. There is always at least one cell \
somewhere on the board that has just one possibility, so there is never a \
need to guess. A rejected move means the digit was already in that row, \
column, or box, so re-read the board before trying again.

Keep going until the board is full. Do not stop to ask questions or to \
explain your plan - just play."""

FIRST_MESSAGE = """Here is the board:

{board}

Play until it is solved."""


@dataclass
class GameResult:
    """How one game went."""

    solved: bool
    filled_cells: int
    empty_cells: int
    moves: int
    rejected: int
    steps: int
    stop_reason: str
    board: str

    def summary(self) -> str:
        outcome = "SOLVED" if self.solved else f"unsolved ({self.stop_reason})"
        return (
            f"{outcome}: filled {self.filled_cells}/81, "
            f"{self.moves} moves, {self.rejected} rejected, {self.steps} steps"
        )


def build_model(
    model: str = MODEL,
    host: str = OLLAMA_HOST,
    num_ctx: int = NUM_CTX,
    reasoning: bool | None = None,
) -> ChatOllama:
    """Connect to an Ollama model.

    `reasoning` controls Qwen3's thinking mode: True is far more accurate and
    far slower, False is quick, None leaves the model's default alone.
    """
    return ChatOllama(
        model=model,
        base_url=host,
        num_ctx=num_ctx,
        temperature=TEMPERATURE,
        reasoning=reasoning,
    )


async def play(
    difficulty: str = "easy",
    model: ChatOllama | None = None,
    max_steps: int = MAX_STEPS,
    verbose: bool = True,
) -> GameResult:
    """Play one game from a fresh board and report how far the model got."""
    async with sudoku_client() as client:
        start = await client.new_game(difficulty)
        if verbose:
            print(f"new {difficulty} game - {start.empty_cells} cells to fill\n")
            print(start.board, "\n")

        agent = create_agent(
            model or build_model(),
            client.tools,
            system_prompt=SYSTEM_PROMPT,
        )

        steps = 0
        stop_reason = "finished"
        try:
            async for chunk in agent.astream(
                {"messages": [("user", FIRST_MESSAGE.format(board=start.board))]},
                {"recursion_limit": max_steps},
                stream_mode="updates",
            ):
                steps += _report(chunk, verbose)
        except Exception as error:  # noqa: BLE001 - a stalled game is a result
            stop_reason = type(error).__name__
            if verbose:
                print(f"\nstopped: {stop_reason}: {error}")

        final = await client.board()
        if final.solved:
            stop_reason = "solved"

        result = _score(final, steps, stop_reason)
        if verbose:
            print(f"\n{final.board}\n\n{result.summary()}")
        return result


def _score(final: BoardState, steps: int, stop_reason: str) -> GameResult:
    return GameResult(
        solved=final.solved,
        filled_cells=final.filled_cells,
        empty_cells=final.empty_cells,
        moves=final.moves,
        rejected=final.rejected,
        steps=steps,
        stop_reason=stop_reason,
        board=final.board,
    )


def _report(chunk: dict, verbose: bool) -> int:
    """Print the model's tool calls as they happen. Returns calls seen."""
    calls = 0
    for update in chunk.values():
        for message in update.get("messages", []) if isinstance(update, dict) else []:
            for call in getattr(message, "tool_calls", []) or []:
                calls += 1
                if verbose:
                    arguments = ", ".join(
                        f"{key}={value}" for key, value in call["args"].items()
                    )
                    print(f"  {call['name']}({arguments})")
            if verbose and getattr(message, "type", None) == "tool":
                first_line = str(message.content).splitlines()[0]
                if first_line.startswith("Move rejected"):
                    print(f"    -> {first_line}")
    return calls


def main() -> None:
    parser = argparse.ArgumentParser(description="Play Sudoku with a local model.")
    parser.add_argument(
        "--difficulty", default="easy", choices=("easy", "medium", "hard")
    )
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--host", default=OLLAMA_HOST)
    parser.add_argument("--num-ctx", type=int, default=NUM_CTX)
    parser.add_argument("--max-steps", type=int, default=MAX_STEPS)
    parser.add_argument(
        "--think",
        dest="reasoning",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="force Qwen3 thinking mode on or off",
    )
    arguments = parser.parse_args()

    model = build_model(
        model=arguments.model,
        host=arguments.host,
        num_ctx=arguments.num_ctx,
        reasoning=arguments.reasoning,
    )
    asyncio.run(
        play(
            difficulty=arguments.difficulty,
            model=model,
            max_steps=arguments.max_steps,
        )
    )


if __name__ == "__main__":
    main()
