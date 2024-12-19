class GameManager:
    def __init__(self, board):
        self.board = board

    def make_move(self, x, y, action="reveal"):
        """
        Perform a move on the board.
        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
            action (str): The action to perform, either "reveal" or "flag".
        """
        if self.board.game_over:
            print("Game is over! No further moves are allowed.")
            return

        if action == "reveal":
            self.board.reveal_cell(x, y)
            if self.board.game_over:
                print("BOOM! You hit a mine. Game over!")
                return
        elif action == "flag":
            self.board.flag_cell(x, y)
            print(f"Cell at ({x}, {y}) has been flagged.")

        # Display the current state of the board
        print(self.board)

        # Check for victory
        if self.board.is_victory():
            print("Congratulations! You've successfully cleared the board!")
            self.board.game_over = True

    def is_over(self):
        """
        Check if the game is over due to victory or hitting a mine.
        Returns:
            bool: True if the game is over, False otherwise.
        """
        return self.board.game_over

    def is_victory(self):
        """
        Check if the game is won.
        Returns:
            bool: True if the player has won, False otherwise.
        """
        return self.board.is_victory()

    def play_game(self):
        """
        Allow manual play through a console-based interface.
        """
        print("Welcome to Minesweeper!")
        print(self.board)

        while not self.is_over():
            try:
                action = input("Enter action (reveal/flag): ").strip().lower()
                x, y = map(int, input("Enter coordinates (x y): ").split())
                self.make_move(x, y, action)
            except ValueError:
                print("Invalid input. Please enter valid coordinates and action.")
