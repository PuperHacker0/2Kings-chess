import pygame
import os
import sys
from subprocess import Popen
import time

class ply(object):
    def __init__(self):
        self.squareFrom = (0, 0)
        self.squareTo = (0, 0)
        self.squareFromSelected, self.squareToSelected = False, False

    def setSquareFrom(self, newSquareFrom):
        newFrom = (newSquareFrom[0] // 100, newSquareFrom[1] // 100)
        self.squareFrom = newFrom

    def setSquareTo(self, newSquareTo):
        newTo = (newSquareTo[0] // 100, newSquareTo[1] // 100)
        self.squareTo = newTo

class board(object):
    namesOfSymbols = {}

    def __init__(self, squares, colorOnTheBottom):
        self.pieceSprites = {}
        self.spritePositions = []
        self.colorOnTheBottom = colorOnTheBottom
        self.squaresPerSide = squares

    def getPieceSprites(self):
        pieceNames = ["Rook", "Knight", "Bishop", "Queen", "King", "Pawn"]
        for pieceName in pieceNames:
            try:
                whitePath = "Depend\\White " + pieceName + ".png"
                blackPath = "Depend\\Black " + pieceName + ".png"

                if os.path.isfile(whitePath):
                    self.pieceSprites.update({"White " + pieceName : pygame.image.load(whitePath)})
                else: raise IOError("White " + pieceName)

                if os.path.isfile(blackPath):
                    self.pieceSprites.update({"Black " + pieceName : pygame.image.load(blackPath)})
                else:
                    raise IOError("Black " + pieceName)

            except IOError as e:
                print("Fatal error: missing the image of the " + str(e) + ".")
                raise IOError

    def resizeSpritesToSquareSize(self, pixelSize):
        for spriteName, sprite in self.pieceSprites.items():
            self.pieceSprites[spriteName] = pygame.transform.scale(sprite, (pixelSize, pixelSize))

    def setSpritePositionsFromFile(self, fileDirectory):
        try:
            if not os.path.isfile(fileDirectory):
                raise IOError("Missing board position file")

            file = open(fileDirectory, "r")
            rowCounter = 0
            self.spritePositions = [[] for x in range(self.squaresPerSide)]

            for rowCounter in range(self.squaresPerSide):
                for position in file.readline().split():
                    if position == "SQ": #Empty Square
                        self.spritePositions[rowCounter].append(("SQ", 0))
                    else:
                        fullNameOfPiece = board.namesOfSymbols.get(position, "Error")
                        if fullNameOfPiece == "Error":
                            raise IOError("Board position file contains invalid information")

                        self.spritePositions[rowCounter].append((position, self.pieceSprites[fullNameOfPiece]))

            if len(self.spritePositions) != self.squaresPerSide:
                raise IOError("Board position file contains invalid information")
            for row in self.spritePositions:
                if len(row) != self.squaresPerSide:
                    raise IOError("Board position file contains invalid information")

        except Exception as e:
            print("Fatal error: " + str(e) + ".")
            raise IOError

        file.close()

    def drawSquares(self, squareSelected = (-1, -1)):
        RGBBrown, RGBWhite, RGBYellow = (190, 80, 70), (255, 255, 255), (200, 200, 0)

        blockIsBlack = False
        for y in range(self.squaresPerSide):
            for x in range(self.squaresPerSide):
                if x == squareSelected[0] and y == squareSelected[1]:
                    pygame.draw.rect(window, RGBYellow, (x * sizeOfSquare, y * sizeOfSquare, sizeOfSquare, sizeOfSquare))
                elif blockIsBlack:
                    pygame.draw.rect(window, RGBBrown, (x * sizeOfSquare, y * sizeOfSquare, sizeOfSquare, sizeOfSquare))
                else:
                    pygame.draw.rect(window, RGBWhite, (x * sizeOfSquare, y * sizeOfSquare, sizeOfSquare, sizeOfSquare))

                if x != self.squaresPerSide - 1:
                    blockIsBlack = not blockIsBlack

    def drawPieces(self):
        for row in range(self.squaresPerSide):
            for column in range(self.squaresPerSide):
                if self.spritePositions[row][column][1] != 0:
                    window.blit(self.spritePositions[row][column][1], (column * sizeOfSquare, row * sizeOfSquare))
     
    def getNamesOfSymbols(self, fileDirectory):
        try:
            if not os.path.isfile(fileDirectory):
                raise IOError("Missing \"Material Names.txt\"")
            file = open(fileDirectory, "r")

            for pieceName in file.readlines():
                pieceName = pieceName.split()

                if len(pieceName) != 4:
                    raise IOError("Error reading file \"Material Names.txt\"")
                board.namesOfSymbols[pieceName[0]] = pieceName[2] + " " + pieceName[3]

        except Exception as e:
            print("Fatal error: " + str(e) + ".")
            raise IOError

        file.close()

    def writePositionToFile(self, fileDirectory, depthOfSearch, playerMoveToBeValidated, colorOfPlayer):
        try:
            file = open(fileDirectory, "w")

            file.write("%d %d " % (self.squaresPerSide, depthOfSearch) + self.colorOnTheBottom + " " + colorOfPlayer + '\n')
            for y in range(self.squaresPerSide):
                for x in range(self.squaresPerSide):
                    file.write(self.spritePositions[y][x][0])

                    if x == self.squaresPerSide - 1:
                        if y != self.squaresPerSide - 1:
                            file.write('\n')
                    else: file.write(' ')

            file.write("\n%d %d --> %d %d" % (playerMoveToBeValidated.squareFrom[0], playerMoveToBeValidated.squareFrom[1],
                                              playerMoveToBeValidated.squareTo[0], playerMoveToBeValidated.squareTo[1]))

            file.close()
        except IOError:
            raise IOError("Cannot write to " + fileName)

    def playMove(self, p):
        self.spritePositions[p.squareTo[1]][p.squareTo[0]] = self.spritePositions[p.squareFrom[1]][p.squareFrom[0]]

class moveBuffer(object):
    def __init__(self, depthOfSearch):
        self.sizeOfBuffer = depthOfSearch
        self.buffer = [ ply() for x in range(depthOfSearch)]
        self.bufferPtr = depthOfSearch

    def moveMatches(self, move):
        if self.bufferPtr < self.sizeOfBuffer and move == self.buffer[self.bufferPtr]:
            return True
        return False

    def getNextEngineMove(self):
        nextMovePtr = self.bufferPtr + 1
        self.bufferPtr += 2 #Both players moved, so move the pointer by 2 places

        if nextMovePtr < self.sizeOfBuffer:
            return self.buffer[nextMovePtr]
        else:
            return 0

    def loadFromFile(self, fileDirectory):
        if not os.path.isfile(fileDirectory):
            raise IOError("Failed to locate move buffer file")
        
        file = open(fileDirectory, "r")
        moveIsValid = file.readline()

        if moveIsValid != "MOVE_VALID": return False

        fileLines = file.readlines()
        try:
            lineCounter = 0
            importedMove = ply()
            for line in fileLines:
                line = line.split()
                if len(line) != 5:
                    raise IOError("Move buffer file contains invalid information")

                importedMove.setSquareFrom((int(line[0]), int(line[1])))
                importedMove.setSquareTo((int(line[3]), int(line[4])))
                buffer[lineCounter] = importedMove

                lineCounter += 1
        except (ValueError, KeyError):
            raise IOError("Move buffer file contains invalid information")
            
        return True
    def resetPtr(self): self.bufferPtr = 0

pygame.init()
squaresOnSideOfBoard = 8
sizeOfSquare = 100
colorOnTheBottomOfTheBoard, colorOfPlayer = 'W', 'W'
depthOfSearch = 4
Board = board(squaresOnSideOfBoard, colorOnTheBottomOfTheBoard)

startingWindowCoordinates = (540, 200)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % startingWindowCoordinates
window = pygame.display.set_mode((Board.squaresPerSide * 100, Board.squaresPerSide * 100))
pygame.display.set_caption("2Kings v0.0")

iconPath = "Depend\\Application icon.jpg"
try:
    if os.path.exists(iconPath):
        appIcon = pygame.image.load(iconPath)
        pygame.display.set_icon(appIcon)
    else: raise IOError
except IOError:
    print("Warning: Failed to load the application icon.")

try:
    Board.getPieceSprites()
except IOError:
    print("Failed to get the images of the pieces.")
    sys.exit(0)

Board.resizeSpritesToSquareSize(sizeOfSquare)

try:
    Board.getNamesOfSymbols("Depend\\Material Names.txt")
    Board.setSpritePositionsFromFile("Depend\\Starting Position.txt")
except IOError:
    print("Failed to read starting position files.")
    sys.exit(0)

endOfGame = False
print("\nApplication started successfully.")
playerMove = ply()
movebuffer = moveBuffer(depthOfSearch - 1)

while not endOfGame:
    pygame.time.delay(30)

    if playerMove.squareFromSelected:
        Board.drawSquares(playerMove.squareFrom)
    else:
        Board.drawSquares()
    Board.drawPieces()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: endOfGame = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if playerMove.squareFromSelected:
                playerMove.setSquareTo(tuple(pygame.mouse.get_pos()))
                
                try:
                    Board.writePositionToFile("Depend\\currentPosition.txt", depthOfSearch, playerMove, colorOfPlayer)
                except IOError as e:
                    print("Fatal error: " + str(e) + ".")
                    sys.exit(0)
                
                playerMove.squareToSelected = True
            else:
                playerMove.squareFromSelected = True
                playerMove.setSquareFrom(tuple(pygame.mouse.get_pos()))

    if playerMove.squareFromSelected and playerMove.squareToSelected:
        expectedPlayerMoveMatches = movebuffer.moveMatches(playerMove)
        PCMove = movebuffer.getNextEngineMove()

        if expectedPlayerMoveMatches and PCMove != 0:
            Board.playMove(PCMove)
        else:
            try:
                Board.writePositionToFile("Depend\\currentPosition.txt", depthOfSearch, playerMove, colorOfPlayer)
            except IOError as e:
                print("Fatal error: " + str(e) + ".")
                sys.exit(0)

            try:
                if not os.path.isfile("Depend\\2KingsEngine.exe"):
                    raise IOError("Failed to locate file \"2KingsEngine.exe\"")

                start = time.time()
                engineProcess = Popen("Depend\\2KingsEngine.exe", cwd = "Depend")
                engineProcess.wait()

                if not movebuffer.loadFromFile("Depend\\MovesToBeBuffered.txt"): #TODO with a try:
                    pass

                print("Time elapsed: ~", int(time.time() - start), " seconds.", sep = '')
                    
                movebuffer.resetPtr()
            except IOError as e:
                print("Fatal error: " + str(e) + ".")
                sys.exit(0)
                #TODO Check if checkmate first

        playerMove.squareFromSelected, playerMove.squareToSelected = False, False
        Board.setSpritePositionsFromFile("Depend\\processedPosition.txt")

pygame.quit()

#os.system("PAUSE") TODO Uncomment for final release
#TODO User needs to have installed pygame? YES FICK
