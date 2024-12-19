class GameManager:
    def __init__(self, board):
        self.board = board
        self.moves = []  # Track moves for analysis

    def make_move(self, x, y, action="reveal"):
        """
        Makes a move on the board.
        :param x: int, x-coordinate of the cell.
        :param y: int, y-coordinate of the cell.
        :param action: str, either "reveal" or "flag".
        """
        if self.board.game_over:
            return

        if action == "reveal":
            self.board.reveal_cell(x, y)
        elif action == "flag":
            self.board.flag_cell(x, y)

        # Log move
        self.moves.append({"x": x, "y": y, "action": action})

    def is_over(self):
        """
        Checks if the game is over (win or loss).
        :return: bool
        """
        return self.board.game_over or self.board.is_victory()

    def is_victory(self):
        """
        Checks if the game is a victory.
        :return: bool
        """
        return self.board.is_victory()

    def get_moves(self):
        """
        Retrieves the list of moves made in the game.
        :return: list of dicts
        """
        return self.moves

    def get_probabilities(self):
        """
        Retrieves the current probability matrix of the board.
        :return: 2D list of probabilities.
        """
        probabilities = []
        for row in self.board.grid:
            probabilities.append([cell.probability for cell in row])
        return probabilities

    def set_probabilities(self, probability_matrix):
        """
        Sets the probabilities on the board using a given matrix.
        :param probability_matrix: 2D list of probabilities.
        """
        for y, row in enumerate(self.board.grid):
            for x, cell in enumerate(row):
                cell.set_probability(probability_matrix[y][x])
