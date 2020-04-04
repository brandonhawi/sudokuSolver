from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, send, emit
import time
import copy
import random
import solver
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

initialBoard = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 9, 5, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [8, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 8, 0, 3, 0, 0, 1],
                [7, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 1, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 9]]

board = list()
firstGen = list()
currentSolver = None

# TODO: Make it interactive (full sudoku game basically)
# TODO: Different algorithms (click buttons to solve with other algorithms)
# TODO: Randomly generate a puzzle (unique solution)

def printBoard(board):
    for row in board:
        print(row)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
    emit('myResponse')


@socketio.on('delayChange')
def handle_delay_change(sliderValue):
    sliderValue = int(sliderValue)
    newDelay = 1/(100**sliderValue)
    currentSolver.changeDelay(newDelay)

@socketio.on('solve')
def backtrackSolve():
    global board
    global currentSolver
    currentSolver = solver.backtrackSolver(board, socketio)
    currentSolver.solve(0, 0)

# @socketio.on('stochastic')
# def stochastic():
#     global board
#     global currentSolver
#     initBoard = solver.Board(board)
#     print("Initial Board: ")
#     printBoard(initBoard.boardArray)
#     currentSolver = solver.stochasticSolver(initBoard, socketio)
#     fullyEvolvedBoard = currentSolver.solve(10000)
#     print("Fully Evolved Board: ")
#     printBoard(fullyEvolvedBoard.boardArray)
#     print("Fully Evolved Board's Fitness: {}".format(fullyEvolvedBoard.fitness))


def reset_board():
    global board
    board = copy.deepcopy(initialBoard)


def adjust_delay(new_delay):
    global delay
    delay = new_delay

@app.route('/')
def index():
    reset_board()
    return render_template('index.html', board=board)

@app.route('/reset')
def reset():
    reset_board()
    return redirect(url_for('index'))

# @app.route('/stochastic')
# def stochasticRoute():
#     reset_board()
#     global firstGen
#     firstGen = createFirstGeneration()
#     return render_template('stochastic.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)