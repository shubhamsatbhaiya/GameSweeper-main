class Cell:
    def __init__(self, x, y, has_mine=False):
        self.x = x
        self.y = y
        self.has_mine = has_mine
        self.revealed = False
        self.flagged = False
        self.neighbor_mines = 0

    def __repr__(self):
        if self.flagged:
            return "F"
        elif not self.revealed:
            return "■"
        elif self.has_mine:
            return "*"
        else:
            return str(self.neighbor_mines)
