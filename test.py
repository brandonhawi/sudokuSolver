from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, send, emit
import time
import copy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

delay = 0

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

# board = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0],
#          [0, 0, 0, 0, 0, 0, 0, 0, 0]]

# board = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
#              [0, 0, 0, 0, 0, 3, 0, 8, 5],
#              [0, 0, 1, 0, 2, 0, 0, 0, 0],
#              [0, 0, 0, 5, 0, 7, 0, 0, 0],
#              [0, 0, 4, 0, 0, 0, 1, 0, 0],
#              [0, 9, 0, 0, 0, 0, 0, 0, 0],
#              [5, 0, 0, 0, 0, 0, 0, 7, 3],
#              [0, 0, 2, 0, 1, 0, 0, 0, 0],
#              [0, 0, 0, 0, 4, 0, 0, 0, 9]]


def isValid(row, col, val):
    return isValidRow(row, val) and isValidCol(col, val) and isValidBox(row, col, val)


def isValidRow(row, val):
    for col in range(len(board[row])):
        if val == board[row][col]:
            return False
    return True


def isValidCol(col, val):
    for row in range(9):
        if val == board[row][col]:
            return False
    return True


def isValidBox(row, col, val):
    rowBox = row // 3
    colBox = col // 3

    rowIndexes = rowBox*3
    colIndexes = colBox*3

    for i in range(rowIndexes, rowIndexes+3):
        for j in range(colIndexes, colIndexes + 3):
            if board[i][j] == val:
                return False
    return True

# TODO: Make it interactive (full sudoku game basically)
# TODO: Different algorithms (click buttons to solve with other algorithms)
# TODO: Randomly generate a puzzle (unique solution)


def solve(row, col):
    for posValue in range(1, 10):
        if(isOpen(row, col)):
            socketio.emit('boardChange', (row, col, posValue))
            time.sleep(delay)
            if isValid(row, col, posValue):
                board[row][col] = posValue

                if row+1 == 9 and col+1 == 9:
                    return True
                elif col+1 == 9:
                    if solve(row+1, 0):
                        return True
                    else:
                        board[row][col] = 0
                        socketio.emit('boardChange', (row, col, 0))
                        time.sleep(delay)
                else:
                    if solve(row, col+1):
                        return True
                    else:
                        board[row][col] = 0
                        socketio.emit('boardChange', (row, col, 0))
                        time.sleep(delay)
        else:
            if row + 1 == 9 and col + 1 == 9:
                return True
            elif col + 1 == 9:
                return solve(row+1, 0)
            else:
                return solve(row, col+1)
    socketio.emit('boardChange', (row, col, 0))
    time.sleep(delay)
    return False


def isOpen(row, col):
    return board[row][col] == 0


def solveBoard(inputBoard):
    solve(0, 0)


@app.route('/')
def hello_world():
    return render_template('index.html', board=board)


@app.route('/solve')
def solver():
    solveBoard(board)
    return redirect(url_for('hello_world'))

@app.route('/reset')
def reset():
    reset_board()
    return redirect(url_for('hello_world'))

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
    emit('myResponse')

def reset_board():
    global board
    board = copy.deepcopy(initialBoard)

if __name__ == '__main__':
    reset_board()
    socketio.run(app, debug=True)
