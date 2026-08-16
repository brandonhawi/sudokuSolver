from collections.abc import Callable
from enum import Enum

import numpy as np
import torch
from torch.utils.data import Dataset

from sudoku.encoding import encode_batch


class DatasetSplit(Enum):
    ALL = 0
    TRAINING = 1
    VALIDATION = 2


class SudokuDataset(Dataset):
    def __init__(
        self,
        csv_file_path: str,
        split: DatasetSplit,
        mask_fn: Callable[[int], torch.Tensor],
        seed: int = 0,
        val_size: int = 10_000,
    ):
        with open(csv_file_path, "rb") as f:
            f.readline()
            buf = np.frombuffer(f.read(), dtype=np.uint8).reshape(-1, 164)
        all_solutions = (buf[:, 82:163] - ord("0")).astype(np.int8)

        g = torch.Generator().manual_seed(seed)
        perm = torch.randperm(len(all_solutions), generator=g)
        match split:
            case DatasetSplit.TRAINING:
                idxs = perm[val_size:]
            case DatasetSplit.VALIDATION:
                idxs = perm[:val_size]
            case DatasetSplit.ALL:
                idxs = perm
        self.solutions = all_solutions[idxs.numpy()]
        self.mask_fn = mask_fn

    def __len__(self):
        return len(self.solutions)

    def __getitem__(self, index: int):
        puzzle = self.solutions[index].copy()
        cells = self.mask_fn(index)

        target_cell = cells[0].item()
        original_answer = torch.tensor(puzzle[target_cell] - 1, dtype=torch.long)

        puzzle[cells.numpy()] = 0
        return torch.from_numpy(puzzle), torch.tensor(target_cell), original_answer


def train_mask_random_k(idx: int, max_k: int = 20) -> torch.Tensor:
    k = torch.randint(1, max_k + 1, (1,)).item()
    return torch.randperm(81)[:k]  # fresh randomness every access


def val_mask_deterministic_k(idx: int, max_k: int = 20) -> torch.Tensor:
    g = torch.Generator().manual_seed(idx)  # same cells for same idx, forever
    k = 1 + idx % max_k
    return torch.randperm(81, generator=g)[:k]


def single_blank_mask(idx: int) -> torch.Tensor:  # tonight's original val policy
    return torch.tensor([idx % 81])


def two_blank_mask(idx: int) -> torch.Tensor:  # the distractor experiment
    target = idx % 81
    distractor = (target + 1 + (idx * 37 + 11) % 80) % 81
    return torch.tensor([target, distractor])


def sample_batch(
    solutions: torch.Tensor, batch_size: int, max_k: int = 20
) -> tuple[torch.Tensor, torch.Tensor]:
    """Vectorized equivalent of train_mask_random_k + SudokuDataset.__getitem__ + encode_batch.

    `solutions` is a (N, 81) int tensor of solved boards; batches are drawn with replacement
    on whatever device it lives on.
    """
    device = solutions.device
    idx = torch.randint(len(solutions), (batch_size,), device=device)
    sol = solutions[idx].long()  # (B, 81)
    scores = torch.rand(batch_size, 81, device=device)
    ranks = scores.argsort(dim=1).argsort(dim=1)  # each row: permutation of 0..80
    k = torch.randint(1, max_k + 1, (batch_size, 1), device=device)
    blank = ranks < k  # exactly k blanks per row
    target = scores.argmin(dim=1)  # the rank-0 blank is the query cell
    y = sol.gather(1, target[:, None]).squeeze(1) - 1
    digits = sol.masked_fill(blank, 0)
    return encode_batch(digits, target), y
