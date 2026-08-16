"""Train SudokuMLP on the Kaggle 1M dataset and log the run to mlflow.

Usage: python scripts/train.py  (run scripts/download_data.py first if data/ is missing)
"""

import pathlib

import mlflow
import torch
from mlflow.data.numpy_dataset import from_numpy

from sudoku.data import (
    DatasetSplit,
    SudokuDataset,
    train_mask_random_k,
    val_mask_deterministic_k,
)
from sudoku.evaluate import precompute_eval_tensors
from sudoku.model import SudokuMLP
from sudoku.train import train

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CSV_PATH = REPO_ROOT / "data" / "sudoku.csv"

TRACKING_URI = "http://gaming-pc:5000/"
EXPERIMENT = "sudoku-solver"
NUM_EPOCHS = 10
BATCH_SIZE = 256
VAL_SIZE = 10_000
SPLIT_SEED = 0


def main():
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    train_dataset = SudokuDataset(
        str(CSV_PATH),
        DatasetSplit.TRAINING,
        mask_fn=train_mask_random_k,
        seed=SPLIT_SEED,
        val_size=VAL_SIZE,
    )
    val_dataset = SudokuDataset(
        str(CSV_PATH),
        DatasetSplit.VALIDATION,
        mask_fn=val_mask_deterministic_k,
        seed=SPLIT_SEED,
        val_size=VAL_SIZE,
    )

    train_solutions = torch.from_numpy(train_dataset.solutions).to(device)
    val_x, val_y = precompute_eval_tensors(val_dataset, device=device)

    model = SudokuMLP().to(device)

    train_ds_for_mlflow = from_numpy(
        features=train_dataset.solutions,
        source="data/sudoku.csv",
        name="sudoku-1m-train-split",
    )

    val_loss, val_acc = train(
        model,
        train_solutions,
        val_x,
        val_y,
        num_epochs=NUM_EPOCHS,
        batch_size=BATCH_SIZE,
        run_params={
            "hidden_size": 256,
            "num_hidden_layers": 1,
            "val_size": VAL_SIZE,
            "split_seed": SPLIT_SEED,
            "mask_strategy_train": "uniform_random_k1-20",
            "mask_strategy_val": "seeded_randperm_k1-20",
            "encoding": "onehot_810_plus_query81",
        },
        train_dataset=train_ds_for_mlflow,
    )

    print(f"final val_loss={val_loss:.4f} val_acc={val_acc:.4f}")


if __name__ == "__main__":
    main()
