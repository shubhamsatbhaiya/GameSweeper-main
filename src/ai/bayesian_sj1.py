import itertools
from collections import defaultdict

class BayesianAnalyzer:
    def __init__(self):
        self.network = None

    def compute_probabilities(self, board):
        unrevealed_cells = board.get_unrevealed_cells()
        if not unrevealed_cells:
            return {}

            # Initialize probability matrix
        prob_matrix = self.initialize_probability_matrix(board)

        # Step 1: Gather constraints
        constraints = self.gather_constraints(board)

        # Step 2: Check for inconsistencies
        if not self.check_consistency(constraints, self.idx_to_cell, self.remaining_mines):
            print("Warning: Constraints are inconsistent. Falling back to uniform probabilities.")
            probabilities = self.handle_inconsistency(unrevealed_cells, self.remaining_mines)
            self.update_probability_matrix(prob_matrix, probabilities)
            self.display_probability_matrix(prob_matrix)
            return probabilities

        # Step 3: Compute probabilities iteratively
        probabilities = self.compute_valid_probabilities(constraints, self.idx_to_cell, self.remaining_mines)
        self.update_probability_matrix(prob_matrix, probabilities)

        # Display the updated matrix
        self.display_probability_matrix(self.prob_matrix)
        # Step 1: Initialize Bayesian Network
        self.network = self.build_bayesian_network(board, unrevealed_cells)

        # Step 2: Update Network with Clues (Evidence)
        self.set_clue_evidence(board)

        # Step 3: Perform Inference
        probabilities = self.infer_probabilities(unrevealed_cells)

        return probabilities

    def build_bayesian_network(self, board, unrevealed_cells):
        # Create a graph structure representing the dependencies
        network = defaultdict(list)
        for cell in unrevealed_cells:
            neighbors = board.get_neighbors(cell.x, cell.y)
            for neighbor in neighbors:
                if not neighbor.revealed and not neighbor.flagged:
                    network[(cell.x, cell.y)].append((neighbor.x, neighbor.y))
        return network

    def set_clue_evidence(self, board):
        # For each clue cell, update the network with observed values
        for y in range(board.height):
            for x in range(board.width):
                cell = board.grid[y][x]
                if cell.revealed and not cell.has_mine:
                    clue = cell.neighbor_mines
                    neighbors = [
                        (n.x, n.y) for n in board.get_neighbors(x, y) if not n.revealed and not n.flagged
                    ]
                    self.network[("clue", x, y)] = {"neighbors": neighbors, "clue": clue}

    def infer_probabilities(self, unrevealed_cells):
        # Placeholder for inference logic (e.g., belief propagation)
        probabilities = {}
        for cell in unrevealed_cells:
            # Simplified example: Assume uniform distribution
            probabilities[(cell.x, cell.y)] = 0.5
        return probabilities
    
    def initialize_probability_matrix(board):
        prob_matrix = [[0.0 for _ in range(board.width)] for _ in range(board.height)]
        return prob_matrix
    
    def update_probability_matrix(prob_matrix, probabilities):
        for (x, y), prob in probabilities.items():
            prob_matrix[y][x] = prob  # Update based on (x, y) coordinates

    def display_probability_matrix(prob_matrix):
        print("\nCurrent Probability Matrix:")
        for row in prob_matrix:
            print(" ".join(f"{prob:.2f}" for prob in row))


