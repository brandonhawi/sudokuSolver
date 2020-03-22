import time

class backtrackSolver:
    def __init__(self, classBoard, givenSocket):
        self.board = classBoard
        self.socket = givenSocket
        self.delay = 0.1
    
    def solve(self, row, col):
        for possibleNumber in range(1, 10):
            if(self.isOpen(row, col)):
                self.displayBoardChange(row, col, possibleNumber)
                if (self.isValid(row, col, possibleNumber)):
                    self.changeBoard(row, col, possibleNumber)
                    if (self.atEndOfBoard(row, col)):
                        return True
                    elif (self.atEndOfRow(col)):
                        if self.solve(row + 1, 0):
                            return True
                        else:
                            self.changeBoardAndDisplay(row, col, 0)
                    else:
                        if self.solve(row, col + 1):
                            return True
                        else:
                            self.changeBoardAndDisplay(row, col, 0)
            else:
                if self.atEndOfBoard(row, col):
                    return True
                elif self.atEndOfRow(col):
                    return self.solve(row + 1, 0)
                else:
                    return self.solve(row, col+1)
        self.changeBoardAndDisplay(row, col, 0)
        return False

    def changeBoard(self, row, col, newNumber):
        self.board[row][col] = newNumber

    def displayBoardChange(self, row, col, possibleNumber):
        self.socket.emit('boardChange', (row, col, possibleNumber))
        time.sleep(self.delay)

    def changeBoardAndDisplay(self, row, col, newNumber):
        self.changeBoard(row, col, newNumber)
        self.displayBoardChange(row, col, newNumber)

    def isOpen(self, row, col):
        return self.board[row][col] == 0

    def isValid(self, row, col, val):
        return self.isValidRow(row, val) and self.isValidCol(col, val) and self.isValidBox(row, col, val)

    def isValidRow(self, row, val):
        for col in range(9):
            if val == self.board[row][col]:
                return False
        return True

    def isValidCol(self, col, val):
        for row in range(9):
            if val == self.board[row][col]:
                return False
        return True

    def isValidBox(self, row, col, val):
        #   (0,0) | (0,1) | (0,2)
        #   ----------------------
        #   (1,0) | (1,1) | (1,2)
        #   ----------------------
        #   (2,0) | (2,1) | (2,2)

        rowBox = row // 3
        colBox = col // 3

        rowStartIndex = rowBox*3
        colStartIndex = colBox*3

        for i in range(rowStartIndex, rowStartIndex+3):
            for j in range(colStartIndex, colStartIndex + 3):
                if self.board[i][j] == val:
                    return False
        return True
    
    def atEndOfBoard(self, rowIndex, colIndex):
        return self.atEndOfCol(rowIndex) and self.atEndOfRow(colIndex)

    def atEndOfRow(self, colIndex):
        return colIndex + 1 == 9

    def atEndOfCol(self, rowIndex):
        return rowIndex + 1 == 9

    def changeDelay(self, newDelay):
        self.delay = newDelay


class stochasticSolver:
    def __init__(self, initBoard, givenSocket):
        self.board = initBoard
        self.socket = givenSocket
        self.delay = 1
    
    def solve(self, generation):
        fitnesses = list()
        for index in range(len(generation)):
            fitness = self.calculateFitness(generation[index])
            if fitness == 81:
                return generation[index]
            fitnessTuple = (index, fitness)
            fitnesses.append(fitnessTuple)
        fitnesses.sort(key=lambda x: -x[1])
        fittestOrganisms = list()
        for i in fitnesses[:4]:
            fittestOrganisms.append(generation[i[0]])
        nextGeneration = breed(fittestOrganisms)
        fitnesses.reverse()
        for i in range(6):
            leastFitIndex = fitnesses[i][0]
            generation[leastFitIndex] = nextGeneration[i]
            socketio.emit("generationChange", fitnesses[i])
        time.sleep(5)
        return self.solve(generation)
    
    def calculateFitness(self, organism):
        fitness = 0
        for row in range(len(organism)):
            for col in range(len(organism[row])):
                if(self.isInInitialBoard(row, col, organism) or self.isFit(row, col, organism)):
                    fitness += 1
        return fitness
    
    def isInInitialBoard(self, row, col, organism):
        return self.board[row][col] == organism[row][col]

    def isFit(self, row, col, organism):
        valueInQuestion = organism[row][col]
        rowBox = row // 3
        colBox = col // 3

        rowIndexes = rowBox*3
        colIndexes = colBox*3

        count = 0
        for i in range(rowIndexes, rowIndexes+3):
            for j in range(colIndexes, colIndexes + 3):
                if organism[i][j] == valueInQuestion:
                    count += 1
        return count <= 1