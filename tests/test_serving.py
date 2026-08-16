import numpy as np
import pandas as pd
import torch

from sudoku.model import SudokuMLP
from sudoku.serving import SudokuSolverModel


def test_predict_returns_probabilities():
    wrapper = SudokuSolverModel()
    wrapper.model = SudokuMLP().eval()  # bypass load_context

    board = np.random.default_rng(0).integers(1, 10, 81)
    board[[3, 40, 77]] = 0
    df = pd.DataFrame(
        {
            "board": [board, board, board],
            "query_cell": np.array([3, 40, 77], dtype=np.int64),
        }
    )

    probs = wrapper.predict(None, df)
    assert probs.shape == (3, 9)
    assert np.allclose(probs.sum(axis=1), 1.0, atol=1e-5)
    assert (probs >= 0).all()


def test_predict_matches_direct_forward():
    from sudoku.encoding import encode_batch

    wrapper = SudokuSolverModel()
    wrapper.model = SudokuMLP().eval()

    board = np.random.default_rng(1).integers(1, 10, 81)
    board[10] = 0
    df = pd.DataFrame({"board": [board], "query_cell": np.array([10], dtype=np.int64)})

    probs = wrapper.predict(None, df)

    x = encode_batch(torch.as_tensor(board[None, :]), torch.tensor([10]))
    with torch.no_grad():
        expected = torch.softmax(wrapper.model(x), dim=1).numpy()
    assert np.allclose(probs, expected)
