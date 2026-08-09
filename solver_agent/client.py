"""Connection to the Sudoku MCP server, as LangChain tools.

The agent only ever sees these tools. Nothing here imports the `sudoku`
package, so the model has no path to the board except the moves it plays.
"""

import os
import re
from contextlib import asynccontextmanager
from dataclasses import dataclass

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession

SERVER_NAME = "sudoku"
SERVER_SCRIPT = "mcp_server.py"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOLVED = re.compile(r"Solved! (\d+) moves, (\d+) rejected")
IN_PROGRESS = re.compile(
    r"(\d+) empty cells remain \((\w+) puzzle, (\d+) moves, (\d+) rejected\)"
)


@dataclass(frozen=True)
class BoardState:
    """What the summary line under a rendered board says."""

    solved: bool
    empty_cells: int
    moves: int
    rejected: int
    board: str

    @property
    def filled_cells(self) -> int:
        return 81 - self.empty_cells


def parse_board(rendered: str) -> BoardState:
    """Read a board plus summary line back into numbers worth scoring."""
    solved = SOLVED.search(rendered)
    if solved:
        return BoardState(
            solved=True,
            empty_cells=0,
            moves=int(solved.group(1)),
            rejected=int(solved.group(2)),
            board=rendered,
        )

    progress = IN_PROGRESS.search(rendered)
    if not progress:
        raise ValueError(f"could not read a board out of:\n{rendered}")

    return BoardState(
        solved=False,
        empty_cells=int(progress.group(1)),
        moves=int(progress.group(3)),
        rejected=int(progress.group(4)),
        board=rendered,
    )


class SudokuClient:
    """Tools for the model, plus a side channel for the harness.

    Setup and scoring go through `call`, which does not pass through the
    model. Only `tools` is handed to the agent.
    """

    def __init__(self, session: ClientSession, tools: list):
        self._session = session
        self.tools = tools

    @property
    def tool_names(self) -> list[str]:
        return [tool.name for tool in self.tools]

    async def call(self, name: str, **arguments) -> str:
        result = await self._session.call_tool(name, arguments)
        parts = [block.text for block in result.content if block.type == "text"]
        return "\n".join(parts) if parts else "(the server returned nothing)"

    async def new_game(self, difficulty: str = "easy") -> BoardState:
        return parse_board(await self.call("new_game", difficulty=difficulty))

    async def board(self) -> BoardState:
        return parse_board(await self.call("show_board"))


@asynccontextmanager
async def sudoku_client(server_script: str = SERVER_SCRIPT, cwd: str = PROJECT_ROOT):
    """Start the MCP server as a subprocess and yield a connected client.

    One session is held open for the whole game. Letting the adapter open a
    session per tool call would spawn a fresh server subprocess for every
    move the model makes.

    The game server must already be running. If it is not, tool calls come
    back as readable errors rather than exceptions, which is what the model
    should see anyway.
    """
    client = MultiServerMCPClient(
        {
            SERVER_NAME: {
                "transport": "stdio",
                "command": "python",
                "args": [server_script],
                "cwd": cwd,
                "env": os.environ.copy(),
            }
        }
    )
    async with client.session(SERVER_NAME) as session:
        yield SudokuClient(session, await load_mcp_tools(session))
