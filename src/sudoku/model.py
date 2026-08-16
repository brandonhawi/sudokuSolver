from torch import Tensor, nn

INPUT_DIM = 891


class SudokuMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.hidden_layer = nn.Linear(891, 256)
        self.activation = nn.ReLU()
        self.output_layer = nn.Linear(256, 9)

    def forward(self, x: Tensor):
        x = self.hidden_layer(x)
        x = self.activation(x)
        return self.output_layer(x)
