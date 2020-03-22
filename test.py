from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, send, emit
import time
import copy
import random
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

delay = 0.1

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


def isValid(board, row, col, val):
    return isValidRow(board, row, val) and isValidCol(board, col, val) and isValidBox(board, row, col, val)


def isValidRow(board, row, val):
    for col in range(len(board[row])):
        if val == board[row][col]:
            return False
    return True


def isValidCol(board, col, val):
    for row in range(9):
        if val == board[row][col]:
            return False
    return True


def isValidBox(board, row, col, val):
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
    global board
    for posValue in range(1, 10):
        if(isOpen(row, col)):
            socketio.emit('boardChange', (row, col, posValue))
            time.sleep(delay)
            if isValid(board, row, col, posValue):
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


def isOpenOnBoard(localBoard, row, column):
    return isOpen(row, column) and localBoard[row][column]


def isOpen(row, col):
    return board[row][col] == 0


def solveBoard():
    solve(0, 0)


def randomFill(localBoard):
    for row in range(len(localBoard)):
        for col in range(len(localBoard[row])):
            if(isOpen(row, col)):
                randValue = random.randint(1, 9)
                localBoard[row][col] = randValue
    return localBoard


def createFirstGeneration():
    generation = list()
    for i in range(5040):
        localBoard = copy.deepcopy(board)
        generation.append(randomFill(localBoard))
    return generation


def assignToBoard(row, col, value):
    board[row][col] = value
    socketio.emit('boardChange', (row, col, value))


def isGivenBoxValid(board, row, col):
    val = board[row][col]
    rowBox = row // 3
    colBox = col // 3

    rowIndexes = rowBox*3
    colIndexes = colBox*3

    count = 0
    for i in range(rowIndexes, rowIndexes+3):
        for j in range(colIndexes, colIndexes + 3):
            if board[i][j] == val:
                count += 1
    return count <= 1


def isGivenRowValid(board, row, col):
    val = board[row][col]
    count = 0
    for col in range(len(board[row])):
        if val == board[row][col]:
            count += 1
    return count <= 1


def isGivenColValid(board, row, col):
    val = board[row][col]
    count = 0
    for row in range(9):
        if val == board[row][col]:
            count += 1
    return count <= 1


def isValidRandomBox(localBoard, row, col):
    global board
    return (board[row][col] != 0) or (isGivenBoxValid(localBoard, row, col) and isGivenRowValid(localBoard, row, col) and isGivenColValid(localBoard, row, col))


def calculateFitness(board):
    fitness = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            if(isValidRandomBox(board, row, col)):
                fitness += 1
    return fitness


def solveStochastic(boards):
    fitnesses = list()
    for index in range(len(boards)):
        fitness = calculateFitness(boards[index])
        if fitness == 81:
            return boards[index]
        printBoard(boards[index])
        print("Fitness is: {}".format(fitness))
        fitnessTuple = (index, fitness)
        fitnesses.append(fitnessTuple)
    fitnesses.sort(key=lambda x: x[1])
    fittestOrganisms = list()
    for i in fitnesses[:8]:
        fittestOrganisms.append(boards[i[0]])
    nextGeneration = breed(fittestOrganisms)
    return solveStochastic(nextGeneration)


def breed(organisms):
    offspring = list()
    for i in range(len(organisms) - 1):
        for j in range(i+1, len(organisms)):
            mom = organisms[i]
            dad = organisms[j]
            child = breedTwoOrganisms(mom, dad)
            offspring.append(child)
    return offspring


def breedTwoOrganisms(mom, dad):
    child = createEmptyBoard()
    for rowIndex in range(len(mom)):
        for colIndex in range(len(mom[rowIndex])):
            if(isValidRandomBox(mom, rowIndex, colIndex)):
                if (isValid(child, rowIndex, colIndex, mom[rowIndex][colIndex])):
                    child[rowIndex][colIndex] = mom[rowIndex][colIndex]
                else:
                    for i in range(1, 10):
                        if (isValid(mom, rowIndex, colIndex, i) or isValid(dad, rowIndex, colIndex, i)):
                            child[rowIndex][colIndex] = i
                    child[rowIndex][colIndex] = random.randint(1, 9)
            elif (isValidRandomBox(dad, rowIndex, colIndex)):
                if (isValid(child, rowIndex, colIndex, dad[rowIndex][colIndex])):
                    child[rowIndex][colIndex] = dad[rowIndex][colIndex]
                else:
                    for i in range(1, 10):
                        if (isValid(mom, rowIndex, colIndex, i) or isValid(dad, rowIndex, colIndex, i)):
                            child[rowIndex][colIndex] = i
                    child[rowIndex][colIndex] = random.randint(1, 9)
            else:
                for i in range(1, 10):
                    if (isValid(mom, rowIndex, colIndex, i) or isValid(dad, rowIndex, colIndex, i)):
                        child[rowIndex][colIndex] = i
                child[rowIndex][colIndex] = random.randint(1, 9)
    return child


def createEmptyBoard():
    board = [[0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0, 0]]
    return board


def printBoard(board):
    for row in board:
        print(row)


@app.route('/')
def hello_world():
    return render_template('index.html', board=board)


@app.route('/reset')
def reset():
    reset_board()
    return redirect(url_for('hello_world'))


@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))
    emit('myResponse')


@socketio.on('delayChange')
def handle_delay_change(slider_value):
    slider_value = int(slider_value)
    new_delay = 1/(100**slider_value)
    adjust_delay(new_delay)


@socketio.on('solve')
def solver():
    solveBoard()


@socketio.on('stochastic')
def stochastic():
    global board
    firstGen = createFirstGeneration()
    board = solveStochastic(firstGen)
    return redirect(url_for('hello_world'))


def reset_board():
    global board
    board = copy.deepcopy(initialBoard)


def adjust_delay(new_delay):
    global delay
    delay = new_delay


if __name__ == '__main__':
    reset_board()
    socketio.run(app, debug=True)
