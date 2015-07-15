# An interface that can load puzzles and receive lists of moves.
# A 'board' is inputted as a string '[rows,cols,[piece1, piece2, ...]]' where pieces have their usual rep (this can be obtained through puzzle.printForLoader())
# A list of moves is inputted as a string '[move1, move2, ...]' where a move is of the form [piece label=entries in its .config, x, y] with x=-1 to send it out of the board


from tkinter import Tk, Entry, Button, Frame, BOTH, LEFT, BOTTOM, END, RIGHT, Canvas
import puzzle as pz
import math
import numpy as np



colourDict = {0:"#ffffff",1:"#ffcc99",2:"#cccccc",3:"#cc00ff",4:"#00ffff",5:"#99ff99",6:"#ffccff",7:"#cc99cc",8:"#cccc00",9:"#00ccff",10:"#99ff00",11:"#990000",12:"#009900",13:"#ccff00",14:"#99ffcc",15:"#999999",16:"#ffcc00",17:"#00cc99",18:"#ff00ff",19:"#ff00cc",20:"#990099",21:"#0000cc",22:"#ccffff",23:"#ff9999",24:"#0099ff",25:"#99ffff",26:"#ff0000",27:"#99ccff",28:"#ccff99",29:"#00cc00",30:"#cc99ff",31:"#9900ff",32:"#0099cc",33:"#ff99cc",34:"#ff0099",35:"#009999",36:"#cc9900",37:"#ffff00",38:"#ff9900",39:"#9999cc",40:"#ffcccc",41:"#9999ff",42:"#ffff99",43:"#ccffcc",44:"#ff99ff",45:"#000099",46:"#ffffcc",47:"#0000ff",48:"#99cccc",49:"#cc0000",50:"#999900",51:"#99cc99",52:"#cccc99",53:"#00ffcc",54:"#00cccc",55:"#99cc00",56:"#00ff99",57:"#cc00cc",58:"#cc0099",59:"#00ff00",60:"#ccccff",61:"#cc9999",62:"#9900cc",63:"#000000"}

defaultStep = 2  # Number of pixels moved at each step
DELAY = 10  # ms delay between animations

#Graphics options
boardColour = "#999999"
gridColour = "#555555"
boxWidth = 50
boxHeight = 50

boardStartX = 40
boardStartY = 40
maxBoardWidth = 200
maxBoardHeight = 200

rosterWidth = 500

extRosterPadding = 40
intRosterPadding = 10

def open():
    root = Tk()
    root.geometry("800x600+100+100")
    window = Window(root)
    root.mainloop()

class Window(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent, background="dark gray")
        self.parent = parent
        self.initUI()
        self.initPuzzles()
        self.run()

    def initUI(self):
        self.parent.title("Block")
        self.pack(fill=BOTH, expand=1)
        self.initCanvas()
        self.initInterfaceZone()

    def initCanvas(self):
        self.canvas = Canvas(self, background="dark gray")
        self.canvas.pack(expand=1,fill=BOTH,padx=1,pady=1)

    def initInterfaceZone(self):
        # Draw the play, step and loading buttons
        self.interfaceFrame = Frame(self, background="dark gray")
        self.playFrame = Frame(self.interfaceFrame, background="dark gray")
        self.loadFrame = Frame(self.interfaceFrame, background="dark gray")

        self.isPlaying = False

        #Do the run buttons
        playButton = Button(self.playFrame, text=">", command=self.playPress)
        playButton.grid(row=0,column=0)
        pauseButton = Button(self.playFrame, text="||", command=self.pausePress)
        pauseButton.grid(row=0,column=1)
        stepBackButton = Button(self.playFrame, text="|<", command=self.stepBackPress)
        stepBackButton.grid(row=1,column=0)
        stepForwardButton = Button(self.playFrame, text=">|", command=self.stepForwardPress)
        stepForwardButton.grid(row=1,column=1)

        self.playFrame.pack(side=LEFT, expand=1, fill=BOTH)

        #Do the load-y stuff
        self.boardInputField = Entry(self.loadFrame)
        self.boardInputField.grid(row=0, column=0)
        boardInputButton = Button(self.loadFrame, text="Load Board", command=self.loadBoardPress)
        boardInputButton.grid(row=0, column=1)
        self.moveInputField = Entry(self.loadFrame)
        self.moveInputField.grid(row=1,column=0)
        moveInputButton = Button(self.loadFrame, text="Load Moves", command=self.loadMovesPress)
        moveInputButton.grid(row=1, column=1)

        self.loadFrame.pack(side=LEFT, expand=1, fill=BOTH)

        self.interfaceFrame.pack(side=BOTTOM)

    def initPuzzles(self):
        self.pieces = [] # Once a puzzle's loaded, will be a list of drawnBlocks
        self.boardWidth = 100
        self.boardHeight = 100
        self.blockWidth = 30
        self.blockHeight = 30

        self.rosterBlockWidth = 0
        self.rosterBlockHeight = 0
        self.rosterStartX = 0

        self.moveList = []
        self.atMove = 0

    def run(self):
        self.after(DELAY,self.onTimer)

    def loadPuzzle(self, puzzle):
        # Accept a puzzle and load it into the GUI

        # First clear memory
        self.pieces = []
        self.canvas.delete("all")
        self.moveList = []
        self.atMove = 0

        #Set up the board and piece roster
        squareSize = min(maxBoardWidth/puzzle.cols, maxBoardHeight/puzzle.rows)
        self.blockWidth = squareSize
        self.blockHeight = squareSize
        self.boardWidth = self.blockWidth*puzzle.cols
        self.boardHeight = self.blockHeight*puzzle.rows

        self.rosterStartX = boardStartX + self.boardWidth + extRosterPadding

        rosterX = self.rosterStartX
        rosterY = boardStartY + intRosterPadding
        maxHeight = 0

        #Start creating pieces, filling roster as we go
        for piece in puzzle.universe:
            label = piece.getLabel()
            if rosterX + intRosterPadding + piece.cols*self.blockWidth + intRosterPadding - self.rosterStartX <= rosterWidth:
                self.pieces.append(drawnBlock(self.canvas,piece,rosterX+intRosterPadding,rosterY,label=label, colour = colourDict[label], boxSize = self.blockWidth))
                rosterX += intRosterPadding + piece.cols*self.blockWidth
                if piece.rows*self.blockHeight>maxHeight:
                    maxHeight = piece.rows*self.blockHeight
            else:
                rosterX = self.rosterStartX
                rosterY += maxHeight + intRosterPadding
                maxHeight = piece.rows*self.blockHeight
                self.pieces.append(drawnBlock(self.canvas,piece,rosterX+intRosterPadding,rosterY,label=label, colour = colourDict[label], boxSize = self.blockWidth))
                rosterX += intRosterPadding + piece.cols*self.blockWidth

        #Draw board and roster
        for i in range(1,puzzle.rows):

            tag=self.canvas.create_rectangle(boardStartX+i*self.blockWidth - 1, boardStartY,
                                             boardStartX+i*self.blockWidth + 1, boardStartY+self.boardHeight, fill="#333333",width=0)
            self.canvas.tag_lower(tag)
        for j in range(1,puzzle.cols):
            tag=self.canvas.create_rectangle(boardStartX, boardStartY + j*self.blockHeight - 1,
                                             boardStartX + self.boardWidth, boardStartY+j*self.blockHeight+1, fill="#333333",width=0)
            self.canvas.tag_lower(tag)
        tag=self.canvas.create_rectangle(boardStartX, boardStartY, boardStartX + self.boardWidth, boardStartY + self.boardHeight,fill="white",width=2)
        self.canvas.tag_lower(tag)

        tag = self.canvas.create_rectangle(boardStartX + self.boardWidth + extRosterPadding, boardStartY,
                                  boardStartX + self.boardWidth + extRosterPadding + rosterWidth, rosterY + maxHeight + intRosterPadding, fill="white")
        self.canvas.tag_lower(tag)



    def move(self, move):
        #Puts a piece into (i,j) or sends it home

        piece = self.getPiece(move.tag)
        if move.home:
            piece.setMove(piece.homeX,piece.homeY)
        else:
            x = boardStartX + move.i*self.blockWidth
            y = boardStartY + move.j*self.blockHeight
            piece.setMove(x,y)

    def getPiece(self, tag):
        foundPiece = -1
        for piece in self.pieces:
                if piece.label == tag:
                    foundPiece = piece
                    break
        if foundPiece == -1:
            print("Error: No piece for tag \'"+ str(tag) + "\' found")
        return piece

    def getMoveStatus(self):
        if self.atMove < len(self.moveList):
            currentMove = self.moveList[self.atMove]
            piece = self.getPiece(currentMove.tag)
            if piece.isMoving:
                return False
            else:
                return True

        else:
            return True

    def handleMoves(self):
        moveCompleted = self.getMoveStatus()
        if moveCompleted:
            if self.atMove < len(self.moveList) - 1:
                self.atMove += 1
                self.move(self.moveList[self.atMove])
            else:
                self.isPlaying = False

    def playPress(self):
        print("Play")
        self.isPlaying=True
        #Start the next move
        if self.atMove < len(self.moveList):
            self.move(self.moveList[self.atMove])

    def pausePress(self):
        print("Pause")
        self.isPlaying=False


    def stepBackPress(self):
        print("Back")

    def stepForwardPress(self):
        print("Forward")

    def loadBoardPress(self):
        print("Load Board")
        input = self.boardInputField.get()
        if input == "":
            self.boardInputField.delete(0,END)
            self.boardInputField.insert(0,"Must enter a board here")
        else:
            prePuzzle = eval(input)
            # Now read in
            rows = prePuzzle[0]
            cols = prePuzzle[1]
            pieceList = prePuzzle[2]
            realPieces = []
            for piece in pieceList:
                realPieces.append(pz.Block(np.array(piece)))
            universe = frozenset(realPieces)
            puzzle = pz.Puzzle(rows,cols,universe)
            self.loadPuzzle(puzzle)

    def loadMovesPress(self):
        print("Load Moves")
        input = self.moveInputField.get()
        if input == "":
            self.moveInputField.delete(0,END)
            self.moveInputField.insert(0,"Must enter a move list here")
        else:
            preMoves = eval(input)
            self.moveList = []
            self.atMove = 0
            for move in preMoves:
                #Expect form [tag, i, j] with i = j = -1 when home is desired
                if move[1]==-1:
                    self.moveList.append(Move(move[0],0,0,home=True))
                else:
                    self.moveList.append(Move(move[0],move[1],move[2]))





    def onTimer(self):
        if self.isPlaying:
            self.handleMoves()
        for piece in self.pieces:
            if piece.isMoving:
                piece.move()
        self.after(DELAY,self.onTimer)

class Move:

    def __init__(self,tag, i ,j ,home=False):
        self.tag = tag
        self.i = i
        self.j = j
        self.home = home

class drawnBlock:

    def __init__(self,canvas,block,x=0,y=0,colour="blue",label=0, boxSize = 50):
        self.block = block
        self.x = x
        self.y = y
        self.targetX = x
        self.targetY = y
        self.homeX = x # Always start at home
        self.homeY = y
        self.isMoving = False
        self.step = defaultStep
        self.canvas = canvas
        self.boxSize = boxSize

        self.label = label

        self.initSquares(colour)

    def initSquares(self,colour):

        self.squares = []
        # Note transposition of (x,y)
        for i in range(0,self.block.cols):
            for j in range(0,self.block.rows):
                if self.block.config[j,i] != 0:
                    newSquare = drawnSquare(-1,self.canvas, self.x+self.boxSize*i,self.y+self.boxSize*j,
                                            self.boxSize*i,self.boxSize*j)
                    newSquare.tag = self.canvas.create_rectangle(self.x+self.boxSize*i,self.y+self.boxSize*j,
                                                            self.x+self.boxSize*(i+1),self.y+self.boxSize*(j+1),fill=colour,width=1)
                    self.squares.append(newSquare)

    def setMove(self,x,y):
        self.targetX = x
        self.targetY = y
        self.isMoving = True
        self.raiseBlock()
        for square in self.squares:
            square.setMove(x,y)


    def move(self):
        self.isMoving = False
        for square in self.squares:
            square.move(self.step)
            if square.isMoving:
                self.isMoving = True

    def raiseBlock(self):
        for square in self.squares:
            self.canvas.tag_raise(square)

    def changeColour(self,colour):
        for square in self.squares:
            self.canvas.itemconfigure(square,fill=colour)


class drawnSquare:

    def __init__(self, tag,canvas,x,y,relX,relY):
        self.tag = tag
        self.canvas = canvas

        self.x = x
        self.y = y
        self.relX = relX
        self.relY = relY

        self.targetX = x
        self.targetY = y
        self.isMoving = False

    def setMove(self,x,y):
        self.targetX = x + self.relX
        self.targetY = y + self.relY
        self.isMoving = True

    def move(self, step):
        dx = self.targetX - self.x
        dy = self.targetY - self.y

        dist = (dx**2 + dy**2)**0.5

        if dist <= step:
            self.canvas.move(self.tag,self.targetX-self.x,self.targetY-self.y)
            self.x = self.targetX
            self.y = self.targetY
            self.isMoving = False


        else:
            angle = math.atan2(dy,dx)
            self.x += math.cos(angle)*step
            self.y += math.sin(angle)*step
            self.canvas.move(self.tag,math.cos(angle)*step,math.sin(angle)*step)


