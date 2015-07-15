import puzzle as pz
import numpy as np
import random
import math

remove1x1 = True
changeByD8 = True
colourDict = {0:"#ffffff",1:"#ffcc99",2:"#cccccc",3:"#cc00ff",4:"#00ffff",5:"#99ff99",6:"#ffccff",7:"#cc99cc",8:"#cccc00",9:"#00ccff",10:"#99ff00",11:"#990000",12:"#009900",13:"#ccff00",14:"#99ffcc",15:"#999999",16:"#ffcc00",17:"#00cc99",18:"#ff00ff",19:"#ff00cc",20:"#990099",21:"#0000cc",22:"#ccffff",23:"#ff9999",24:"#0099ff",25:"#99ffff",26:"#ff0000",27:"#99ccff",28:"#ccff99",29:"#00cc00",30:"#cc99ff",31:"#9900ff",32:"#0099cc",33:"#ff99cc",34:"#ff0099",35:"#009999",36:"#cc9900",37:"#ffff00",38:"#ff9900",39:"#9999cc",40:"#ffcccc",41:"#9999ff",42:"#ffff99",43:"#ccffcc",44:"#ff99ff",45:"#000099",46:"#ffffcc",47:"#0000ff",48:"#99cccc",49:"#cc0000",50:"#999900",51:"#99cc99",52:"#cccc99",53:"#00ffcc",54:"#00cccc",55:"#99cc00",56:"#00ff99",57:"#cc00cc",58:"#cc0099",59:"#00ff00",60:"#ccccff",61:"#cc9999",62:"#9900cc",63:"#000000"}

class Point:

    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __eq__(self,other):
        if self.x == other.x and self.y == other.y:
            return True
        else:
            return False

def growPiecesGen(row,col,avgSize):
    """Generate a puzzle by growing pieces up to a size of avgSize"""
    tol = 100  # Number of attempts to make for each piece
    pieces = set([])
    board = np.zeros((row, col))  # Will fill this with +ve integers as the algorithm progresses
    nextSquare = Point(0,0)
    completed = False
    pieceNumber = 1 # Identifier for each piece, so boards are not just a matrix of ones
    while not completed:
        #We try to add a block starting in 'next' position. Always connected, unlikely to be not simply connected.
        #During construction represent a piece by using a list of coordinates for the squares present

        tempBlock = [nextSquare]
        board[nextSquare.x, nextSquare.y] = pieceNumber
        numSquares = 1

        #----------Specify the distribution of piece sizes here----------
        variation = 0.2
        proportion = 1 - variation + 2*variation*random.random()
        pieceSize = math.floor(proportion*avgSize)
        #pieceSize = avgSize
        #pieceSize = 2 + math.floor(random.random()*6)

        for i in range (0,pieceSize-1):
            viable = False
            attempts = 0
            while attempts < tol and (not viable):
                attempts +=1
                # First pick a piece to grow from
                piece = tempBlock[math.floor(random.random()*numSquares)]
                # Now a direction to grow in
                rand = math.floor(random.random()*4)
                if (rand == 0) and (piece.x+1<=row-1):
                    new = Point(piece.x + 1,piece.y)
                    if board[new.x,new.y] == 0:
                        viable = True
                        tempBlock.append(new)
                        numSquares += 1
                        board[new.x,new.y] = pieceNumber

                elif (rand == 1) and (piece.x - 1 >= 0):
                    new = Point(piece.x - 1,piece.y)
                    if board[new.x,new.y] == 0:
                        viable = True
                        tempBlock.append(new)
                        numSquares += 1
                        board[new.x,new.y] = pieceNumber

                elif (rand == 2) and (piece.y + 1 <= col-1):
                    new = Point(piece.x,piece.y + 1)
                    if board[new.x,new.y] == 0:
                        viable = True
                        tempBlock.append(new)
                        numSquares += 1
                        board[new.x,new.y] = pieceNumber

                elif (rand == 3) and (piece.y - 1 >= 0):
                    new = Point(piece.x, piece.y - 1)
                    if board[new.x,new.y] == 0:
                        viable = True
                        tempBlock.append(new)
                        numSquares += 1
                        board[new.x,new.y] = pieceNumber

        #Construct the block with its regular representation
        minX = float('inf')
        maxX = -float('inf')
        minY = float('inf')
        maxY = -float('inf')
        for square in tempBlock:
            minX = min(minX,square.x)
            maxX = max(maxX,square.x)
            minY = min(minY,square.y)
            maxY = max(maxY,square.y)

        config = np.zeros((maxX-minX+1,maxY-minY+1))

        for square in tempBlock:
            config[square.x-minX,square.y-minY] = pieceNumber

        pieces.add(pz.Block(config))

        # Prepare for the next pass
        pieceNumber += 1
        # Find the next square we need to fill, if any
        completed = True
        flag = 0
        for i in range(0,row):
            for j in range(0,col):
                if board[i,j] == 0:
                    completed = False
                    nextSquare = Point(i,j)
                    flag = 1
                    break

            if flag:
                break



    if remove1x1:
        board = removeLittleSquares(board, pieces)

    puzzle = pz.Puzzle(row,col,frozenset(pieces))
    if changeByD8:
        #Pick an element of D8 to roughly fix corner biases
        r = math.floor(random.random()*4)
        s = math.floor(random.random()*2)

        # This is just for drawing. Not necessary
        board = np.rot90(board, r)
        if s==1:
            board = np.fliplr(board)

        #Now manipulate actual puzzle
        puzzle.rotate(r)
        if s==1:
            puzzle.reflect()

    return puzzle

    #Return/print board instead for drawing
    #return board

def removeLittleSquares(board, pieces):
    rows = board.shape[0]
    cols = board.shape[1]
    hasChanged = False
    justStarted = True
    while justStarted or hasChanged: # Unfortunately, cannot iterate just over 'pieces' as the set changes in each loop
        justStarted = False
        hasChanged = False
        for piece in pieces:
            if piece.rows == 1 and piece.cols == 1:
                hasChanged = True
                # So we know we're working with a trivial square
                pieceNumber = piece.config[0,0]
                # Find in the board
                location = Point(-1,-1)
                for i in range(0,rows):
                    for j in range(0,cols):
                        if board[i, j] == pieceNumber:
                           location = Point(i,j)

                # Find a direction we can glue the square
                successfulGluing = False
                while not successfulGluing:
                   # Randomly pick a direction to glue
                    direction = math.floor(random.random()*4)
                    if direction == 0:
                        if location.x > 0:
                            # So can glue to the left. Get the label of that piece
                            newNumber = board[location.x-1,location.y]
                            successfulGluing=True
                    elif direction == 1:
                        if location.x <rows-1:
                            newNumber = board[location.x+1,location.y]
                            successfulGluing=True
                    elif direction == 2:
                        if location.y > 0:
                            newNumber = board[location.x,location.y-1]
                            successfulGluing=True
                    elif direction == 3:
                        if location.y <cols-1:
                            newNumber = board[location.x,location.y+1]
                            successfulGluing=True

                #Find the piece
                newPiece = 0
                for otherPiece in pieces:
                    if otherPiece.getLabel() == newNumber:
                        newPiece = otherPiece
                        break

                # Now find the (x,y) coordinate of the new piece
                firstSquare = -1
                for i in range(0,newPiece.rows):
                    if newPiece.config[i,0]!=0:
                        firstSquare = i
                        break
                origin = Point(-1,-1)
                flag = 0
                for j in range(0,cols):
                    for i in range(0,rows):
                        if board[i,j]==newNumber:
                            origin = Point(i-firstSquare,j)
                            flag = 1
                            break
                    if flag == 1:
                        break

                relativePosition = Point(location.x-origin.x,location.y-origin.y)

                r = newPiece.rows
                c = newPiece.cols
                if relativePosition.x >= r:
                    finalPiece = pz.Block(np.zeros((r+1,c)))
                    finalPiece.config[0:r,0:c] = newPiece.config[0:r,0:c]
                    finalPiece.config[relativePosition.x,relativePosition.y] = newNumber
                elif relativePosition.x < 0:
                    finalPiece = pz.Block(np.zeros((r+1,c)))
                    finalPiece.config[1:r+1,0:c] = newPiece.config[0:r,0:c]
                    finalPiece.config[relativePosition.x+1,relativePosition.y] = newNumber
                elif relativePosition.y >= c:
                    finalPiece = pz.Block(np.zeros((r,c+1)))
                    finalPiece.config[0:r,0:c] = newPiece.config[0:r,0:c]
                    finalPiece.config[relativePosition.x,relativePosition.y] = newNumber
                elif relativePosition.y < 0:
                    finalPiece = pz.Block(np.zeros((r,c+1)))
                    finalPiece.config[0:r,1:c+1] = newPiece.config[0:r,0:c]
                    finalPiece.config[relativePosition.x,relativePosition.y+1] = newNumber
                else:
                    finalPiece = newPiece
                    finalPiece.config[relativePosition.x,relativePosition.y] = newNumber

                #Correct the board
                board[location.x,location.y] = newNumber

                #Correct the piece list
                pieces.remove(piece)
                pieces.remove(newPiece)
                pieces.add(finalPiece)
                break

    #Should return pieces in the end
    return board
    #return pieces