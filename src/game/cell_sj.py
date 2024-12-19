class Cell:
    def __init__(self, x, y, has_mine=False):
        self.x = x
        self.y = y
        self.has_mine = has_mine
        self.revealed = False
        self.flagged = False
        self.neighbor_mines = 0
        self.probability = 0.5  # Default probability before Bayesian updates

    def set_probability(self, probability):
        """
        Updates the probability of the cell containing a mine.
        :param probability: float, value between 0 and 1.
        """
        self.probability = probability

    def __repr__(self, show_probabilities=False):
        """
        String representation of the cell.
        :param show_probabilities: bool, whether to display probability values.
        """
        if self.flagged:
            return "F"
        elif not self.revealed:
            return f"{self.probability:.2f}" if show_probabilities else "■"
        elif self.has_mine:
            return "*"
        else:
            return str(self.neighbor_mines)
