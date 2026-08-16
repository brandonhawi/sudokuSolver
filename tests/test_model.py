import torch

from sudoku.model import INPUT_DIM, SudokuMLP


def test_output_shape():
    model = SudokuMLP()
    x = torch.randn(4, INPUT_DIM)
    assert model(x).shape == (4, 9)


def test_single_example():
    model = SudokuMLP()
    x = torch.randn(1, INPUT_DIM)
    assert model(x).shape == (1, 9)


def test_gradients_flow():
    model = SudokuMLP()
    x = torch.randn(4, INPUT_DIM)
    model(x).sum().backward()
    assert all(p.grad is not None for p in model.parameters())
