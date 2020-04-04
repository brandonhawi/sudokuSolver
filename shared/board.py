class Board:
    def __init__(self, initBoard):
        self._boardArray = initBoard

    def getBoardArray(self):
        return self._boardArray

    def setBoardArray(self, newBoardArray):
        self._boardArray = newBoardArray

    boardArray = property(getBoardArray, setBoardArray)

    def serialize(self):
        return {
            'boardArray': self.boardArray
        }

    def __getitem__(self, rowIndex):
        # Overrides Board[row]
        return self.getBoardArray()[rowIndex]

    def __str__(self):
        output = "Board Object: \n"
        for i in self.boardArray:
            output += str(i) + "\n"
        return output
    
    def __repr__(self):
        return str(self)