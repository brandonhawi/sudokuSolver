import numpy as np
import pytest
import torch

from sudoku.data import (
    DatasetSplit,
    SudokuDataset,
    sample_batch,
    single_blank_mask,
    train_mask_random_k,
    val_mask_deterministic_k,
)
from sudoku.model import INPUT_DIM

N_ROWS = 50
VAL_SIZE = 10


@pytest.fixture(scope="module")
def csv_path(tmp_path_factory):
    """A small CSV in the Kaggle layout: header, then '<81 puzzle digits>,<81 solution digits>' rows."""
    rng = np.random.default_rng(0)
    lines = ["quizzes,solutions"]
    for _ in range(N_ROWS):
        solution = rng.integers(1, 10, 81)
        puzzle = solution.copy()
        puzzle[rng.choice(81, 20, replace=False)] = 0
        lines.append("".join(map(str, puzzle)) + "," + "".join(map(str, solution)))
    path = tmp_path_factory.mktemp("data") / "sudoku.csv"
    path.write_text("\n".join(lines) + "\n", newline="\n")
    return str(path)


def test_split_sizes(csv_path):
    full = SudokuDataset(csv_path, DatasetSplit.ALL, mask_fn=single_blank_mask, val_size=VAL_SIZE)
    train = SudokuDataset(
        csv_path, DatasetSplit.TRAINING, mask_fn=single_blank_mask, val_size=VAL_SIZE
    )
    val = SudokuDataset(
        csv_path, DatasetSplit.VALIDATION, mask_fn=single_blank_mask, val_size=VAL_SIZE
    )
    assert len(full) == N_ROWS
    assert len(train) == N_ROWS - VAL_SIZE
    assert len(val) == VAL_SIZE


def test_split_deterministic_and_disjoint(csv_path):
    train_a = SudokuDataset(
        csv_path, DatasetSplit.TRAINING, mask_fn=single_blank_mask, seed=0, val_size=VAL_SIZE
    )
    train_b = SudokuDataset(
        csv_path, DatasetSplit.TRAINING, mask_fn=single_blank_mask, seed=0, val_size=VAL_SIZE
    )
    val = SudokuDataset(
        csv_path, DatasetSplit.VALIDATION, mask_fn=single_blank_mask, seed=0, val_size=VAL_SIZE
    )

    assert np.array_equal(train_a.solutions, train_b.solutions)

    train_rows = {row.tobytes() for row in train_a.solutions}
    val_rows = {row.tobytes() for row in val.solutions}
    assert not train_rows & val_rows


def test_getitem(csv_path):
    ds = SudokuDataset(csv_path, DatasetSplit.ALL, mask_fn=single_blank_mask, val_size=VAL_SIZE)
    idx = 5
    puzzle, target_cell, answer = ds[idx]

    assert puzzle.shape == (81,)
    assert target_cell.item() == idx % 81
    assert puzzle[target_cell] == 0
    assert answer.dtype == torch.long
    assert answer.item() == ds.solutions[idx][idx % 81] - 1


def test_train_mask_random_k_range():
    for idx in range(100):
        cells = train_mask_random_k(idx)
        assert 1 <= len(cells) <= 20
        assert len(cells.unique()) == len(cells)
        assert ((cells >= 0) & (cells < 81)).all()


def test_val_mask_deterministic():
    for idx in range(50):
        cells = val_mask_deterministic_k(idx)
        assert torch.equal(cells, val_mask_deterministic_k(idx))
        assert len(cells) == 1 + idx % 20


def test_sample_batch(csv_path):
    ds = SudokuDataset(csv_path, DatasetSplit.ALL, mask_fn=single_blank_mask, val_size=VAL_SIZE)
    # identical rows, so labels are checkable no matter which row each draw picked
    row = torch.from_numpy(ds.solutions[0]).long()
    solutions = row.expand(16, 81).contiguous()

    x, y = sample_batch(solutions, batch_size=32)
    assert x.shape == (32, INPUT_DIM)
    assert ((y >= 0) & (y <= 8)).all()

    board = x[:, :810].view(32, 81, 10)
    query = x[:, 810:]
    blanks_per_row = board[:, :, 0].sum(dim=1)
    assert blanks_per_row.min() >= 1 and blanks_per_row.max() <= 20

    target = query.argmax(dim=1)
    assert (board[torch.arange(32), target, 0] == 1).all()  # query cell is always blank
    assert torch.equal(y, row[target] - 1)
