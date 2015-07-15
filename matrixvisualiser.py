from tkinter import Tk, Frame, BOTH, Canvas

#To use, call matrixvisualiser.drawMatrix(matrix,colours). 'matrix' is the matrix to be shown, 'colours' is a
 #   dictionary between matrix entries and colours eg {0:"#ffffff, 1:"#000000"} colours all zeros as white and ones as black

boxWidth = 20
boxHeight = 20
outlineWidth=0
outlineColour="black"

class Drawer(Frame):
    """The object matrices will be drawn in. A matrix here is a list of lists, assumed to be rectangular and non-empty
        with integer entries. Numpy arrays also work."""
    def __init__(self, parent, matrix, colours):
        Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Matrix Visualiser")
        self.pack(fill=BOTH, expand=1)

    def draw(self,matrix, colours):
        canvas = Canvas(self, background="white")
        row = len(matrix)
        col = len(matrix[0])
        for i in range(0,row):
            for j in range(0,col):
                canvas.create_rectangle(i*boxWidth, j*boxHeight, (i+1)*boxWidth, (j+1)*boxHeight, fill=colours[matrix[i][j]],
                                        outline=outlineColour, width=outlineWidth)

        canvas.pack(fill=BOTH, expand=1)

def drawMatrix(matrix, colours):
    root = Tk()
    root.geometry(str(boxWidth*len(matrix))+"x"+str(boxHeight*len(matrix[0]))+"+100+100")
    drawer = Drawer(root,matrix,colours)
    drawer.draw(matrix,colours)
    root.mainloop()
