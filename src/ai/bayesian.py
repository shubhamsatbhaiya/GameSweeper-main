import itertools

class BayesianAnalyzer:
    def __init__(self):
        pass

    def compute_probabilities(self, board):
        unrevealed_cells = board.get_unrevealed_cells()
        if not unrevealed_cells:
            return {}

        # Gather constraints
        constraints = []
        revealed_clue_cells = []
        for y in range(board.height):
            for x in range(board.width):
                cell = board.grid[y][x]
                if cell.revealed and not cell.has_mine:
                    # This cell gives us a clue
                    clue = cell.neighbor_mines
                    unrevealed_neighbors = [c for c in board.get_neighbors(x, y) if not c.revealed and not c.flagged]
                    if unrevealed_neighbors:
                        constraints.append((unrevealed_neighbors, clue))
                        revealed_clue_cells.append(cell)

        # If no constraints (e.g., start of game), assume uniform probability
        if not constraints:
            total_mines = board.mines
            flagged_mines = sum(1 for row in board.grid for c in row if c.flagged)
            remaining_mines = total_mines - flagged_mines
            remaining_cells = len(unrevealed_cells)
            base_prob = remaining_mines / remaining_cells if remaining_cells > 0 else 0.0
            return {(c.x, c.y): base_prob for c in unrevealed_cells}

        # Build a mapping from cells to an index
        cell_to_idx = {(c.x, c.y): i for i, c in enumerate(unrevealed_cells)}
        idx_to_cell = {i: c for i, c in enumerate(unrevealed_cells)}

        # Solve constraints by brute forcing all combinations of mine assignments to unrevealed cells.
        # This can be very large, so for demonstration, we limit board size or just try a subset.
        # For full board, this might be infeasible --> for demonstration assume a smaller board or partial approach.

        # Maximum number of unrevealed cells to brute force reasonably:
        if len(unrevealed_cells) > 16:
            # Too large for brute force; fallback to uniform approximation:
            total_mines = board.mines
            flagged_mines = sum(1 for row in board.grid for c in row if c.flagged)
            remaining_mines = total_mines - flagged_mines
            remaining_cells = len(unrevealed_cells)
            base_prob = remaining_mines / remaining_cells if remaining_cells > 0 else 0.0
            return {(c.x, c.y): base_prob for c in unrevealed_cells}

        # Count valid configurations
        valid_config_count = 0
        mine_counts = [0]*len(unrevealed_cells)
        
        # Compute how many mines remain:
        total_mines = board.mines
        flagged_mines = sum(1 for row in board.grid for c in row if c.flagged)
        remaining_mines = total_mines - flagged_mines

        # Generate combinations of exactly `remaining_mines` mines out of `len(unrevealed_cells)` if possible
        # If remaining_mines > number of unrevealed_cells, something is off, but let's just proceed.
        if remaining_mines <= len(unrevealed_cells):
            candidate_configurations = itertools.combinations(range(len(unrevealed_cells)), remaining_mines)
        else:
            # If logic is off, just consider all subsets for safety
            candidate_configurations = itertools.chain.from_iterable(
                itertools.combinations(range(len(unrevealed_cells)), r)
                for r in range(len(unrevealed_cells)+1)
            )

        for mines_set in candidate_configurations:
            mines_set = set(mines_set)
            # Check all constraints
            if self.check_constraints(constraints, idx_to_cell, mines_set):
                valid_config_count += 1
                for m in mines_set:
                    mine_counts[m] += 1

        if valid_config_count == 0:
            # No valid configuration found; fallback to uniform
            # This might happen if the puzzle is inconsistent or early in the game.
            base_prob = remaining_mines / len(unrevealed_cells) if unrevealed_cells else 0
            return {(c.x, c.y): base_prob for c in unrevealed_cells}

        probabilities = {}
        for i, c in idx_to_cell.items():
            probabilities[(c.x, c.y)] = mine_counts[i] / valid_config_count

        return probabilities

    def check_constraints(self, constraints, idx_to_cell, mines_set):
        # For each constraint (unrevealed_neighbors, clue),
        # ensure exactly 'clue' of these neighbors are in the mines_set
        for (neighbors, clue) in constraints:
            count = 0
            for n in neighbors:
                for i, cell in idx_to_cell.items():
                    if cell.x == n.x and cell.y == n.y:
                        if i in mines_set:
                            count += 1
                        break
            if count != clue:
                return False
        return True