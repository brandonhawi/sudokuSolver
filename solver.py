board = list()


def printBoard():
    print("-----------------")
    for row in board:
        for col in row:
            print(col, end=" ")
        print()
    print("-----------------")


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


def solve(row, col):
    for posValue in range(1, 10):
        if(isOpen(row, col)):
            if isValid(row, col, posValue):
                board[row][col] = posValue
                if row+1 == 9 and col+1 == 9:
                    return True
                elif col+1 == 9:
                    if solve(row+1, 0):
                        return True
                    else:
                        board[row][col] = 0
                else:
                    if solve(row, col+1):
                        return True
                    else:
                        board[row][col] = 0
        else:
            if row + 1 == 9 and col + 1 == 9:
                return True
            elif col + 1 == 9:
                return solve(row+1, 0)
            else:
                return solve(row, col+1)
    return False


def isOpen(row, col):
    return board[row][col] == 0


def solveBoard(inputBoard):
    global board 
    board = inputBoard
    solve(0, 0)
    return board
