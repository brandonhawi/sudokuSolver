from typing import Any

import mlflow
import mlflow.data
import torch
from torch import nn

from sudoku.data import sample_batch
from sudoku.evaluate import evaluate
from sudoku.model import INPUT_DIM


def train(
    model: nn.Module,
    train_solutions: torch.Tensor,
    val_x: torch.Tensor,
    val_y: torch.Tensor,
    *,
    num_epochs: int = 10,
    batch_size: int = 256,
    lr: float = 1e-3,
    max_k: int = 20,
    log_every: int = 100,
    eval_every: int = 1000,
    run_params: dict[str, Any] | None = None,
    train_dataset: mlflow.data.Dataset | None = None,
) -> tuple[float, float]:
    device = train_solutions.device
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    steps_per_epoch = len(train_solutions) // batch_size

    with mlflow.start_run():
        mlflow.log_params(
            {
                "lr": lr,
                "optimizer": "adam",
                "batch_size": batch_size,
                "num_epochs": num_epochs,
                "max_k": max_k,
                "sampling": "vectorized_with_replacement",
                "device": str(device),
                **(run_params or {}),
            }
        )
        if train_dataset is not None:
            mlflow.log_input(train_dataset, context="training")

        # verify initial perf
        val_loss, val_acc = evaluate(model, val_x, val_y, loss_fn)
        mlflow.log_metric("val_loss", val_loss, step=0)
        mlflow.log_metric("val_acc", val_acc, step=0)

        step = 0
        for epoch in range(num_epochs):
            model.train()
            for _ in range(steps_per_epoch):
                x, y = sample_batch(train_solutions, batch_size, max_k=max_k)
                logits = model(x)
                loss = loss_fn(logits, y)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                step += 1
                if step % log_every == 0:
                    mlflow.log_metric("train_loss", loss.item(), step=step, synchronous=False)
                if step % eval_every == 0:
                    val_loss, val_acc = evaluate(model, val_x, val_y, loss_fn)
                    mlflow.log_metric("val_loss", val_loss, step=step, synchronous=False)
                    mlflow.log_metric("val_acc", val_acc, step=step, synchronous=False)

        # final eval
        val_loss, val_acc = evaluate(model, val_x, val_y, loss_fn)
        mlflow.log_metric("val_loss", val_loss, step=step)
        mlflow.log_metric("val_acc", val_acc, step=step)

        # log from cpu so signature inference works with the numpy input_example
        mlflow.pytorch.log_model(
            model.to("cpu"),
            name="model",
            input_example=torch.randn(1, INPUT_DIM).numpy(),
        )
        model.to(device)

    return val_loss, val_acc
