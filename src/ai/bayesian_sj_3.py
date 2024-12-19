import itertools
from collections import defaultdict

class BayesianAnalyzer:
    def __init__(self):
        self.network = None  # Stores the Bayesian network structure
        self.evidence = {}   # Tracks evidence provided by revealed cells
        self.history = []    # Stores past board states and probabilities for reference
        self.probability_matrix = []  # Probability matrix to track probabilities for each cell

    def compute_probabilities(self, board):
        unrevealed_cells = board.get_unrevealed_cells()
        if not unrevealed_cells:
            return {}

        # Step 1: Initialize or Update Bayesian Network
        if self.network is None:
            self.network = self.build_bayesian_network(board, unrevealed_cells)
        
        # Step 2: Update Network with Clues (Evidence)
        self.update_clue_evidence(board)

        # Step 3: Perform Inference
        probabilities = self.infer_probabilities(unrevealed_cells, board)

        # Step 4: Save current state to history
        self.add_to_history(board, probabilities)

        # Update probability matrix
        self.update_probability_matrix(board, probabilities)

        return probabilities

    def build_bayesian_network(self, board, unrevealed_cells):
        """Create a Bayesian network structure with dependencies between cells."""
        network = defaultdict(list)
        for cell in unrevealed_cells:
            neighbors = board.get_neighbors(cell.x, cell.y)
            for neighbor in neighbors:
                if not neighbor.revealed and not neighbor.flagged:
                    network[(cell.x, cell.y)].append((neighbor.x, neighbor.y))
        return network

    def update_clue_evidence(self, board):
        """Update the Bayesian network with observed clues from revealed cells."""
        for y in range(board.height):
            for x in range(board.width):
                cell = board.grid[y][x]
                if cell.revealed and not cell.has_mine:
                    clue = cell.neighbor_mines
                    neighbors = [
                        (n.x, n.y) for n in board.get_neighbors(x, y) if not n.revealed and not n.flagged
                    ]
                    self.evidence[("clue", x, y)] = {"neighbors": neighbors, "clue": clue}

    def update_evidence(self, board, revealed_cell):
        """Incrementally update evidence based on a newly revealed cell."""
        x, y = revealed_cell.x, revealed_cell.y
        if revealed_cell.has_mine:
            self.evidence[(x, y)] = "mine"
        else:
            self.evidence[(x, y)] = revealed_cell.neighbor_mines

        # Adjust the Bayesian network based on new evidence
        self.update_clue_evidence(board)

    def infer_probabilities(self, unrevealed_cells, board):
        """Infer probabilities for each unrevealed cell using the Bayesian network."""
        probabilities = {}
        for cell in unrevealed_cells:
            if (cell.x, cell.y) in self.evidence:
                # Use existing evidence directly
                if self.evidence[(cell.x, cell.y)] == "mine":
                    probabilities[(cell.x, cell.y)] = 1.0
                else:
                    probabilities[(cell.x, cell.y)] = 0.0
            else:
                # Perform inference for cells without direct evidence
                probabilities[(cell.x, cell.y)] = self.compute_cell_probability(cell, board)
        return probabilities

    def compute_cell_probability(self, cell, board):
        """Calculate the probability based on the number of flagged cells and clues."""
        neighbors = board.get_neighbors(cell.x, cell.y)
        flagged_neighbors = sum(1 for neighbor in neighbors if neighbor.flagged)
        revealed_neighbors = sum(1 for neighbor in neighbors if neighbor.revealed and not neighbor.has_mine)

        # Adjust probabilities based on neighboring cells
        if flagged_neighbors > 0:
            return 0.7  # Adjust this based on the number of flagged neighbors
        elif revealed_neighbors > 0:
            return 0.2  # Adjust based on the number of revealed neighbors

        return 0.5  # Default probability

    def add_to_history(self, board, probabilities):
        """Store the board state and computed probabilities for reference."""
        board_state = self.serialize_board(board)
        self.history.append({"board_state": board_state, "probabilities": probabilities})

    def serialize_board(self, board):
        """Serialize the board state to store in history."""
        return [
            [(cell.revealed, cell.has_mine, cell.neighbor_mines, cell.flagged) for cell in row]
            for row in board.grid
        ]

    def update_probability_matrix(self, board, probabilities):
        """Update the probability matrix with the latest probabilities."""
        self.probability_matrix = [
            [0.0 for _ in range(board.width)] for _ in range(board.height)
        ]
        for y in range(board.height):
            for x in range(board.width):
                if (x, y) in probabilities:
                    self.probability_matrix[y][x] = probabilities[(x, y)]

    def print_probability_matrix(self):
        """Print the probability matrix in a readable format."""
        for row in self.probability_matrix:
            print(" | ".join([f"{prob:.2f}" for prob in row]))

# Usage:
# After each move, call `compute_probabilities` to update the probability matrix.
# To print the matrix, use:
# analyzer.print_probability_matrix()
