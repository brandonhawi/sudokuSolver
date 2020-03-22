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

def isOpenOnBoard(localBoard, row, column):
    return isOpen(row, column) and localBoard[row][column]

def isOpen(row, col):
    return board[row][col] == 0

def randomFill(localBoard):
    for row in range(len(localBoard)):
        for col in range(len(localBoard[row])):
            if(isOpen(row, col)):
                randValue = random.randint(1, 9)
                localBoard[row][col] = randValue
    return localBoard


def createFirstGeneration():
    generation = list()
    for i in range(10):
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
    return (board[row][col] != 0) or isGivenBoxValid(localBoard, row, col)


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
        fitnessTuple = (index, fitness)
        fitnesses.append(fitnessTuple)
    fitnesses.sort(key=lambda x: -x[1])
    fittestOrganisms = list()
    for i in fitnesses[:4]:
        fittestOrganisms.append(boards[i[0]])
    nextGeneration = breed(fittestOrganisms)
    fitnesses.reverse()
    for i in range(6):
        leastFitIndex = fitnesses[i][0]
        boards[leastFitIndex] = nextGeneration[i]
        socketio.emit("generationChange", fitnesses[i])
    time.sleep(5)
    return solveStochastic(boards)

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
                child[rowIndex][colIndex] = mom[rowIndex][colIndex]
            elif (isValidRandomBox(dad, rowIndex, colIndex)):
                child[rowIndex][colIndex] = dad[rowIndex][colIndex]
            else:
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

@socketio.on('stochastic')
def stochastic():
    global board
    global firstGen
    board = solveStochastic(firstGen)
    return redirect('/')


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

@app.route('/stochastic')
def stochasticRoute():
    global firstGen
    firstGen = createFirstGeneration()
    return render_template('stochastic.html', boards=firstGen)

if __name__ == '__main__':
    socketio.run(app, debug=True)