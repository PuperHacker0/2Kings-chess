try:
    import os, sys, time, pygame, subprocess
except ImportError:
    print("Error importing one or more modules. Please make sure that you have installed pygame.")
    os.system("PAUSE")
    sys.exit(0)

class PieceSprite(object):
    def __init__(self, ID, sprite):
        self.sprite = sprite
        self.ID = ID

class board(object):
    def __init__(self, squaresPerSide, colorOnTheBottom):
        self.pieceSprites = {}
        self.squaresPerSide = squaresPerSide
        self.spritePositions = [[0 for x in range(self.squaresPerSide)] for x in range(self.squaresPerSide)]
        self.colorOnTheBottom = colorOnTheBottom

    def getIDFromFullName(self, fullName):
        splitName = fullName.split()

        if splitName[1] == "King":
            splitName[1] = "+"

        return splitName[0][0] + splitName[1][0]

    def getPieceSprites(self):
        pieceNames = ["Rook", "Knight", "Bishop", "Queen", "King", "Pawn"]
        self.pieceSprites.update({ "SQ" : PieceSprite("SQ", 0) }) #Empty square
        
        for pieceName in pieceNames:
            whitePath = "Depend\\White " + pieceName + ".png"
            blackPath = "Depend\\Black " + pieceName + ".png"

            if not os.path.isfile(whitePath):
                raise IOError("missing the image of the White " + pieceName)
            elif not os.path.isfile(blackPath):
                raise IOError("missing the image of the Black " + pieceName)

            whiteID, blackID = self.getIDFromFullName("White " + pieceName), self.getIDFromFullName("Black " + pieceName)
            self.pieceSprites.update({ whiteID : PieceSprite(whiteID, pygame.image.load(whitePath)) })
            self.pieceSprites.update({ blackID : PieceSprite(blackID, pygame.image.load(blackPath)) })

    def resizeSpritesToSquareSize(self, pixelSize):
        for pieceSprite in self.pieceSprites.values():
            if pieceSprite.sprite != 0:
                pieceSprite.sprite = pygame.transform.scale(pieceSprite.sprite, (pixelSize, pixelSize))

    def setSpritePositionsFromFile(self, fileDirectory):
        if not os.path.isfile(fileDirectory):
            raise IOError("missing board position file")

        file = open(fileDirectory, "r")

        for rowCounter in range(self.squaresPerSide):
            columnCounter = 0
            
            for pieceID in file.readline().split():
                self.spritePositions[rowCounter][columnCounter] = self.pieceSprites.get(pieceID, "Error")
                    
                if self.spritePositions[rowCounter][columnCounter] == "Error":
                    raise IOError("board position file contains invalid information")
                columnCounter += 1
            
        wrongNumberOfColumns = False
        for row in self.spritePositions:
            if len(row) != self.squaresPerSide:
                wrongNumberOfColumns = True
                break

        if len(self.spritePositions) != self.squaresPerSide or wrongNumberOfColumns:
            file.close()
            raise IOError("board position file contains invalid information")

        file.close()

    def playMove(self, p):
        tmp = self.spritePositions[p.squareFrom[1]][p.squareFrom[0]]
        self.spritePositions[p.squareFrom[1]][p.squareFrom[0]] = self.spritePositions[p.squareTo[1]][p.squareTo[0]]
        self.spritePositions[p.squareTo[1]][p.squareTo[0]] = tmp

    def writePositionToFile(self, fileDirectory, depthOfSearch, playerMoveToBeValidated, colorOfPlayer):
        try:
            file = open(fileDirectory, "w")

            file.write("%d %d " % (self.squaresPerSide, depthOfSearch) + self.colorOnTheBottom + " " + colorOfPlayer + '\n')
            for y in range(self.squaresPerSide):
                for x in range(self.squaresPerSide):
                    file.write(self.spritePositions[y][x].ID)

                    if x == self.squaresPerSide - 1:
                        if y != self.squaresPerSide - 1:
                            file.write('\n')
                    else: file.write(' ')

            file.write("\n%d %d --> %d %d" % (playerMoveToBeValidated.squareFrom[0], playerMoveToBeValidated.squareFrom[1],
                                              playerMoveToBeValidated.squareTo[0], playerMoveToBeValidated.squareTo[1]))

            file.close()
        except IOError:
            raise IOError("Cannot write to " + fileName)

    def drawSquares(self, squareFromSelected = (-1, -1), squareToSelected = (-1, -1)):
        RGBBrown, RGBWhite, RGBYellow = (190, 80, 70), (255, 255, 255), (200, 200, 0)

        blockIsBlack = False
        for y in range(self.squaresPerSide):
            for x in range(self.squaresPerSide):
                if (x == squareFromSelected[0] and y == squareFromSelected[1]) or (x == squareToSelected[0] and y == squareToSelected[1]):
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
                if self.spritePositions[row][column].sprite != 0:
                    window.blit(self.spritePositions[row][column].sprite, (column * sizeOfSquare, row * sizeOfSquare))

class ply(object):
    def __init__(self):
        self.squareFrom = (-1, -1)
        self.squareTo = (-1, -1)
        self.squareFromSelected, self.squareToSelected = False, False

    def setSquareFrom(self, newSquareFrom):
        self.squareFrom = (newSquareFrom[0], newSquareFrom[1])

    def setSquareTo(self, newSquareToInPixels):
        self.squareTo = (newSquareToInPixels[0], newSquareToInPixels[1])

    def __eq__(self, other):
        return self.squareFrom == other.squareFrom and self.squareTo == other.squareTo

    def isValid(self):
        return self.squareFrom != (-1, -1) and self.squareTo != (-1, -1)

class moveBuffer(object):
    def __init__(self, depthOfSearch):
        self.sizeOfBuffer = depthOfSearch
        self.buffer = [ply() for x in range(depthOfSearch)]
        self.bufferPtr = depthOfSearch

    def nextMove(self):
        self.bufferPtr += 1

        if self.bufferPtr > self.sizeOfBuffer:
            return ply()

        return self.buffer[self.bufferPtr - 1]

    def loadMovesFromFile(self, fileDirectory):
        if not os.path.isfile(fileDirectory):
            raise IOError("failed to locate move buffer file")
        
        file = open(fileDirectory, "r")

        if file.readline() != "MOVE_VALID\n":
            return False

        fileLines = file.readlines()

        try:
            lineCounter = 0

            for line in fileLines:
                line = line.split()

                if len(line) != 5:
                    raise IOError("move buffer file contains invalid information")

                self.buffer[lineCounter].setSquareFrom((int(line[0]), int(line[1])))
                self.buffer[lineCounter].setSquareTo((int(line[3]), int(line[4])))

                lineCounter += 1
        except (ValueError, KeyError):
            raise IOError("move buffer file contains invalid information")
            
        return True

    def resetPtr(self):
        self.bufferPtr = 0

def loadApplicationIcon(fileDirectory):
    if os.path.exists(fileDirectory):
        pygame.display.set_icon(pygame.image.load(fileDirectory))
    else:
        print("Warning: failed to load the application icon.")


squaresOnSideOfBoard, sizeOfSquare = 8, 100
colorOnTheBottomOfTheBoard, colorOfPlayer = 'W', 'W'
Board = board(squaresOnSideOfBoard, colorOnTheBottomOfTheBoard)

try:
    print("Loading piece sprites...")
    Board.getPieceSprites()
    print("Formatting piece sprites...")
    Board.resizeSpritesToSquareSize(sizeOfSquare)
    print("Parsing position file...")
    Board.setSpritePositionsFromFile("Depend\\Starting Position.txt")
except IOError as e:
    print("Fatal error: " + str(e) + ".")
    sys.exit(0)

print("Creating application interface...\n\n")
pygame.init()
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d, %d" % (100, 100)
defaultWindowTitleCaption = "2Kings v0.1 by Puperhacker"
window = pygame.display.set_mode((Board.squaresPerSide * sizeOfSquare, Board.squaresPerSide * sizeOfSquare))
pygame.display.set_caption(defaultWindowTitleCaption)
loadApplicationIcon("Depend\\Application icon.jpg")

depthOfSearch = 4
movebuffer = moveBuffer(depthOfSearch - 1)
playerMove = ply()
endOfGame = False

def drawToWindow(Board, playerMove):
    if playerMove.squareFromSelected and playerMove.squareToSelected:
        Board.drawSquares(playerMove.squareFrom, playerMove.squareTo)
    elif playerMove.squareFromSelected:
        Board.drawSquares(playerMove.squareFrom)
    else:
        Board.drawSquares()
    Board.drawPieces()
    pygame.display.update()

def processWindowEvents(windowEvents):
    for event in windowEvents:
        if event.type == pygame.QUIT:
            endOfGame = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mousePositionSquare = pygame.mouse.get_pos()
            mousePositionSquare = tuple(coordinate // sizeOfSquare for coordinate in mousePositionSquare)

            if playerMove.squareFromSelected:
                playerMove.setSquareTo(mousePositionSquare)
                playerMove.squareToSelected = True

                Board.writePositionToFile("Depend\\currentPosition.txt", depthOfSearch, playerMove, colorOfPlayer)
            else:
                playerMove.squareFromSelected = True
                playerMove.setSquareFrom(mousePositionSquare)

engineProcess = 0
while not endOfGame:
    try:
        drawToWindow(Board, playerMove)
        pygame.time.delay(60)
        processWindowEvents(pygame.event.get())

        if playerMove.squareFromSelected and playerMove.squareToSelected:
            drawToWindow(Board, playerMove)
            playerMove.squareFromSelected, playerMove.squareToSelected = False, False
            predictedPlayerMove, predictedPlayerMoveResponse = movebuffer.nextMove(), movebuffer.nextMove()

            if predictedPlayerMove == playerMove and predictedPlayerMoveResponse.isValid():
                Board.playMove(predictedPlayerMove)
                Board.playMove(predictedPlayerMoveResponse)
                print("Predicted player's move.")
            else:
                Board.writePositionToFile("Depend\\currentPosition.txt", depthOfSearch, playerMove, colorOfPlayer)
                
                if not os.path.isfile("Depend\\2Kings Engine.exe"):
                    raise IOError("failed to locate file \"2Kings Engine.exe\"")

                pygame.display.set_caption(defaultWindowTitleCaption + " [THINKING]")
                startingTimeOfProcessing = time.time()
                engineProcess = subprocess.Popen("Depend\\2Kings Engine.exe", cwd = "Depend")

                while engineProcess.poll() == None:
                    processWindowEvents(pygame.event.get())

                if not movebuffer.loadMovesFromFile("Depend\\MovesToBeBuffered.txt"):
                    movebuffer.bufferPtr -= 2 #Move was invalid, restore the two read moves
                    continue

                movebuffer.resetPtr()
                pygame.display.set_caption(defaultWindowTitleCaption)
                print("Time elapsed: ~", int(time.time() - startingTimeOfProcessing), " seconds.", sep = '')
                Board.setSpritePositionsFromFile("Depend\\processedPosition.txt")

    except IOError as e:
        print("Fatal error: " + str(e) + ".")
        sys.exit(0)

pygame.quit()
os.system("PAUSE")
