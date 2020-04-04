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
        self.socket.emit('cellChange', (row, col, possibleNumber))
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