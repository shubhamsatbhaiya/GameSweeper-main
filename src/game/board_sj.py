import random
from .cell_sj import Cell

class Board:
    def __init__(self, width=9, height=9, mines=10):
        self.width = width
        self.height = height
        self.mines = mines
        self.grid = []
        self.probabilities = [[0.5] * width for _ in range(height)]  # Initialize probabilities
        self.game_over = False
        self._initialize_board()

    def _initialize_board(self):
        # Place mines
        cells = [Cell(x, y) for y in range(self.height) for x in range(self.width)]
        mine_positions = random.sample(cells, self.mines)
        for cell in mine_positions:
            cell.has_mine = True

        # Convert list back to 2D grid
        self.grid = [cells[i*self.width:(i+1)*self.width] for i in range(self.height)]

        # Calculate neighbor mine counts
        for y in range(self.height):
            for x in range(self.width):
                if not self.grid[y][x].has_mine:
                    self.grid[y][x].neighbor_mines = self.count_neighbor_mines(x, y)

    def count_neighbor_mines(self, x, y):
        neighbors = self.get_neighbors(x, y)
        return sum(1 for c in neighbors if c.has_mine)

    def get_neighbors(self, x, y):
        neighbors = []
        for nx in [x-1, x, x+1]:
            for ny in [y-1, y, y+1]:
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if not (nx == x and ny == y):
                        neighbors.append(self.grid[ny][nx])
        return neighbors

    def reveal_cell(self, x, y):
        cell = self.grid[y][x]
        if cell.revealed or cell.flagged:
            return

        cell.revealed = True
        if cell.has_mine:
            self.game_over = True
            return

        # If no neighboring mines, reveal neighbors recursively
        if cell.neighbor_mines == 0:
            for n in self.get_neighbors(x, y):
                if not n.revealed and not n.flagged:
                    self.reveal_cell(n.x, n.y)

    def flag_cell(self, x, y):
        cell = self.grid[y][x]
        if not cell.revealed:
            cell.flagged = not cell.flagged

    def is_victory(self):
        # Victory if all non-mine cells are revealed
        for y in range(self.height):
            for x in range(self.width):
                c = self.grid[y][x]
                if not c.has_mine and not c.revealed:
                    return False
        return True

    def update_probabilities(self, probabilities):
        """
        Updates the probability matrix for each cell.
        :param probabilities: 2D list of probabilities with the same dimensions as the board.
        """
        self.probabilities = probabilities

    def get_state(self):
        """
        Returns the current board state as a dictionary for AI processing.
        - 'revealed': List of revealed cells with their neighbor mine counts.
        - 'flagged': List of flagged cells.
        - 'unrevealed': List of unrevealed cells with their current probabilities.
        """
        revealed = [
            {'x': cell.x, 'y': cell.y, 'neighbor_mines': cell.neighbor_mines}
            for row in self.grid for cell in row if cell.revealed
        ]
        flagged = [
            {'x': cell.x, 'y': cell.y}
            for row in self.grid for cell in row if cell.flagged
        ]
        unrevealed = [
            {'x': cell.x, 'y': cell.y, 'probability': self.probabilities[cell.y][cell.x]}
            for row in self.grid for cell in row if not cell.revealed and not cell.flagged
        ]
        return {'revealed': revealed, 'flagged': flagged, 'unrevealed': unrevealed}

    def __str__(self):
        # Text-based representation for debugging
        rows = []
        for row in self.grid:
            rows.append(' '.join(str(c) for c in row))
        return '\n'.join(rows)
    
    def get_unrevealed_cells(self):
        result = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.grid[y][x].revealed and not self.grid[y][x].flagged:
                    result.append(self.grid[y][x])
        return result
