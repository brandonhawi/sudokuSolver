import pathlib
import shutil

import kagglehub

CSV_PATH = "../data/sudoku.csv"

if pathlib.Path("data").exists() and pathlib.Path(CSV_PATH).exists():
    print("Data already exists")
else:
    print("Downloading data")
    path = kagglehub.dataset_download("bryanpark/sudoku")
    dest = pathlib.Path("data")
    dest.mkdir(exist_ok=True)
    shutil.copy(pathlib.Path(path) / "sudoku.csv", dest / "sudoku.csv")
    print(f"Copied to {dest / 'sudoku.csv'}")
