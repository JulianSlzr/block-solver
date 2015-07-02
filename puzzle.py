import numpy as np
import time


class Puzzle:
    """This represents one of the game's puzzles"""

    def __init__(self, rows, cols, universe):
        self.rows = rows
        self.cols = cols
        self.universe = universe
        self.visited = set()

    def rotate(self,k):
        # Rotate the entire puzzle by k*90 degrees clockwise
        tempUni = self.universe
        self.universe = set([])
        for piece in tempUni:
            self.uinverse.add(piece.rotate(piece,k))

    def reflect(self,k):
        # Reflect entire puzzle left to right
        tempUni = self.universe
        self.universe = set([])
        for piece in tempUni:
            self.universe.add(piece.reflect())
        if k == 1 or k == 3:
            temp = self.rows
            self.rows = self.cols
            self.cols = temp

    def solve(self):
        print("Solving puzzle via cached DFS...")
        start = time.clock()
        board = Board(self, frozenset())
        result = board.dfs()
        if result:
            print(result.matrix)
            print("Nodes visited: {}".format(len(self.visited)))
        else:
            print("No solution found")
        end = time.clock()
        print("Time: {} seconds\n".format(end - start))

class Block:
    """This represents an abstract block to be placed"""

    def __init__(self, config):
        # Sized-to-fit rectangle representing the block
        self.config = np.array(config)
        # The rectangle's dimensions
        self.rows = self.config.shape[0]
        self.cols = self.config.shape[1]
        
    def getLabel(self):
        for i in range(0,self.rows):
            if self.config[i,0] != 0:
                return self.config[i,0]

    def rotate(self,k):
        # Rotate the block by k*90 degrees clockwise
        self.config = np.rot90(self.config,k)
        self.rows = self.config.shape[0]
        self.cols = self.config.shape[1]

    def reflect(self):
        # Reflect the block left to right
        self.config = np.fliplr(self.config)



class Placement:
    """This represents a block placed in the context of a board"""

    def __init__(self, board, block, row, col):
        self.board = board
        self.block = block
        self.row = row
        self.col = col
        self.matrix = self.compute_matrix()
        self.matrix.flags.writeable = False # for hashing

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        # http://stackoverflow.com/a/16592241
        return hash(self.matrix.data)

    def compute_matrix(self):
        """A 'placed' matrix that can be summed with other placement matrices to give a 'board' matrix"""
        matrix = np.zeros((self.board.puzzle.rows, self.board.puzzle.cols))
        matrix[self.row:self.row+self.block.rows, self.col:self.col+self.block.cols] = self.block.config
        return matrix

class Board:
    """This represents a board with some pieces on it"""

    def __init__(self, puzzle, placements):
        self.placements = placements
        self.puzzle = puzzle
        self.decomp = [placement.matrix for placement in placements]
        self.matrix = sum(self.decomp) if self.decomp else np.zeros((self.puzzle.rows, self.puzzle.cols))
        self.remaining = self.puzzle.universe - {placement.block for placement in placements}

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        """A board state is uniquely determined by its decomposition set (set of the matrices that sum to the total board)"""
        return hash(self.placements)

    def check_legality(self, placement):
        return np.array_equal(np.maximum(self.matrix, placement.matrix), self.matrix + placement.matrix)

    def is_complete(self):
        return np.all(self.matrix != 0)

    def get_child_boards(self):
        # Enumerate legal moves
        # TODO: Rank by 'goodness'
        # TODO: Have a backtracking 'goodness' as well
        for block in self.remaining:
            for row in range(self.puzzle.rows - block.rows + 1):
                for col in range(self.puzzle.cols - block.cols + 1):
                    placement = Placement(self, block, row, col)
                    if self.check_legality(placement):
                        board = Board(self.puzzle, self.placements.union({placement}))
                        yield board