# Strategy:
#
# 0) Generate initial set of chromosomes
#
# Loop:
# 1) Get a training set of puzzles
# 2) Run each chromosome on the training set (via the "go to best adjacent config as determined by traits", TODO: lookahead?)
# 3) Score each chromosome on the number of steps it takes (need to relativize by the size of the board, chromosomes?)
# 4) Take the better subset to be parents
# 5) Crossover (select each trait from parents with some probability), mutate sometimes

# Notes:
# Start: [161.625, 161.75, 163.625, 175.875, 185.875, 200.0, 200.0, 200.0]
# (GEN 8): [98.125, 136.75, 149.75, 166.25, 168.625, 175.625, 200.0, 200.0]
# 98 - corresponds to Traits(fullness=0.84145781331306, visitedness=-0.638698988705099, edginess=0.4011897218987517),
#        but I ascribe success to luck from randomness for now

from puzzle import *

import numpy as np
import random

from collections import namedtuple

Traits = namedtuple("Traits", ["fullness", "visitedness", "edginess"])

GENERATIONS = 8
CHROMOSOMES = 8
TRAINING_SIZE = 8
GAME_CUTOFF = 200

# Adopt the genetic approach since we expect the trait space to be highly non-convex

class Chromosome:

	def __init__(self, traits):
		self.traits = traits
		self.score = 0
		self.visited = set()

	def grader(self, board):
		grade = 0
		# Trait 1: Fullness metric:
		grade += self.traits.fullness * np.count_nonzero(board.matrix)
		# Trait 2: Visitedness
		grade += self.traits.visitedness * 10*int(board in self.visited)
		# Trait 3: Edginess (number of edge positions left)
		grade += self.traits.edginess * (np.count_nonzero(board.matrix) - np.count_nonzero(board.matrix[1:-1, 1:-1]))
		# Fudge factor
		grade += random.uniform(-5, 5);
		return grade

	def play_puzzle(self, puzzle):

		board = Board(puzzle, frozenset())
		move_count = GAME_CUTOFF

		# Game loop (with some cutoff value)
		for i in range(GAME_CUTOFF):

			self.visited.add(board)

			# print board.matrix

			# Get legal adjacent board states
			possible_moves = list(board.get_child_boards()) + list(board.get_parent_boards())

			# If winning state, go there immediately
			for move in possible_moves:
				if move.is_complete():
					move_count = i + 1
					break
			# TODO: This is a bug when game_cutoff is reached by i... do something else?
			if move_count != GAME_CUTOFF:
				break

			# Grade each board as desired
			grades = [self.grader(move) for move in possible_moves]

			# Enter the best state
			board = possible_moves[np.argmax(grades)]

		# Return the move count
		return move_count

def get_puzzles(count):
	puzzles = [
		# Intermediate puzzle 1
		Puzzle(6, 5, frozenset([
			Block([[0, 1, 0, 0], [1, 1, 0, 0], [1, 1, 1, 1]]),
			Block([[2, 2, 2, 2], [0, 0, 2, 2], [0, 0, 0, 2]]),
			Block([[3], [3]]),
			Block([[4], [4]]),
			Block([[5, 5, 0], [0, 5, 5], [0, 5, 5]]),
			Block([[6, 0, 0], [6, 6, 6], [6, 0, 0], [6, 0, 0]])
		])),
		# Intermediate puzzle 2
		Puzzle(3, 10, frozenset([
			Block([[1, 1, 1], [1, 1, 1], [1, 0, 0]]),
			Block([[2, 0, 2], [2, 2, 2]]),
			Block([[3, 3, 3, 3, 3], [0, 0, 0, 3, 0]]),
			Block([[4, 4, 4]]),
			Block([[5, 5, 0, 0], [5, 5, 5, 5]]),
			Block([[6, 6, 6]])
		])),
		# Intermediate puzzle 3
		Puzzle(10, 3, frozenset([
			Block([[1, 1], [1, 1], [0, 1]]),
			Block([[2, 0, 0], [2, 2, 0], [2, 2, 2]]),
			Block([[3], [3]]),
			Block([[4, 0, 0], [4, 0, 0], [4, 4, 0], [4, 4, 4]]),
			Block([[5, 5], [5, 5], [5, 0]]),
			Block([[0, 6], [0, 6], [6, 6], [6, 0]])
		])),
		# Intermediate puzzle 4
		Puzzle(10, 3, frozenset([
			Block([[1, 0], [1, 0], [1, 0], [1, 1], [1, 0]]),
			Block([[2, 2], [2, 0]]),
			Block([[0, 3], [3, 3], [0, 3], [0, 3]]),
			Block([[4, 4], [4, 4], [4, 4]]),
			Block([[5], [5], [5]]),
			Block([[6, 0, 6], [6, 0, 6], [6, 6, 6]])
		])),
		# DOUBLED CHECKED PAST HERE
		# Intermediate puzzle 5
		Puzzle(11, 3, frozenset([
			Block([[1, 0, 0], [1, 1, 1], [1, 1, 1]]),
			Block([[0, 0, 2], [0, 0, 2], [2, 2, 2], [0, 0, 2]]),
			Block([[3, 3, 0], [0, 3, 3]]),
			Block([[0, 4], [4, 4], [0, 4], [4, 4]]),
			Block([[5, 0], [5, 5], [5, 5]]),
			Block([[6, 6], [6, 0], [6, 6]])
		])),
		# Intermediate puzzle 6
		Puzzle(11, 3, frozenset([
			Block([[1, 1], [1, 0], [1, 0]]),
			Block([[2, 0], [2, 0], [2, 2], [2, 0]]),
			Block([[3, 0, 0], [3, 3, 3]]),
			Block([[0, 0, 4], [4, 4, 4], [0, 4, 4], [0, 4, 0]]),
			Block([[0, 5], [0, 5], [5, 5], [5, 5]]),
			Block([[0, 6], [6, 6], [6, 6]]),
			Block([[7, 7]])
		])),
		# Intermediate puzzle 7
		Puzzle(3, 9, frozenset([
			Block([[1, 1], [1, 0], [1, 1]]),
			Block([[2, 2], [0, 2], [0, 2]]),
			Block([[3, 3]]),
			Block([[4, 4], [4, 4], [0, 4]]),
			Block([[0, 5, 0], [5, 5, 0], [0, 5, 5]]),
			Block([[6, 6, 6], [6, 0, 0]]),
			Block([[7, 7]])
		])),
		# Intermediate puzzle 8
		Puzzle(12, 3, frozenset([
			Block([[1, 1, 0], [1, 0, 0], [1, 1, 1]]),
			Block([[2, 2, 0], [2, 2, 2], [0, 0, 2]]),
			Block([[3, 3], [3, 3], [3, 3]]),
			Block([[0, 4], [0, 4], [0, 4], [4, 4]]),
			Block([[5, 5, 5], [5, 0, 5], [0, 0, 5]]),
			Block([[0, 6], [6, 6], [6, 0]]),
			Block([[7, 7], [0, 7]])
		])),
	]

	return random.sample(puzzles, count)


def random_trait():
	return Traits(random.uniform(0, 1), random.uniform(-1, 0.5), random.uniform(-1, 1))


def main():

	# training_set = get_puzzles(TRAINING_SIZE)
	# chromosome = Chromosome(Traits(fullness=0.84145781331306, visitedness=-0.638698988705099, edginess=0.4011897218987517))
	# scores = [chromosome.play_puzzle(puzzle) for puzzle in training_set]
	# chromosome.score = np.mean(scores)
	# print chromosome.score
	# return

	# Initial chromosome configurations
	chromosomes = [Chromosome(random_trait()) for i in range(CHROMOSOMES)]

	for i in range(GENERATIONS):

		print "GENERATION {}".format(i)

		training_set = get_puzzles(TRAINING_SIZE)

		for chromosome in chromosomes:
			print "CHROMOSOME: {}".format(chromosome.traits)
			scores = [chromosome.play_puzzle(puzzle) for puzzle in training_set]
			chromosome.score = np.mean(scores)
			print chromosome.score

		# Sort chromosomes by scores
		by_movecount = sorted(chromosomes, key=lambda x: x.score)
		print [x.score for x in by_movecount]
		# Preserve top 50% to reproduce from
		winners = by_movecount[:CHROMOSOMES/2]

		chromosomes = []

		# Reproduce by pairing
		for j in range(CHROMOSOMES):

			parent_1 = winners[random.randrange(0, len(winners))];
			parent_2 = winners[random.randrange(0, len(winners))];

			trait_fields = []
			# For each trait:
			for k in xrange(len(chromosome.traits)):
				which_parent = random.randint(0, 1)

				# Wildcard
				if random.random() < 0.2:
					trait_fields.append(random_trait()[k])
				else:
					trait_fields.append(parent_1.traits[k] if which_parent else parent_2.traits[k])

			chromosomes.append(Chromosome(Traits(*trait_fields)))


if __name__ == "__main__":
	main()