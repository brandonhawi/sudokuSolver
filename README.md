# Sudoku Solver

## What 

This is a web application with a React front end and Flask back end that solves Sudoku puzzles. It also initially used SocketIO to update the client as the Sudoku puzzle but once React was implemented, SocketIO was no longer needed. 

## Dev Environment Setup

This repository uses [uv](https://docs.astral.sh/uv/) to manage packages and the virtual environment.

After cloning the repository, a simple `uv sync` will create a virtual environment for the application if it does not already exist and install all necessary packages.

To run the app: `uv run flask run`

Make sure that you use `uv add <package>` to install any new packages added to the solution (or `uv add --dev <package>` for dev tools). 