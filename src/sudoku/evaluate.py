import torch
from torch import nn
from torch.utils.data import DataLoader

from sudoku.data import SudokuDataset
from sudoku.encoding import encode_batch


def precompute_eval_tensors(
    dataset: SudokuDataset,
    device: str | torch.device = "cpu",
    batch_size: int = 4096,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Encode an eval dataset into (x, y) tensors once, so evaluation never touches the
    per-item Dataset path again. Only valid for deterministic mask policies."""
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)
    xs, ys = [], []
    for digits, query, y in loader:
        xs.append(encode_batch(digits, query))
        ys.append(y)
    return torch.cat(xs).to(device), torch.cat(ys).to(device)


@torch.no_grad()
def evaluate(
    model: nn.Module,
    val_x: torch.Tensor,
    val_y: torch.Tensor,
    loss_fn: nn.Module | None = None,
    chunk: int = 8192,
) -> tuple[float, float]:
    """Return (mean loss, accuracy) over a precomputed eval set."""
    if loss_fn is None:
        loss_fn = nn.CrossEntropyLoss()

    was_training = model.training
    model.eval()
    total_loss = 0.0
    total_correct = 0

    for i in range(0, len(val_x), chunk):
        x, y = val_x[i : i + chunk], val_y[i : i + chunk]
        logits = model(x)
        total_loss += loss_fn(logits, y).item() * len(x)
        total_correct += (logits.argmax(dim=1) == y).sum().item()

    model.train(was_training)
    return total_loss / len(val_x), total_correct / len(val_x)
