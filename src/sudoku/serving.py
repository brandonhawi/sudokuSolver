import pathlib
import tempfile
from typing import Any

import mlflow.pyfunc
import numpy as np
import pandas as pd
import torch
from mlflow.models import ModelSignature
from mlflow.types import ColSpec, DataType, Schema, TensorSpec
from mlflow.types.schema import Array
from torch import nn

from sudoku.encoding import encode_batch

REGISTERED_MODEL_NAME = "sudoku-solver"

# one row per query: a board (81 digits, 0 = blank) and the cell to predict
SIGNATURE = ModelSignature(
    inputs=Schema(
        [
            ColSpec(Array(DataType.long), "board"),
            ColSpec(DataType.long, "query_cell"),
        ]
    ),
    outputs=Schema([TensorSpec(np.dtype("float32"), (-1, 9))]),
)

INPUT_EXAMPLE = pd.DataFrame(
    {
        "board": [np.zeros(81, dtype=np.int64)],
        "query_cell": np.array([0], dtype=np.int64),
    }
)


class SudokuSolverModel(mlflow.pyfunc.PythonModel):
    """Pyfunc wrapper that keeps the board encoding server-side.

    Clients send sudoku-level inputs (board digits + query cell) and get back the
    9 digit probabilities; they never see the one-hot encoding.
    """

    def load_context(self, context):
        from sudoku.model import SudokuMLP

        self.model = SudokuMLP()
        state = torch.load(context.artifacts["state_dict"], map_location="cpu", weights_only=True)
        self.model.load_state_dict(state)
        self.model.eval()

    def predict(
        self, context, model_input: pd.DataFrame, params: dict[str, Any] | None = None
    ) -> Any:
        boards = torch.as_tensor(np.stack(list(model_input["board"])), dtype=torch.long)
        queries = torch.as_tensor(model_input["query_cell"].to_numpy(), dtype=torch.long)
        x = encode_batch(boards, queries)
        with torch.no_grad():
            return torch.softmax(self.model(x), dim=1).numpy()


def log_solver_model(model: nn.Module) -> None:
    """Log (and register) the model as a self-contained pyfunc artifact.

    The state dict plus the package source (via code_paths) travel inside the
    artifact, so serving needs only mlflow and torch installed.
    """
    state = {k: v.detach().cpu() for k, v in model.state_dict().items()}
    with tempfile.TemporaryDirectory() as tmp:
        state_path = pathlib.Path(tmp) / "state_dict.pt"
        torch.save(state, state_path)
        mlflow.pyfunc.log_model(
            name="model",
            python_model=SudokuSolverModel(),
            artifacts={"state_dict": str(state_path)},
            code_paths=[str(pathlib.Path(__file__).parent)],
            signature=SIGNATURE,
            input_example=INPUT_EXAMPLE,
            registered_model_name=REGISTERED_MODEL_NAME,
        )
