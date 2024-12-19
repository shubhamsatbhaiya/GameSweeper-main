import itertools

class BayesianAnalyzer:
    def __init__(self):
        pass

    def compute_probabilities(self, board):
        """
        Compute probabilities of each unrevealed cell being a mine based on the current board state.
        Args:
            board (Board): The Minesweeper board instance.
        Returns:
            dict: A mapping of (x, y) coordinates to probabilities of being a mine.
        """
        unrevealed_cells = board.get_unrevealed_cells()
        if not unrevealed_cells:
            return {}

        # Gather constraints
        constraints = []
        for y in range(board.height):
            for x in range(board.width):
                cell = board.grid[y][x]
                if cell.revealed and not cell.has_mine:
                    # This cell gives a clue
                    clue = cell.neighbor_mines
                    unrevealed_neighbors = [c for c in board.get_neighbors(x, y) if not c.revealed and not c.flagged]
                    if unrevealed_neighbors:
                        constraints.append((unrevealed_neighbors, clue))

        # If no constraints, use uniform probability
        if not constraints:
            return self.uniform_probabilities(board, unrevealed_cells)

        # Map cells to indices
        cell_to_idx = {c: i for i, c in enumerate(unrevealed_cells)}
        idx_to_cell = {i: c for i, c in enumerate(unrevealed_cells)}

        # Compute the number of remaining mines
        total_mines = board.mines
        flagged_cells = len([c for c in board.get_all_cells() if c.flagged])
        remaining_mines = total_mines - flagged_cells
        # flagged_mines = sum(1 for row in board.grid for c in row if c.flagged)
        # remaining_mines = total_mines - flagged_mines
        # Ensure remaining_mines is valid
        if remaining_mines < 0 or remaining_mines > len(unrevealed_cells):
            print(f"Invalid remaining_mines: {remaining_mines}, resetting to valid range.")
            remaining_mines = max(0, min(remaining_mines, len(unrevealed_cells)))


        # If too many unrevealed cells, fallback to uniform approximation
        if len(unrevealed_cells) > 16:
            return self.uniform_probabilities(board, unrevealed_cells)

        # Count valid configurations
        valid_config_count = 0
        mine_counts = [0] * len(unrevealed_cells)

        # Generate candidate configurations
        candidate_configurations = itertools.combinations(range(len(unrevealed_cells)), remaining_mines)

        for mines_set in candidate_configurations:
            mines_set = set(mines_set)
            # Check constraints for this configuration
            if self.check_constraints(constraints, idx_to_cell, mines_set):
                valid_config_count += 1
                for m in mines_set:
                    mine_counts[m] += 1

        # Compute probabilities
        if valid_config_count == 0:
            # No valid configuration found; fallback to uniform probabilities
            return self.uniform_probabilities(board, unrevealed_cells)

        probabilities = {
            (c.x, c.y): mine_counts[i] / valid_config_count for i, c in idx_to_cell.items()
        }

        return probabilities

    # def compute_probabilities(self,board):
    #     probabilities = {}
    #     unrevealed_cells = board.get_unrevealed_cells()
    #     flagged_cells = len([c for c in board.get_all_cells() if c.flagged])
    #     remaining_mines = board.total_mines - flagged_cells

    #     # Ensure remaining_mines is valid
    #     if remaining_mines < 0 or remaining_mines > len(unrevealed_cells):
    #         print(f"Invalid remaining_mines: {remaining_mines}, resetting to valid range.")
    #         remaining_mines = max(0, min(remaining_mines, len(unrevealed_cells)))

    #     # Generate candidate mine configurations
    #     candidate_configurations = itertools.combinations(range(len(unrevealed_cells)), remaining_mines)

    #     # Evaluate probabilities for each cell
    #     for cell_index in range(len(unrevealed_cells)):
    #         mine_count = 0
    #         total_configurations = 0

    #         for configuration in candidate_configurations:
    #             total_configurations += 1
    #             if cell_index in configuration:
    #                 mine_count += 1

    #         # Assign probabilities to cells
    #         probabilities[(unrevealed_cells[cell_index].x, unrevealed_cells[cell_index].y)] = (
    #             mine_count / total_configurations if total_configurations > 0 else 0.5
    #         )

    #     return probabilities


    def uniform_probabilities(self, board, unrevealed_cells):
        """
        Compute uniform probabilities for unrevealed cells.
        Args:
            board (Board): The Minesweeper board instance.
            unrevealed_cells (list): List of unrevealed cells.
        Returns:
            dict: Uniform probabilities for each unrevealed cell.
        """
        total_mines = board.mines
        flagged_mines = sum(1 for row in board.grid for c in row if c.flagged)
        remaining_mines = total_mines - flagged_mines
        remaining_cells = len(unrevealed_cells)
        base_prob = remaining_mines / remaining_cells if remaining_cells > 0 else 0.0
        return {(c.x, c.y): base_prob for c in unrevealed_cells}

    def check_constraints(self, constraints, idx_to_cell, mines_set):
        """
        Check if a given set of mine placements satisfies all constraints.
        Args:
            constraints (list): List of (neighbors, clue) constraints.
            idx_to_cell (dict): Mapping from indices to cells.
            mines_set (set): Indices of cells considered as mines in the current configuration.
        Returns:
            bool: True if all constraints are satisfied, False otherwise.
        """
        for (neighbors, clue) in constraints:
            count = 0
            for n in neighbors:
                for i, cell in idx_to_cell.items():
                    if n.x == cell.x and n.y == cell.y and i in mines_set:
                        count += 1
                        break
            if count != clue:
                return False
        return True
