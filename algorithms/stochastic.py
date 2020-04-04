from flask import json
import copy
import random

#TODO: Clean this up. Refactor and focus on the evolutionary part. 

# class stochasticSolver:
#     def __init__(self, initBoard, givenSocket):
#         self.board = initBoard
#         self.socket = givenSocket
#         self.delay = 1

#     def solve(self, generationSize):
#         firstGeneration = self.createRandomSizeNGeneration(generationSize)
#         #self.displayGeneration(firstGeneration)
#         return self.evolve(firstGeneration)

#     def createRandomSizeNGeneration(self, n):
#         generation = list()
#         for i in range(n):
#             cloneBoard = self.copyInitBoard()
#             randomizedBoard = self.randomFill(cloneBoard)
#             generation.append(randomizedBoard)
#         return generation

#     def randomFill(self, givenBoard):
#         givenBoardArray = givenBoard.boardArray
#         for rowIndex in range(len(givenBoardArray)):
#             for colIndex in range(len(givenBoardArray[rowIndex])):
#                 if(self.isOpen(givenBoard, rowIndex, colIndex)):
#                     randValue = random.randint(1, 9)
#                     givenBoardArray[rowIndex][colIndex] = randValue
#         givenBoard.boardArray = givenBoardArray
#         return givenBoard

#     def evolve(self, generation):
#         print("Generation Size: {}".format(len(generation)))
#         totalFitness = 0
#         for currentBoard in generation:
#             currentBoard.fitness = self.calculateFitness(currentBoard)
#             totalFitness += currentBoard.fitness[0] + currentBoard.fitness[1] + currentBoard.fitness[2]
#             if currentBoard.fitness[0] + currentBoard.fitness[1] + currentBoard.fitness[2] == 27:
#                 return currentBoard
#         print("Generation Total Fitness: {}".format(totalFitness))
#         sortedGeneration = self.sortByHighestFitness(generation)
#         breededOrganisms = self.breedNFittestOrganisms(100, sortedGeneration)
#         nextGeneration = self.createNextGeneration(
#             sortedGeneration, breededOrganisms)
#         return self.evolve(nextGeneration)

#     def sortByHighestFitness(self, generation):
#         generation.sort(key=lambda x: -(x.fitness[0] + x.fitness[1] + x.fitness[2]))
#         return generation

#     def calculateFitness(self, organism):
#         fitness = (self.totalRowFitness(organism), self.totalColFitness(organism), self.totalBoxFitness(organism))
#         # for row in range(len(organism.boardArray)):
#         #     for col in range(len(organism.boardArray[row])):
#         #         if(self.isInInitialBoard(row, col, organism) or self.isFit(row, col, organism)):
#         #             fitness += 1
#         return fitness

#     def totalRowFitness(self, organism):
#         fitness = 0
#         for row in range(len(organism.boardArray)):
#             if (self.isListFit(organism.boardArray[row])):
#                 fitness += 1
#         return fitness

#     def totalColFitness(self, organism):
#         fitness = 0
#         for col in range(9):
#             columnList = list()
#             for row in range(9):
#                 columnList.append(organism.boardArray[row][col])
#             if (self.isListFit(columnList)):
#                 fitness += 1
#         return fitness
    
#     def totalBoxFitness(self, organism):
#         fitness = 0
#         for rowBox in range(2):
#             for colBox in range(2):
#                 rowIndexes = rowBox*3
#                 colIndexes = colBox*3
#                 boxList = list()
#                 for i in range(rowIndexes, rowIndexes+3):
#                     for j in range(colIndexes, colIndexes + 3):
#                         boxList.append(organism.boardArray[i][j])
#                 if (self.isListFit(boxList)):
#                     fitness += 1
#         return fitness
    
#     def isListFit(self, givenList):
#         return len(givenList) == len(set(givenList))

#     def breedNFittestOrganisms(self, n, sortedGeneration):
#         fittestOrganisms = self.getNFittestOrganisms(n, sortedGeneration)
#         breededOrganisms = self.breed(fittestOrganisms)
#         return breededOrganisms

#     def getNFittestOrganisms(self, n, sortedGeneration):
#         fittestOrganisms = list()
#         for i in sortedGeneration[:n]:
#             fittestOrganisms.append(i)
#         return fittestOrganisms

#     def isInInitialBoard(self, row, col, organism):
#         return self.board.boardArray[row][col] == organism.boardArray[row][col]

#     def isFit(self, row, col, organism):
#         return self.validBox(row, col, organism) and self.validRow(row, col, organism) and self.validCol(row, col, organism)

#     def validBox(self, row, col, organism):
#         organism = organism.boardArray
#         valueInQuestion = organism[row][col]
#         rowBox = row // 3
#         colBox = col // 3

#         rowIndexes = rowBox*3
#         colIndexes = colBox*3

#         count = 0
#         for i in range(rowIndexes, rowIndexes+3):
#             for j in range(colIndexes, colIndexes + 3):
#                 if organism[i][j] == valueInQuestion:
#                     count += 1
#         return count <= 1

#     def validRow(self, row, col, organism):
#         organism = organism.boardArray
#         valueInQuestion = organism[row][col]
#         count = 0
#         for col in range(len(organism[row])):
#             if organism[row][col] == valueInQuestion:
#                 count += 1
#         return count <= 1

#     def validCol(self, row, col, organism):
#         organism = organism.boardArray
#         valueInQuestion = organism[row][col]
#         count = 0
#         for row in range(9):
#             if organism[row][col] == valueInQuestion:
#                 count += 1
#         return count <= 1

#     def breed(self, organisms):
#         offspring = list()
#         for i in range(len(organisms) - 1):
#             for j in range(i+1, len(organisms)):
#                 parent1 = organisms[i]
#                 parent2 = organisms[j]
#                 child = self.breedTwoOrganisms(parent1, parent2)
#                 offspring.append(child)
#         return offspring

#     def breedTwoOrganisms(self, parent1, parent2):
#         child = self.copyInitBoard()
#         childArray = child.boardArray
#         if (parent1.fitness[0] == 9):
#             if (parent1.fitness[1] == 9):
#                 # If all rows and columns are good, 
#             # If all rows are fit, only change columns at a time
#             parent1Array = copy.deepcopy(parent1.boardArray)
#             randomIndex = list(range(9))
#             random.shuffle(randomIndex)
#             for rows in range(9):
#                 for cols in range(9):
#                     childArray[rows][cols] = parent1Array[rows][randomIndex[cols]]
#         else:
#             for rowIndex in range(len(childArray)):
#                 if (self.isListFit(parent1.boardArray[rowIndex])):
#                     childArray[rowIndex] = parent1.boardArray[rowIndex]
#                 elif (self.isListFit(parent2.boardArray[rowIndex])):
#                     childArray[rowIndex] = parent2.boardArray[rowIndex]
#                 else:
#                     for colIndex in range(len(childArray[rowIndex])):
#                         childArray[rowIndex][colIndex] = random.randint(1, 9)
#             # for rows in range(9):
#             #     for cols in range(9):
#             #         hereditaryChance = random.randint(1,3)
#             #         if (hereditaryChance == 1):
#             #             childArray[rows][cols] = parent1.boardArray[rows][cols]
#             #         elif (hereditaryChance == 2):
#             #             childArray[rows][cols] = parent2.boardArray[rows][cols]
#             #         else:
#             #             childArray[rows][cols] = random.randint(1, 9)
#         # for rowIndex in range(len(childArray)):
#         #     if (parent1.fitness[0] == 9):
#         #         # If rows have one of each number, shuffling will not change the totalRowFitness
#         #         parent1Array = copy.deepcopy(parent1.boardArray[rowIndex])
#         #         random.shuffle(parent1Array)
#         #         childArray[rowIndex] = parent1Array
#         #     else:
#         #         for colIndex in range(9):
#         #             if (self.isOpen(child, rowIndex, colIndex)):
#         #                 childArray[rowIndex][colIndex] = random.randint(1, 9)
#             # for colIndex in range(len(childArray[rowIndex])):
#             #     if(self.isOpen(child, rowIndex, colIndex)):
#             #         if (parent1.boardArray[rowIndex][colIndex] == parent2.boardArray[rowIndex][colIndex]):
#             #             hereditaryChance = random.randint(1,2)
#             #             if (hereditaryChance == 1 ):
#             #                 childArray[rowIndex][colIndex] = parent1.boardArray[rowIndex][colIndex]
#             #             else:
#             #                 childArray[rowIndex][colIndex] = parent2.boardArray[rowIndex][colIndex]
#             #         else:
#             #             hereditaryChance = random.randint(1,3)
#             #             if (hereditaryChance == 1 ):
#             #                 childArray[rowIndex][colIndex] = parent1.boardArray[rowIndex][colIndex]
#             #             elif (hereditaryChance == 2):
#             #                 childArray[rowIndex][colIndex] = parent2.boardArray[rowIndex][colIndex]
#             #             else:
#             #                 childArray[rowIndex][colIndex] = random.randint(1, 9)
#                     #########
#                     # if (self.isListFit(parent1.boardArray[rowIndex])):
#                     #     childArray[rowIndex][colIndex] = parent1.boardArray[rowIndex][colIndex]
#                     # elif (self.isListFit(parent2.boardArray[rowIndex])):
#                     #     childArray[rowIndex][colIndex] = parent2.boardArray[rowIndex][colIndex]
#                     # else:
#                     #     childArray[rowIndex][colIndex] = random.randint(1, 9)
#                     #########
#                     # isParent1Fit = self.isFit(rowIndex, colIndex, parent1)
#                     # isParent2Fit = self.isFit(rowIndex, colIndex, parent2)
#                     # if (isParent1Fit and isParent2Fit):
#                     #     hereditaryChance = random.randint(1,10)
#                     #     if (hereditaryChance < 5):
#                     #         childArray[rowIndex][colIndex] = parent1.boardArray[rowIndex][colIndex]
#                     #     elif (5 < hereditaryChance < 10):
#                     #         childArray[rowIndex][colIndex] = parent2.boardArray[rowIndex][colIndex]
#                     #     else:
#                     #         childArray[rowIndex][colIndex] = random.randint(1, 9)         
#                     # elif(isParent1Fit):
#                     #     childArray[rowIndex][colIndex] = parent1.boardArray[rowIndex][colIndex]
#                     # elif (isParent2Fit):
#                     #     childArray[rowIndex][colIndex] = parent2.boardArray[rowIndex][colIndex]
#                     # else:
#                     #     childArray[rowIndex][colIndex] = random.randint(1, 9)
#         return child

#     def isOpen(self, givenBoard, rowIndex, colIndex):
#         return givenBoard.boardArray[rowIndex][colIndex] == 0

#     def copyInitBoard(self):
#         clonedBoardArray = copy.deepcopy(self.board.boardArray)
#         return Board(clonedBoardArray)

#     def createNextGeneration(self, sortedGeneration, breededOrganisms):
#         numToBeReplaced = len(breededOrganisms)
#         offset = len(sortedGeneration) - numToBeReplaced
#         for index in range(len(breededOrganisms)):
#             sortedGeneration[index + offset] = breededOrganisms[index]
#         return sortedGeneration

#     def displayGeneration(self, generation):
#         generation = list(map(lambda x: x.serialize(), generation))
#         self.socket.emit("displayGeneration", generation)
