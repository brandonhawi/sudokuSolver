import torch
import torch.nn.functional as F

from sudoku.model import INPUT_DIM


def encode_batch(digits: torch.Tensor, query_cells: torch.Tensor) -> torch.Tensor:
    assert digits.ndim == 2 and digits.shape[1] == 81, (
        f"expected (B, 81), and got {tuple(digits.shape)}"
    )
    assert query_cells.shape == (digits.shape[0],), (
        f"expected ({digits.shape[0]},), got {tuple(query_cells.shape)}"
    )
    board = F.one_hot(digits.long(), num_classes=10).float().flatten(1)
    query = F.one_hot(query_cells.long(), num_classes=81).float()
    out = torch.cat([board, query], dim=1)
    assert out.shape == (digits.shape[0], INPUT_DIM)
    return out
