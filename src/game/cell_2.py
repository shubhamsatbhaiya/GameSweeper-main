class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.has_mine = False
        self.neighbor_mines = 0
        self.revealed = False
        self.flagged = False

    def __str__(self):
        if self.revealed:
            if self.has_mine:
                return "*"
            elif self.neighbor_mines > 0:
                return str(self.neighbor_mines)
            else:
                return " "
        elif self.flagged:
            return "F"
        else:
            return "X"
